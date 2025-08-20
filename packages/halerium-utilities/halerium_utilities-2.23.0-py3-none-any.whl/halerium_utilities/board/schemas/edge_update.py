from pydantic.v1 import validator
from typing import Literal, Union

from halerium_utilities.board.schemas.id_schema import EdgeId
from halerium_utilities.board.schemas.edge import Connections
from halerium_utilities.board.schemas.edge_types import EDGES


# factory for creating type specifics in which all fields are optional and all defaults are None
type_specific_models = {}
for _name, _model in EDGES.items():
    _new_model = type(_model.__name__+"Update", (_model,), {})
    for _field in _new_model.__fields__.values():
        _field.default = None
        _field.required = False
    type_specific_models[_name] = _new_model


class EdgeUpdate(EdgeId):
    type: Literal[tuple(EDGES)]
    connections: Connections = None
    type_specific: Union[(dict, *type_specific_models.values())] = None

    @validator('type_specific')
    def check_type_specific(cls, t, values):
        if t is None:
            return None
        type = values.get("type", tuple(EDGES)[0])
        schema = type_specific_models[type]
        return schema.validate(t)

