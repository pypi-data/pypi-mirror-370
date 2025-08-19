import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from .globals import current_engine, current_nominode


class NominodeLogHandler(logging.Handler):
    # Send log lines in a separate thread, log lines are 'non critical' so if we get a timeout we don't care too much
    # Using a thread pool to limit the number of threads spawned

    def __init__(
        self,
        *args,
        sync=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.sync = sync
        self.threadPool = ThreadPoolExecutor(1)

    def shutdown(self):
        self.threadPool.shutdown()

    def emit(self, record):
        if self.sync:
            self._emit(record)
        else:
            self.threadPool.submit(self._emit, record)

    def mask(self, record):
        if current_engine and hasattr(current_engine, "secrets"):
            secrets = {
                param
                for secret in current_engine.secrets.values()
                for key, param in secret.items()
                if key != "alias"
            }
            for secret in secrets:
                str_secret = str(secret)
                if hasattr(record, "msg"):
                    record.msg = record.msg.replace(str_secret, "X" * len(str_secret))
                if hasattr(record, "message"):
                    record.message = record.message.replace(
                        str_secret, "X" * len(str_secret)
                    )
        return record

    def _emit(self, record):
        try:
            record = self.mask(record)
            to_send = record.__dict__.copy()
            to_send["execution_uuid"] = current_nominode.execution_uuid
            to_send["log_version"] = "0.1.0"
            if to_send["exc_info"]:
                to_send["exception_lines"] = traceback.format_exception(
                    *to_send["exc_info"]
                )
                del to_send["exc_info"]

            r_logger = logging.getLogger("requests")
            url_logger = logging.getLogger("urllib3")
            r_logger.propagate = False
            url_logger.propagate = False
            current_nominode.api.request(
                "put", f"execution/log/{current_nominode.execution_uuid}", data=to_send
            )
            r_logger.disabled = True
            url_logger.disabled = True
        except:
            print(f"Error logging {record} , {traceback.format_exc()}")
