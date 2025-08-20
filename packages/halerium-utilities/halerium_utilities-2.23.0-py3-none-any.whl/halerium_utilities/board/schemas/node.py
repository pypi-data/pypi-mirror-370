from pydantic.v1 import BaseModel, validator, Field
from typing import Literal, Union

from halerium_utilities.board.schemas.id_schema import NodeId
from halerium_utilities.board.schemas.node_types import NODES


class Position(BaseModel):
    x: int = 0
    y: int = 0


class Size(BaseModel):
    width: int = Field(520, ge=0, description="The width of the node in pixels")
    height: int = Field(320, ge=0, description="The height of the node in pixels")


class Node(NodeId):
    type: Literal[tuple(NODES)]
    position: Position = Position.construct()
    size: Size = Size.construct()
    type_specific: Union[(dict, *NODES.values())] = Field(default_factory=dict)

    @validator('type_specific', always=True)
    def check_type_specific(cls, t, values):
        type = values.get("type", tuple(NODES)[0])
        schema = NODES[type]

        return schema.validate(t)
