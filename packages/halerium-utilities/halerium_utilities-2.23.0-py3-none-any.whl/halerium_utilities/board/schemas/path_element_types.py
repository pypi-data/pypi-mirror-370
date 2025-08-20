from typing import Any, Dict, List, Literal, Optional
from pydantic.v1 import BaseModel, Field, validator

from .node_types import Attachment


# Define the ActionType as a Literal
ActionType = Literal["run", "run-tree"]


class TaskAction(BaseModel):
    nodeId: str
    type: ActionType


class NoteLinkTypeSpecific(BaseModel):
    title: str = ""
    message: str = ""
    attachments: Attachment = Field(default_factory=dict)
    linkedNodeId: Optional[str] = None


class BotLinkTypeSpecific(BaseModel):
    prompt_input: str = ""
    prompt_output: str = ""
    attachments: Attachment = Field(default_factory=dict)
    linkedNodeId: Optional[str] = None


class ActionChainTypeSpecific(BaseModel):
    actions: List[TaskAction] = Field(default_factory=list)
    actionLabel: Optional[str] = None


class FileContentTarget(BaseModel):
    targetId: Optional[str] = None  # the store id or card_id
    targetType: Literal["library", "card"]


class FilePathTarget(BaseModel):
    targetId: Optional[str] = None  # the store id or card_id
    targetType: Literal["memory", "card"]


class UploadTypeSpecific(BaseModel):
    actions: List[TaskAction] = Field(default_factory=list)
    uploadLabel: Optional[str] = None
    uploadDirectory: str = "."
    filePathTargets: List[FilePathTarget] = Field(default_factory=list)
    fileContentTargets: List[FileContentTarget] = Field(default_factory=list)
    chunkingArguments: List[Dict[str, Any]] = Field(default_factory=list)
    fileTypes: Optional[List[str]] = None

    @validator("chunkingArguments", pre=True, always=True)
    def replace_dict_with_empty_list(cls, v):
        if isinstance(v, dict):
            return []
        return v


ELEMENTS = {
    "note": NoteLinkTypeSpecific,
    "bot": BotLinkTypeSpecific,
    "action-chain": ActionChainTypeSpecific,
    "upload": UploadTypeSpecific,
}
