from pydantic.v1 import BaseModel, Field, validator

from halerium_utilities.board.schemas.utils import check_uuid4


class NodeId(BaseModel):
    id: str = Field(description="The unique id (uuid.v4) of the node",
                    example="46b24f1c-ccaf-4b54-bf95-122cc37ec9e3")

    @validator('id')
    def check_id(cls, s):
        return check_uuid4(s)


class EdgeId(BaseModel):
    id: str = Field(description="The unique id (uuid.v4) of the edge",
                    example="46b24f1c-ccaf-4b54-bf95-122cc37ec9e3")

    @validator('id')
    def check_id(cls, s):
        return check_uuid4(s)


class WorkflowId(BaseModel):
    id: str = Field(
        description="The unique id (uuid.v4) of the workflow",
        example="46b24f1c-ccaf-4b54-bf95-122cc37ec9e3",
    )

    @validator("id")
    def check_id(cls, s):
        return check_uuid4(s)


class ElementId(BaseModel):
    id: str = Field(
        description="The unique id (uuid.v4) of the path element",
        example="46b24f1c-ccaf-4b54-bf95-122cc37ec9e3",
    )

    @validator("id")
    def check_id(cls, s):
        return check_uuid4(s)
