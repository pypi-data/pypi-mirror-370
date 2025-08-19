import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple

import click
import requests
import yaml

from nomnomdata.engine.errors import ParameterError, ValidationError
from nomnomdata.engine.util import dict_union

from .components import Connection, Parameter, ParameterGroup
from .globals import current_engine
from .nominode import NominodeClient, NominodeContext
from .testing import NominodeContextMock

__all__ = ["ModelType", "Model", "Action", "Engine", "ExecutionContextMock"]

python_type = type
logger = logging.getLogger(__name__)


@click.group(help="CLI interface to your engine")
def _cli():
    pass


@_cli.command(help="Run the engine, the expected entry point of an engine container")
def run():
    current_engine._run()


@_cli.command(help="Dump the engine model.yaml file, ready for the model-update command")
def dump_yaml():
    current_engine._dump_yaml()


class ModelType(str, Enum):
    ENGINE = "engine"
    CONNECTION = "connection"
    SHARED_OBJECT = "shared_object"

    def __str__(self):
        return self.value


class Model:
    nnd_model_version = 2
    model_type: ModelType


@dataclass
class Action:
    name: str
    parameter_groups: List[ParameterGroup]
    display_name: str
    as_kwargs: bool
    description: str
    help: Dict
    func: Callable

    @property
    def all_parameters(self):
        return {p.name: p for pg in self.parameter_groups.values() for p in pg.parameters}


class Engine(Model):
    """
    The engine object represents the model that will be presented to the Nominode UI,
    it also implements parameter validation.

    :example:

    .. code-block:: python

        from nomnomdata.engine import Engine

        engine = Engine(
            uuid="ENGINE-1",
            alias="engine-1",
            description="Some cool engine that does interesting things",
            categories=["cool", "powerful", "expensive"],
            help_md_path="s3://help-md-bucket/coolengine/help.md",
            icons={
                "1x": "s3://icon-bucket/coolengine/coolengine-icon-256.png",
                "2x": "./some-local-dir/coolengine-icon-512.png",
                "3x": "../other-dir/coolengine-icon-1024.png"
            }
        )
        general_settings = ParameterGroup(
                Parameter(Integer(), name="Maximum"),
                Parameter(Integer(), name="Minimum"),
                display_name="General Settings"
            )

        @engine.action(display_name="Do Something")
        @engine.parameter_group(general_settings)
        def do_something(parameters):
            print(parameters)

        if __name__ == "__main__":
            engine.main()

    """

    model_type = ModelType.ENGINE

    def __init__(
        self,
        uuid: str,
        alias: str,
        description: str = "",
        categories: List[str] = None,
        help_header_id: str = None,
        help_md_path: str = None,
        icons: Dict[str, str] = None,
        mock=False,
    ):
        if help_header_id and help_md_path:
            raise ValueError("Cannot use both help_header_id and help_md_path")

        self.uuid = uuid
        self.alias = alias
        self.description = description
        self.categories = (
            [{"name": val} for val in categories] if categories else [{"name": "General"}]
        )
        if help_header_id:
            self.help = {"header_id": help_header_id}
        elif help_md_path:
            self.help = {"file": help_md_path}
        else:
            self.help = None
        if icons:
            self.icons = {k: v for k, v in icons.items() if k in ["1x", "2x", "3x"]}
        else:
            self.icons = None
        self.actions = defaultdict(lambda: dict(parameters={}))
        self._current_action = None
        self.api = NominodeClient()
        self.mock = mock
        self._current_parameters = {}
        super().__init__()

        logger.debug(f"New Engine Registered '{uuid}'")

    def _run(self):
        nominode_ctx = NominodeContext.from_env()
        with nominode_ctx:
            try:
                logger.info("Fetching task from nominode")
                checkout = self.api.checkout_execution()
                self._current_parameters = checkout["parameters"]
                action_name = self._current_parameters.pop("action_name")
                params = self._current_parameters.copy()
                self.secrets = self.api.get_secrets()
                for secret_uuid in self.secrets:
                    for pname, p in params.items():
                        if (
                            isinstance(p, dict)
                            and p.get("connection_uuid") == secret_uuid
                        ):
                            params[pname] = self.secrets[secret_uuid]
                            params[pname]["connection_uuid"] = p.get("connection_uuid")
                logger.info(f"Action: {action_name}")
                action = self.actions[action_name]
                kwargs = self._finalize_kwargs(action.all_parameters, params)
                logger.debug(f"Calling Action {action.name}")
                self._current_action = action
                if action.as_kwargs:
                    return action.func(**kwargs)
                else:
                    return action.func(kwargs)
            finally:
                self._current_action = None

    def _finalize_kwargs(
        self, model_params: Dict[str, Parameter], params: Dict[str, Any]
    ):
        kwargs = {}
        # the sorted here while not
        # strictly needed does keep things deterministic for tests
        union_params = dict_union(model_params, params)
        for keyword, (param, val) in union_params.items():
            if keyword in ["alias", "connection_uuid", "shared_config_uuid"]:
                kwargs[keyword] = val
            elif not param:
                logger.warning(f"\tUnknown parameter '{keyword}', discarding")
            else:
                try:
                    logger.debug(f"\tDeserializing {keyword}:'{val}' with {param.type}")
                    kwargs[keyword] = param.load(val) if val is not None else val
                    logger.debug(
                        f"\tValidating {keyword}:'{kwargs[keyword]}' with {param.type}"
                    )
                    param.validate(kwargs[keyword])
                except ParameterError as e:
                    e.add_key(keyword)
                    logger.exception(f"\t{e}")
                    raise

        return kwargs

    def _dump_yaml(self):
        from .encoders import ModelEncoder

        click.echo("Encoding engine to YAML")
        json_dump = json.dumps(self, indent=4, cls=ModelEncoder)
        with open("model.yaml", "w") as f:
            f.write(yaml.dump(json.loads(json_dump), sort_keys=False, width=10000))
        click.echo("YAML written to ./model.yaml")

    def main(self):
        """
        Entry point for the engine, your program should call this for your engine to function.
        Blocking and will only return once specified command is complete.
        """
        current_engine._set(self)

        try:
            _cli.main()
        finally:
            current_engine._set(None)

    def action(
        self,
        display_name: str,
        help_header_id: str = None,
        help_md_path: str = None,
        description="",
        as_kwargs=False,
    ) -> Callable[[Any], Tuple[List[Tuple[str, requests.PreparedRequest]], Any]]:
        """
        Use as a decorator on a function to add an 'action' to your engine.

        :param display_name: Descriptive name that will be displayed in the UI
        :param help_header_id:
            The header ID to scroll to in any parent MD files that are declared,
            cannot be used if help_md_path is not None.
        :param help_md_path:
            A file path or URI to the location of an MD file to use as the help,
            cannot be used if help_header_id is not None.
        :param description: The long form description of what this engine done.
        :param as_kwargs:
            Will cause parameters to be passed to the wrapped function as kwargs instead of args,
            defaults to False
        :example:

        .. code-block:: python

            # note this example is not functional
            # as we do not declared any parameter_groups yet
            @engine.action(
                display_name="Do Something",
                help_header_id="Do Something",
                description="This action does something very helpful",
            )
            def my_cool_engine_action(parameters):
                print(parameters)
        """
        if help_header_id and help_md_path:
            raise ValueError("Cannot use both help_header_id and help_md_path")

        def action_dec(func):
            logger.debug(f"Action '{display_name}'")
            if not hasattr(func, "parameter_groups"):
                func.parameter_groups = {}
            for pg in func.parameter_groups.values():
                logger.debug(f"\tParameter Group {pg.name}")
                for p in pg.parameters:
                    logger.debug(f"\t\tParameter {p.name} {p.type}")
            if help_header_id:
                helpdict = {"header_id": help_header_id}
            elif help_md_path:
                helpdict = {"file": help_md_path}
            else:
                helpdict = None
            self.actions[func.__name__] = Action(
                parameter_groups=func.parameter_groups,
                name=func.__name__,
                display_name=display_name,
                description=description,
                as_kwargs=as_kwargs,
                func=func,
                help=helpdict,
            )

            @wraps(func)
            def call(*args, **kwargs):
                return self.__call__action__(func, *args, **kwargs)

            return call

        return action_dec

    def __call__action__(self, func, *args, **kwargs):
        kwargs["action_name"] = func.__name__
        mock = NominodeContextMock(task_parameters=kwargs)
        with mock:
            current_engine._set(self)
            try:
                result = self._run()
                return mock.calls, result
            finally:
                current_engine._set(None)
                self._current_action = None

    def parameter_group(
        self,
        parameter_group: ParameterGroup,
        name=None,
        display_name=None,
        description=None,
        collapsed=None,
    ) -> Callable:
        """Decorate your action with this have it accept groups of parameters

        :param parameter_group: Instantiated :class:`~nomnomdata.engine.components.ParameterGroup` class
        :param name: Override parameter group name
        :param display_name: Override display name
        :param description: Override discription
        :param collapsed: Override collapsed status


        :example:
        .. code-block:: python

            general_settings = ParameterGroup(
                Parameter(Integer(), name="Maximum"),
                Parameter(Integer(), name="Minimum"),
                display_name="General Settings"
            )

            @engine.action(display_name="Do Something")
            @engine.parameter_group(general_settings)
            def do_something(parameters):
                print(parameters)

        """

        def parameter_dec(func):
            params = getattr(func, "parameter_groups", {})
            if name:
                parameter_group.name = name
            if display_name:
                parameter_group.display_name = display_name
            if description:
                parameter_group.description = description
            if collapsed is not None:
                parameter_group.collapsed = collapsed
            params[parameter_group.name] = parameter_group
            func.parameter_groups = params
            return func

        return parameter_dec

    def update_parameter(self, key: str, value: any):
        """
        Update a specific task parameter on the nominode.

        :param key: The given key for the parameter that is being updated.
        :param value: The new value for the parameter, will be validated against the model.
        :raises ValueError: if given parameter key does not exist in the action model.
        :raises TypeError: when trying to update a connection. Connections cannot be updated.
        """
        if not self.mock:
            parameter = self._current_action.all_parameters.get(key)
            if not parameter:
                raise ValueError(
                    f"Parameter {key} does not exist in action model, cannot update"
                )
            if isinstance(parameter.type, Connection):
                raise TypeError(
                    f"{key} is a connection and cannot be updated using Engine.update_parameter"
                )
            try:
                parameter.validate(value)
            except ValidationError as e:
                logger.exception(
                    f"Validation error when trying to update {key} with {value}, {e}"
                )
            self._current_parameters[key] = parameter.type.dump(value)
        else:
            self._current_parameters[key] = value
        return self.api.update_task_parameters(parameters={key: value})

    def update_progress(
        self, message: str = None, progress: int = None
    ) -> Dict[str, str]:
        """
        Update nominode with current task progress

        :param message: Message for to attach to current task progress
        :param progress: Number representing the percentage complete of the task (0-100)
        :return: Response data
        """
        return self.api.update_progress(message=message, progress=progress)

    def update_result(self, result: Dict[str, any]) -> Dict[str, str]:
        """
        Update the task parameters on the nominode

        :param result: JSON data representing the result of this task. Currently only a json encoded Bokeh plot is supported.
        :return: Response data
        """
        return self.api.update_result(result=result)
