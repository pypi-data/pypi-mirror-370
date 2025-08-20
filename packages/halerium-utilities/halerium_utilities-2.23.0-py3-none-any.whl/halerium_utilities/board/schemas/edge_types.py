from pydantic.v1 import BaseModel


class SolidLineTypeSpecific(BaseModel):
    pass


class SolidArrowTypeSpecific(BaseModel):
    pass


class DashedLineTypeSpecific(BaseModel):
    pass


class PromptTypeSpecific(BaseModel):
    pass


EDGES = {
    "solid_line": SolidLineTypeSpecific,
    "solid_arrow": SolidArrowTypeSpecific,
    "dashed_line": DashedLineTypeSpecific,
    "prompt_line": PromptTypeSpecific
}