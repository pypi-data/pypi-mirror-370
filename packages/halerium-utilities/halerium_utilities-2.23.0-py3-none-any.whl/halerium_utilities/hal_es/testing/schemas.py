from pydantic.v1 import BaseModel, Field, root_validator, validator
from typing import List, Literal, Optional, Union

from halerium_utilities.board.schemas.path_element_update import PathElementUpdate


class ElementValue(PathElementUpdate):
    id: None = None


class ElementEvaluation(BaseModel):
    index: int
    expected_value: ElementValue = Field(description="Here you can specify which values of the element should be "
                                                     "considered in the evaluation. If left as None, everything "
                                                     "will be compared.", default=None)
    eval_prompt: str = Field(description="The prompt with which the values defined in `expected` are evaluated. "
                                         "If left as None the evaluation will be based on a programmatic "
                                         "comparison of the specified values.", default=None)

    @root_validator
    def check_at_least_one_value(cls, values):
        if values.get("expected_value") is None and values.get("eval_prompt") is None:
            raise ValueError('If neither `expected_value` nor `eval_prompt` are defined nothing can be evaluated.')
        return values


class InsertText(BaseModel):
    text: str
    field: str


class SendPrompt(BaseModel):
    pass


class AppendBotElement(BaseModel):
    pass


class UploadFile(BaseModel):
    file_path: str


class ExecuteActions(BaseModel):
    pass


ACTIONS = {
    "insert_text": InsertText,
    "send_prompt": SendPrompt,
    "append_bot_element": AppendBotElement,
    "upload_file": UploadFile,
    "execute_actions": ExecuteActions,
}


class ElementInteraction(BaseModel):
    index: int
    action_type: Literal[tuple(ACTIONS)]
    action: Union[(dict, *ACTIONS.values())] = Field(default_factory=dict)

    @validator('action', always=True)
    def check_action(cls, t, values):
        action_type = values.get("action_type", None)
        schema = ACTIONS[action_type]

        return schema.validate(t)


class UserInfo(BaseModel):
    username: str
    name: Optional[str] = None


class TestCase(BaseModel):
    board_path: Optional[str] = None
    hale_name: Optional[str] = None
    test_name: Optional[str] = "test"
    user_info: Optional[UserInfo] = None
    test_steps: List[ElementInteraction] = Field(default_factory=list)
    evaluations: List[ElementEvaluation] = Field(default_factory=list)

    @root_validator
    def check_at_least_one_value(cls, values):
        if values.get("board_path") is None and values.get("hale_name") is None:
            raise ValueError('At least one of board_path or hale_name must be provided.')
        return values
