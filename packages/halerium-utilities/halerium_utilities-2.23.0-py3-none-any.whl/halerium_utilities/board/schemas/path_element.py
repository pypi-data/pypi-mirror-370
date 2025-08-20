from typing import Literal, Union

from pydantic.v1 import validator
from halerium_utilities.board.schemas.id_schema import ElementId
from halerium_utilities.board.schemas.path_element_types import ELEMENTS


class PathElement(ElementId):
    type: Literal[tuple(ELEMENTS)]  # type: ignore
    type_specific: Union[(dict, *ELEMENTS.values())] = {}

    @validator("type_specific", always=True)
    def check_type_specific(cls, t, values):
        type = values.get("type", tuple(ELEMENTS)[0])
        schema = ELEMENTS[type]

        return schema.validate(t)
