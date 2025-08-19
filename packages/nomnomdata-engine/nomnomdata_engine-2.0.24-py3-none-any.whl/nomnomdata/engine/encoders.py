from json import JSONEncoder
from pathlib import PosixPath

from .components import Connection, Parameter, ParameterGroup, ParameterType, SharedConfig
from .engine import Action, Engine


class ModelEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, PosixPath):
            return str(o)
        if isinstance(o, Connection):
            return self.serialize_connection(o)
        if isinstance(o, SharedConfig):
            return self.serialize_shared_config(o)
        if isinstance(o, Parameter):
            return self.serialize_parameter(o)
        if isinstance(o, ParameterGroup):
            return self.serialize_parameter_group(o)
        elif isinstance(o, ParameterType):
            return self.serialize_parameter_type(o)
        elif isinstance(o, Engine):
            return self.serialize_engine(o)
        elif isinstance(o, Action):
            return self.serialize_action(o)
        else:
            return super().default(o)

    def serialize_shared_config(self, shared_config: SharedConfig):
        result = {
            "uuid": shared_config.shared_config_type_uuid,
            "alias": shared_config.alias,
            "nnd_model_version": 2,
            "description": shared_config.description,
            "categories": [{"name": val} for val in shared_config.categories]
            if shared_config.categories
            else [{"name": "General"}],
            "type": "shared_config_type",
        }
        result["parameters"] = shared_config.parameter_groups
        return result

    def serialize_connection(self, connection: Connection):
        result = {
            "uuid": connection.connection_type_uuid,
            "alias": connection.alias,
            "nnd_model_version": 2,
            "description": connection.description,
            "categories": [{"name": val} for val in connection.categories]
            if connection.categories
            else [{"name": "General"}],
            "type": "connection",
        }
        result["direction"] = connection.direction
        result["parameters"] = connection.parameter_groups
        result["mask"] = connection.mask
        return result

    def serialize_engine(self, engine: Engine):
        parameter_categories = set()
        for action in engine.actions.values():
            for pg in action.parameter_groups.values():
                for parameter in [p for p in pg.parameters if p.categories]:
                    parameter_categories.update(
                        [cat["name"] for cat in parameter.categories]
                    )

        result = {
            "uuid": engine.uuid,
            "alias": engine.alias,
            "description": engine.description,
            "nnd_model_version": engine.nnd_model_version,
            "categories": engine.categories,
            "type": engine.model_type.__str__(),
            "parameter_categories": [{"name": c} for c in sorted(parameter_categories)],
        }
        if engine.icons:
            result["icons"] = engine.icons
        if engine.help:
            result["help"] = engine.help
        result["actions"] = engine.actions
        return result

    def serialize_action(self, action: Action):
        # add parameters to this dict last so
        # that it's more human readable
        result = {
            "display_name": action.display_name or action.name.capitalize(),
            "description": action.description,
        }
        if action.help:
            result["help"] = action.help
        result["parameters"] = [p for p in action.parameter_groups.values()]
        return result

    def serialize_parameter_group(self, pg: ParameterGroup):
        result = {
            "name": pg.name,
            "display_name": pg.display_name,
            "description": pg.description,
            "type": pg.type,
            "collapsed": pg.collapsed,
            "parameters": [p for p in pg.parameters],
        }
        if pg.shared_parameter_group_uuid:
            result["shared_parameter_group_uuid"] = pg.shared_parameter_group_uuid
        return result

    def serialize_parameter(self, p: Parameter):
        result = {
            "name": p.name,
            "display_name": p.display_name,
            "description": p.description,
            "required": p.required,
        }
        if p.help:
            result["help"] = p.help
        if p.default:
            result["default"] = p.type.dump(p.default)
        if p.many:
            result["many"] = p.many
        if p.categories:
            result["categories"] = p.categories
        if p.show_on:
            result["show_on"] = {
                "parameter_name": p.show_on.name,
                "parameter_value": p.show_on.value,
            }
        if p.direction:
            result["direction"] = p.direction
        if isinstance(p.type, Connection):
            result.update(self.serialize_connection_parameter(p.type))
        elif isinstance(p.type, SharedConfig):
            result.update(self.serialize_shared_config_parameter(p.type))
        else:
            result.update(self.serialize_parameter_type(p.type))
        return result

    def serialize_connection_parameter(self, c: Connection):
        return {"connection_type_uuid": c.connection_type_uuid, "type": c.type}

    def serialize_shared_config_parameter(self, c: SharedConfig):
        return {"shared_config_type_uuid": c.shared_config_type_uuid, "type": c.type}

    def serialize_parameter_type(self, pt: ParameterType):
        result = {k: v for k, v in pt.__dict__.items() if v is not None}
        result["type"] = pt.type
        if pt.shared_object_type_uuid:
            result["shared_object_type_uuid"] = pt.shared_object_type_uuid
        return result
