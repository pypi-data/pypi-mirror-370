from pydantic.v1 import BaseModel, validator
from typing import Literal, Union

from halerium_utilities.board.schemas.edge_types import EDGES
from halerium_utilities.board.schemas.id_schema import NodeId, EdgeId
from halerium_utilities.board.connection_rules.connectors import CONNECTORS


class Connection(NodeId):
    connector: Literal[tuple(CONNECTORS)]


class Connections(BaseModel):
    source: Connection
    target: Connection


class Edge(EdgeId):
    type: Literal[tuple(EDGES)]
    connections: Connections
    type_specific: Union[(dict, *EDGES.values())] = {}

    @validator('type_specific', always=True)
    def check_type_specific(cls, t, values):
        type = values.get("type", tuple(EDGES)[0])
        schema = EDGES[type]

        return schema.validate(t)
