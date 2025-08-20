from pydantic.v1 import BaseModel, ConfigDict, Field, validator
from typing import Literal, Union

from halerium_utilities.board.schemas.id_schema import NodeId
from halerium_utilities.board.schemas.node_types import NODES


# factory for creating type specifics in which all fields are optional and all defaults are None
type_specific_models = {}
for _name, _model in NODES.items():
    _new_model = type(_model.__name__+"Update", (_model,), {})
    for _field in _new_model.__fields__.values():
        _field.default = None
        _field.default_factory = None
        _field.required = False
    type_specific_models[_name] = _new_model


class PositionUpdate(BaseModel):
    x: int = None
    y: int = None


class SizeUpdate(BaseModel):
    width: int = Field(None, ge=0, description="The width of the node in pixels")
    height: int = Field(None, ge=0, description="The height of the node in pixels")


class NodeUpdate(NodeId):
    type: Literal[tuple(NODES)]
    position: PositionUpdate = None
    size: SizeUpdate = None
    type_specific: Union[(dict, *type_specific_models.values())] = None

    @validator('type_specific')
    def check_type_specific(cls, t, values):
        if t is None:
            return None
        type = values.get("type", tuple(NODES)[0])
        schema = type_specific_models[type]
        return schema.validate(t)
