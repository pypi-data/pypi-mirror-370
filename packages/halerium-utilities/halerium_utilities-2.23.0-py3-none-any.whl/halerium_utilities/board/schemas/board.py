from pydantic.v1 import BaseModel, Field
from typing import List, Optional

from halerium_utilities.board.schemas.node import Node
from halerium_utilities.board.schemas.edge import Edge
from halerium_utilities.board.schemas.workflow import Workflow


class Board(BaseModel):
    version: str
    nodes: List[Node]
    edges: List[Edge]
    workflows: Optional[List[Workflow]] = Field(default_factory=list)
