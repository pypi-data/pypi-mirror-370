import logging
from abc import ABCMeta, abstractmethod
from enum import StrEnum
from typing import Any, Dict, List

from nomnomdata.engine.errors import LoadError, MissingParameters, ValidationError
from nomnomdata.engine.util import dict_union

py_type = type

logger = logging.getLogger(__name__)


class ParameterType(metaclass=ABCMeta):
    """
    ParameterType is the base class for all parameter types.
    Should never be directly instantiated.
    """

    @property
    @abstractmethod
    def type(self):
        pass

    @property
    def shared_object_type_uuid(self):
        return None

    def validate(self, val):
        return True

    def dump(self, val):
        return val

    def load(self, val):
        return val


class Rule:
    def __init__(self, name: str = "", value: List[str] = [""]):
        self.name = name
        self.value = value


class Direction(StrEnum):
    target = "TARGET"
    source = "SOURCE"


class Parameter:
    """
    Parameter for use in a ParameterGroup, also contains options
    to control the look in the Nominode UI

    :param type:
        Set the type to allow validation of the parameter and
        so the UI understands how to render this parameter.
        Example valid parameter type :class:`~nomnomdata.engine.parameters.String`
    :param name:
        Parameter name, will be the key used in the final result passed to
        your function.
    :param display_name:
        The name of the parameter to be displayed to the user.
    :param help_header_id:
        Header ID in any MD file declared in upper scope that will be
        linked to this parameter.
    :param help_md_path:
        Full path to an MD file that will be linked
        to this parameter. Cannot be used with help_header_id.
    :param required:
        Setting this to true will require the user to set a value for this parameter,
        defaults to False
    :param description:
        The long form description the UI will diplay next
        to the parameter
    :param default:
        Default value of the parameter will be set as on task creation,
        valid values vary by the ParameterType you use, defaults to nothing
    """

    def __init__(
        self,
        type: ParameterType,
        name: str,
        display_name: str = "",
        help_header_id: str = None,
        help_md_path: str = None,
        required: bool = False,
        description: str = "",
        default: object = None,
        many: bool = False,
        categories: List[str] = None,
        show_on: Rule = None,
        direction: Direction = None
    ):
        if (
            not isinstance(type, ParameterType)
            and type is not None
            and issubclass(type, ParameterType)
        ):
            raise ValueError(f"{type} is not an instance, perhaps a forgotten ()?")
        elif not isinstance(type, ParameterType):
            raise ValueError(
                f"{type} is type {py_type(type)} when it must be an instance of a {ParameterType} subclass"
            )
        if name == "alias":
            raise ValueError(
                "alias is a protected parameter name, please use another name for your parameter"
            )
        self.type = type
        self.name = name
        self.direction = direction
        if help_header_id and help_md_path:
            raise ValueError("Cannot use both help_header_id and help_md_path")
        if help_header_id:
            self.help = {"header_id": help_header_id}
        elif help_md_path:
            self.help = {"file": help_md_path}
        else:
            self.help = None
        self.display_name = display_name or self.name.capitalize()
        self.required = required
        self.description = description
        if default:
            type.validate(default)
        self.default = default
        self.many = many
        self.categories = [{"name": val} for val in categories] if categories else None
        self.show_on = show_on

    def validate(self, value: Any):
        self._verify_required(value)
        if self.many and value is not None:
            for v in value:
                self._validate(v)
        else:
            self._validate(value)
        return True

    def _validate(self, value: Dict[str, Any]):
        if value is not None:
            self.type.validate(value)
        return True

    def load(self, value: Any):
        if self.many:
            return [self._load(v) for v in value]
        else:
            return self._load(value)

    def _load(self, value: Any):
        try:
            result = self.type.load(value)
            return result
        except Exception as e:
            raise LoadError(f"Exception while loading parameter value: {value}") from e

    def _verify_required(self, val: Any):
        if self.required and val is None:
            raise MissingParameters()

    def __str__(self):
        return f"{self.type.__class__.__name__} Parameter"

    def __repr__(self):
        return f"<{self.type.__class__.__name__} Parameter>"


class ParameterGroup:
    """ParameterGroup acts as a logical and visual grouping for parameters

    :param name:
        Unique key for this group, defaults to "general"
    :warning: you cannot use parameter groups with the same name on one action
    :param display_name:
        Display name to render in the UI, defaults to "General Parameters"
    :param description: UI description for this parameter group, defaults to ""
    :param collapsed:
        If the UI should collapse this parameter group when rendering,
        defaults to False
    :param shared_parameter_group_uuid:
        UUID of the shared parameter group defined for this parameter,
        can be safely left undefined in 95% of cases
    """

    def __init__(
        self,
        *args: Parameter,
        name: str = "general",
        display_name: str = "General Parameters",
        description: str = "",
        collapsed: bool = False,
        shared_parameter_group_uuid: str = "",
    ):

        self.parameters = args
        self.collapsed = collapsed
        self.shared_parameter_group_uuid = shared_parameter_group_uuid
        self.description = description
        self.name = name
        self.display_name = display_name
        self.type = "group"


class NestedType(ParameterType):
    def __init__(self, parameter_groups: List[ParameterGroup]):
        self.parameter_groups = parameter_groups

    def load(self, value: Dict[str, Any]):
        union_params = dict_union(self.all_parameters, value)
        kwargs = {}
        for keyword, (param, val) in union_params.items():
            if keyword in ["alias", "connection_uuid", "shared_config_uuid"]:
                kwargs[keyword] = val
            elif not param:
                logger.warning(f"\tUnknown parameter '{keyword}', discarding")
            else:
                if param.many:
                    kwargs[keyword] = [param.type.load(v) for v in val] if val else []
                else:
                    kwargs[keyword] = param.type.load(val) if val is not None else val
        return kwargs

    def validate(self, value: Dict[str, Any]):
        if value:
            union_params = dict_union(self.all_parameters, value)
            for keyword, (param, val) in union_params.items():
                if keyword not in ["alias", "connection_uuid", "shared_config_uuid"]:
                    try:
                        param.validate(val)
                    except ValidationError as e:
                        e.add_key(keyword)
                        raise

    @property
    def all_parameters(self):
        results = {}
        for pg in self.parameter_groups:
            if isinstance(pg, Parameter):
                results[pg.name] = pg
            else:
                for p in pg.parameters:
                    results[p.name] = p
        return results


class Connection(NestedType):
    """
    Connections are generally used for authentication credentials,
    parameters will be stored encrypted on the Nominode instead of in plain text and can require
    seperate permissions to be viewed or used.


    :param connection_type_uuid:
        Unique ID associated with this Connection
    :param parameter_groups:
        ParameterGroups in this connection
    :param description:
        Description of the connection to be rendered on the UI, defaults to ""
    :param alias:
        Short(er) alias for the connection
    :param categories:
        Categories this connection belongs to, for easier sorting in the UI.
    """

    type = "connection"

    def __init__(
        self,
        connection_type_uuid: str,
        parameter_groups: List[ParameterGroup],
        description: str = "",
        alias: str = "",
        categories: List[str] = None,
        mask: str = "",
        direction: Direction = Direction.target,
    ):

        self.connection_type_uuid = connection_type_uuid
        self.description = description
        self.alias = alias
        self.categories = categories
        self.mask = mask
        self.direction = direction
        super().__init__(parameter_groups=parameter_groups)


class SharedConfig(NestedType):
    """
    Shared Config are generally used for authentication credentials,
    parameters will be stored encrypted on the Nominode instead of in plain text and can require
    seperate permissions to be viewed or used.


    :param shared_config_type_uuid:
        Unique ID associated with this Shared Config
    :param parameter_groups:
        ParameterGroups in this Shared Config
    :param description:
        Description of the Shared Config to be rendered on the UI, defaults to ""
    :param alias:
        Short(er) alias for the Shared Config
    :param categories:
        Categories this Shared Config belongs to, for easier sorting in the UI.
    """

    type = "shared_config"

    def __init__(
        self,
        shared_config_type_uuid: str,
        parameter_groups: List[ParameterGroup],
        description: str = "",
        alias: str = "",
        categories: List[str] = None,
    ):

        self.shared_config_type_uuid = shared_config_type_uuid
        self.description = description
        self.alias = alias
        self.categories = categories
        self.parameter_groups = parameter_groups
