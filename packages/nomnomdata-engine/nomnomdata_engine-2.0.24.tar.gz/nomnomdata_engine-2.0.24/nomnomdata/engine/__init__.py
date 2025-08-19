import dunamai as _dunamai

from . import components
from .components import Connection, Parameter, ParameterGroup, ParameterType, SharedConfig
from .engine import Engine
from .globals import current_engine, current_nominode

# alias for old style path
components.Engine = Engine

__version__ = _dunamai.get_version(
    "nomnomdata-engine", third_choice=_dunamai.Version.from_any_vcs
).serialize()

__author__ = "Nom Nom Data Inc"
