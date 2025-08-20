from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class ParameterModel(BaseModel):
    type: Literal["string", "number", "boolean"]
    description: str = ""


class ParametersModel(BaseModel):
    properties: Optional[Dict[str, ParameterModel]] = Field(default_factory=dict)
    required: Optional[List[str]] = Field(default_factory=list)


class FunctionModel(BaseModel):
    function: str
    pretty_name: str = None
    group: Optional[str] = None
    description: str
    parameters: ParametersModel = Field(default_factory=ParametersModel)
    config_parameters: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode='before')
    def set_pretty_name(cls, values):
        if not values.get("pretty_name"):
            values['pretty_name'] = values.get('function')
        return values


class SetupCommand(BaseModel):
    setupCommands: List[str] = Field(default_factory=list)


# Used for validation for create and get capability group methods
class CapabilityGroupModel(BaseModel):
    name: str = ""
    displayName: str = ""
    runnerType: Literal['nano', 'small', 'standard', 'performance', 'highend', 'gpu'] = "nano"
    sharedRunner: bool = False
    setupCommand: SetupCommand = Field(default_factory=SetupCommand)
    sourceCode: Optional[str] = None
    functions: List[FunctionModel] = Field(default_factory=list)


# Used for validation for update capability group method (everything is optional)
class UpdateCapabilityGroupModel(BaseModel):
    name: Optional[str] = None
    displayName: Optional[str] = None
    runnerType: Optional[Literal['nano', 'small', 'standard', 'performance', 'highend', 'gpu']] = None
    sharedRunner: Optional[bool] = None
    setupCommand: Optional[SetupCommand] = None
    sourceCode: Optional[str] = None
    functions: Optional[List[FunctionModel]] = None
