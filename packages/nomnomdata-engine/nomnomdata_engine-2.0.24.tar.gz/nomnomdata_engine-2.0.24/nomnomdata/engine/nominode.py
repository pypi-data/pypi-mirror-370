import json
import logging
from os import environ
from typing import Dict
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .globals import current_nominode
from .logging import NominodeLogHandler


class NominodeClient:
    """
    Interact with the Nominode API
    """

    def __init__(self):
        self.logger = logging.getLogger("nomigen.nominode_api")
        self._session = None

    @property
    def nominode_url(self):
        api_url = current_nominode.nomnom_api
        # ensure we always have a trailing / on the api url, otherwise we mess up urljoin
        return api_url if api_url.endswith("/") else api_url + "/"

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({"token": current_nominode.token})
            # max value for each backoff is 2 minutes, 20 retries gets us about 30 minutes of retrying
            retries = Retry(
                total=20, backoff_factor=1, status_forcelist=[502, 503, 504, 404]
            )
            self._session.mount(self.nominode_url, HTTPAdapter(max_retries=retries))
        return self._session

    def request(
        self,
        method: str,
        url_prefix: str = None,
        data: dict = None,
        params: Dict[str, str] = None,
        reg_data: str = None,
        headers: Dict[str, str] = None,
        path_override: str = None,
    ):
        """
        Authenticated request to nominode.

        Makes an authenticated request to the nominode and returns a JSON blob.

        Generally should not be used.

        :param method: HTTP Method to use (GET,POST,PUT,ect)
        :param url_prefix: Endpoint to hit e.g. execution/log
        :param data: Payload for request, must be JSON serializable
        :type data: optional
        :param params: URL Parameters, must be url encodable
        :type params: optional
        :param reg_data: Non JSON data to append to request. Cannot be used with data parameter
        :type reg_data: optional
        :param headers: Header dictionary
        :type headers: optional
        :param path_override: Override string for the start of the nominode url (usually /api/v1)
        :type path_override: optional
        :return: JSON Response data
        :rtype: dict
        """
        response_data = self._get_response_data(
            method=method,
            endpoint_url=url_prefix,
            data=reg_data,
            headers=headers,
            json_data=data,
            params=params,
            path_override=path_override,
        )
        return response_data

    def _get_response_data(
        self,
        method,
        endpoint_url,
        json_data=None,
        params=None,
        data=None,
        headers=None,
        path_override=None,
    ):
        headers = headers or {}
        if json_data:
            headers.update({"Content-Type": "application/json"})
        # endpoint urls should not start with a /
        endpoint_url = (
            endpoint_url if not endpoint_url.startswith("/") else endpoint_url.lstrip("/")
        )
        # this is to support overriding /api/1/ to /api/v2 if needed
        if path_override:
            split_url = list(urlsplit(self.nominode_url))
            split_url[2] = path_override
            base_url = urlunsplit(split_url)
            url = urljoin(base_url, endpoint_url)
        else:
            url = urljoin(self.nominode_url, endpoint_url)

        response = self.session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data if data else json.dumps(json_data, default=str),
        )
        try:
            response.raise_for_status()
            data = response.json()
            return data
        except Exception:
            self.logger.exception(
                f"Error during {method}:{url} - {response.status_code} - response payload:\n{response.text}"
            )
            raise

    def update_progress(
        self, message: str = None, progress: int = None
    ) -> Dict[str, str]:
        """
        Update nominode with current task progress

        :param message: Message for to attach to current task progress
        :param progress: Number representing the percentage complete of the task (0-100)
        :return: Response data
        """
        # Called to periodically update the completion status of a given execution
        # Always sets to - '05': 'Executing: Running in docker container'
        if message is None and progress is None:
            raise Exception(
                "Message or Progress needs to be provided when updating execution status..."
            )
        data = {"status_code": "05", "progress": progress, "message": message}
        return self.request(
            "put", "execution/update/%s" % current_nominode.execution_uuid, data=data
        )

    def update_connection(self, connection: str, connection_uuid: str) -> Dict[str, str]:
        """
        Update a connection on the nominode

        :param connection: Dictionary representing the updated connection object
        :param connection_uuid: UUID of the connection to be updated
        :return: Response data
        """
        data = {"alias": connection["alias"], "parameters": json.dumps(connection)}
        return self.request("post", "connection/%s/update" % connection_uuid, data=data)

    def checkout_execution(self) -> Dict:
        """
        Fetch the task parameters. Should only be called once.

        :return: task parameters dictionary
        """
        return self.request(
            "put", "execution/checkout/%s" % current_nominode.execution_uuid
        )

    def update_task_parameters(self, parameters: dict, task_uuid: str = None) -> None:
        """
        Patch the task parameters on the nominode.

        :param parameters:
            Dictionary representing the updated parameters. Partial updates are possible and will be merged in with existing parameters.
        :param task_uuid:
            UUID of the task to update, will default to the current task
        :type task_uuid: optional

        """
        task_uuid = task_uuid if task_uuid else current_nominode.task_uuid
        result = self.request(
            "put", "/task/{}/parameters".format(task_uuid), data=parameters
        )
        if "error" in result:
            raise Exception(result["error"])

    def update_result(self, result: Dict[str, any]) -> Dict[str, str]:
        """
        Update the task parameters on the nominode

        :param result: JSON data representing the result of this task. Currently only a json encoded Bokeh plot is supported.
        :return: Response data
        """
        assert "result_type" in result
        assert "result" in result
        result = self.request(
            "put",
            f"projects/{current_nominode.project_uuid}/task_execution/{current_nominode.execution_uuid}/result",
            data=result,
            path_override="api/v2/",
        )
        if "error" in result:
            raise Exception(result["error"])
        else:
            return result

    def get_secrets(self):
        """
        Fetch the encoded connections associated with this task
        Returns:
            dict: decoded connections
        """
        x = self.request("get", "execution/decode/%s" % current_nominode.execution_uuid)
        if "error" in x:
            raise Exception(x["error"])
        if x == {"result": None}:
            return {}
        else:
            return x

    def get_metadata_table(self, metadata_uuid: str, data_table_uuid: str):
        """
        Fetch a specific metadata table and data table from the nominode

        Parameters:
            metadata_uuid (string): UUID String of the metadata table.
            data_table_uuid (string): UUID String of the data table within the metadata.

        Returns:
            dict: success/response data
        """
        assert metadata_uuid, "metadata_uuid is required"
        assert data_table_uuid, "data_table_uuid is required"

        # Get the data_table details and column information
        url = "metadata/{metadata_uuid}/{data_table_uuid}"
        url = url.format(metadata_uuid=metadata_uuid, data_table_uuid=data_table_uuid)
        data_table = self.request("get", url)
        if "results" in data_table:
            # Grab first data table that matches.
            data_table = data_table["results"][0]
        else:
            raise Exception(
                "Error getting data table details for {}...".format(data_table_uuid)
            )

        return data_table


class NominodeLoggingContext:
    def __init__(self, sync=False):
        self.root_logger = logging.getLogger()
        self.nominode_handler = NominodeLogHandler(sync=sync)

    def mask_secrets(self, secrets):
        self.nominode_handler.mask_secrets(secrets)

    def __enter__(self):
        self.root_logger.setLevel(environ.get("NND_LOG_LEVEL", logging.INFO))
        self.root_logger.addHandler(self.nominode_handler)

    def __exit__(self, et, ev, tb):
        self.root_logger.removeHandler(self.nominode_handler)
        self.nominode_handler.shutdown()


class NominodeContext:
    def __init__(self, execution_uuid, task_uuid, project_uuid, nomnom_api, token):
        self.execution_uuid = execution_uuid
        self.task_uuid = task_uuid
        self.project_uuid = project_uuid
        self.nomnom_api = nomnom_api
        self.token = token
        self.api_mock = NoContext()
        self.logging_context = NominodeLoggingContext()
        self.api = NominodeClient()

    def mask_secrets(self, secrets):
        self.logging_context.mask_secrets(secrets)

    def __enter__(self):
        current_nominode._set(self)
        self.logging_context.__enter__()
        return self

    def __exit__(self, *args):
        self.logging_context.__exit__(*args)
        current_nominode._set(NoContext())

    @classmethod
    def from_env(cls):
        try:
            instance = cls(
                execution_uuid=environ["execution_uuid"],
                task_uuid=environ["task_uuid"],
                project_uuid=environ["project_uuid"],
                nomnom_api=environ["nomnom_api"],
                token=environ["token"],
            )
        except KeyError as e:
            raise RuntimeError(
                f"Could not find expected environment variable '{e.args[0]}'"
            )
        return instance


class NoContext:
    def __getattr__(self, name):
        if name in ["execution_uuid", "task_uuid", "project_uuid", "nomnom_api", "token"]:
            raise RuntimeError(
                "Not in nominode context, wrap with ExecutionContextMock or only execute via a nominode"
            )
        else:
            return super().__getattribute__(name)
