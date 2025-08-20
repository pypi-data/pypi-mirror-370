from pydantic.v1 import BaseModel, Field, validator
from typing import Dict, List, Literal, Union

from halerium_utilities.board.schemas import Node, Edge, PathElement
from halerium_utilities.board.schemas.edge_update import EdgeUpdate
from halerium_utilities.board.schemas.id_schema import NodeId, EdgeId, ElementId
from halerium_utilities.board.schemas.node_update import NodeUpdate
from halerium_utilities.board.schemas.path_element_update import PathElementUpdate
from halerium_utilities.collab.schemas.process_queue_update import ProcessQueueUpdate


class BoardAction(BaseModel):
    type: Literal["add_node", "update_node", "remove_node",
                  "add_edge", "update_edge", "remove_edge",
                  "add_task", "update_task", "remove_task", "insert_task",
                  "update_process_queue", "send_node_to_execute"] = Field(
        description=("The type of the specific action to perform. "
                     "Valid values are add_node, remove_node, update_node, add_edge, "
                     "remove_edge, update_edge, add_task, update_task, "
                     "remove_task, insert_task, update_process_queue, send_node_to_execute."),
        example="remove_node"
    )
    payload: Union[Dict, Node, NodeUpdate, NodeId, Edge, EdgeUpdate, EdgeId,
                   PathElement, PathElementUpdate, ElementId, ProcessQueueUpdate] = Field(
        description=("The corresponding payload for the action. For add_*, update_* "
                     "requires at least the id with additional optional properties, for "
                     "remove_* just the id is enough."),
        example={"id": "46b24f1c-ccaf-4b54-bf95-122cc37ec9e3"}
    )

    @validator("payload")
    def validate_payload(cls, t, values):
        type = values.get("type", "update_node")
        if type == "add_node":
            schema = Node
        elif type == "update_node":
            schema = NodeUpdate
        elif type == "remove_node":
            schema = NodeId
        elif type == "add_edge":
            schema = Edge
        elif type == "update_edge":
            schema = EdgeUpdate
        elif type == "remove_edge":
            schema = EdgeId
        elif type == "insert_task":
            schema = InsertTaskPayload
        elif type == "update_task":
            schema = UpdateTaskPayload
        elif type == "remove_task":
            schema = RemoveTaskPayload
        elif type == "update_process_queue":
            schema = ProcessQueueUpdate
        elif type == "send_node_to_execute":
            schema = NodeId
        else:
            raise NotImplemented

        return schema.validate(t)


class BoardActions(BaseModel):
    actions: List[BoardAction] = Field(description="The array of board actions to perform",
                                       min_items=1,
                                       example=[
                                           {
                                               "type": "remove_node",
                                               "payload": {
                                                   "id": "46b24f1c-ccaf-4b54-bf95-122cc37ec9e3"
                                               }
                                           }
                                       ])


class InsertTaskPayload(BaseModel):
    workflowId: str
    task: PathElement
    index: int


class RemoveTaskPayload(BaseModel):
    workflowId: str
    task: ElementId


class UpdateTaskPayload(BaseModel):
    workflowId: str
    task: PathElementUpdate
