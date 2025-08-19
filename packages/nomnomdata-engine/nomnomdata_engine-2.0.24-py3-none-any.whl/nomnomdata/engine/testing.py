import json
import logging
import re
from os import environ
from pprint import pformat

from httmock import HTTMock, urlmatch

from .globals import current_engine
from .nominode import NominodeContext


class EngineContextMock:
    def __init__(self, engine=None, task_parameters=None):
        from .engine import Engine

        self.engine = engine or Engine(uuid="TEST-ENGINE", alias="TEST", mock=True)
        task_parameters = task_parameters.copy() if task_parameters else {}
        self.engine._current_parameters = task_parameters
        self.nominode_ctx = NominodeContextMock(task_parameters=task_parameters)

    def __enter__(self):
        current_engine._set(self.engine)
        self.nominode_ctx.__enter__()
        return self

    def __exit__(self, *args):
        current_engine._set(None)
        self.nominode_ctx.__exit__(*args)


class ExecutionContextMock(EngineContextMock):
    def __enter__(self):
        super().__enter__()
        self.nominode_context = NominodeContext.from_env()
        self.nominode_context.__enter__()
        return self

    def __exit__(self, *args):
        self.nominode_context.__exit__(*args)
        super().__exit__(*args)


class NominodeContextMock(HTTMock):
    def __init__(self, task_parameters=None):
        super().__init__(self.api_match)
        self.logger = logging.getLogger("nomigen.nominode-mock")
        task_parameters = task_parameters or {}
        self.secrets = {
            k: {**secret, "alias": f"Connection Alias {i}"}
            if secret
            else {"alias": f"Connection {i}"}
            for i, (k, secret) in enumerate(task_parameters.pop("config", {}).items())
        }
        self.secrets = self.secrets if self.secrets else {"result": None}

        self.params = {**task_parameters, "alias": "Testing Task Alias"}
        self.calls = []
        self.environ = None

    def __enter__(self):
        self.environ = environ.copy()
        environ["execution_uuid"] = "TEST_UUID"
        environ["task_uuid"] = "TASK_UUID"
        environ["project_uuid"] = "TEST_PROJECT"
        environ["nomnom_api"] = "http://127.0.0.1:9090"
        environ["token"] = "token"
        environ["NND_LOG_LEVEL"] = logging.getLevelName(logging.getLogger().level)
        super().__enter__()
        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        environ.pop("execution_uuid")
        environ.pop("task_uuid")
        environ.pop("project_uuid")
        environ.pop("nomnom_api")
        environ.pop("token")

    @urlmatch(netloc=r"(.*\.)?127.0.0.1:9090$")
    def api_match(self, url, request):
        self.calls.append((url.path, json.loads(request.body)))
        match = re.match(r"/connection/(?P<uuid>.+)/update", url.path)
        if match:
            json_data = request.body
            loaded = json.loads(json_data)
            uuid = match.groupdict()["uuid"]
            self.params["config"][uuid] = json.loads(loaded["parameters"])
            self.logger.debug("Caught connections update. Test creds updated")
        elif url.path == "/execution/log/TEST_UUID":
            json_data = request.body
            loaded = json.loads(json_data)
        elif url.path == "/task/TASK_UUID/update":
            json_data = request.body
            loaded = json.loads(json_data)
            self.logger.debug("Caught task update {}".format(pformat(loaded)))
        elif url.path == "/execution/update/TEST_UUID":
            json_data = request.body
            loaded = json.loads(json_data)
            self.logger.debug(
                "Caught execution progress update {}".format(pformat(loaded))
            )
        elif url.path == "/execution/decode/TEST_UUID":
            return json.dumps(self.secrets)
        elif url.path == "/task/TASK_UUID/parameters":
            json_data = request.body
            loaded = json.loads(json_data)
            self.logger.debug("Caught task parameter update {}".format(pformat(loaded)))
            return json.dumps({"result": "success"})
        elif url.path == "/execution/checkout/TEST_UUID":
            return json.dumps({"parameters": self.params, "task_uuid": "TASK_UUID"})
        else:
            self.logger.info(
                f"Unknown api endpoint called {url.path}, \n Body {request.body}"
            )
        return '{"you_logged":"test"}'
