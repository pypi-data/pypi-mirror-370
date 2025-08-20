from typing import List, Optional
from halerium_utilities.board.schemas.id_schema import WorkflowId
from halerium_utilities.board.schemas.path_element import PathElement


class Workflow(WorkflowId):
    name: str = ""
    chatText: str = ""
    linearTasks: List[PathElement] = []
    linkedNodeId: Optional[str] = None
