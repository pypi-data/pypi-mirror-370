from pydantic.v1 import Field

from halerium_utilities.board.schemas.id_schema import NodeId


class ProcessQueueUpdate(NodeId):
    continue_prompt: bool = Field(
        default=False,
        description="Whether to continue the prompt process",
        example=True)
    end: bool = Field(
        default=True,
        description="Whether to push to the end (true) or the beginning (false) of the queue. Default is true.",
        example=False)
