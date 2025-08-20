from typing import Literal, Union

from pydantic.v1 import validator
from halerium_utilities.board.schemas.id_schema import ElementId
from halerium_utilities.board.schemas.path_element_types import ELEMENTS


# factory for creating type specifics in which all fields are optional and all defaults are None
type_specific_models = {}
for _name, _model in ELEMENTS.items():
    _new_model = type(_model.__name__+"Update", (_model,), {})
    for _field in _new_model.__fields__.values():
        _field.default = None
        _field.default_factory = None
        _field.required = False
    type_specific_models[_name] = _new_model


class PathElementUpdate(ElementId):
    type: Literal[tuple(ELEMENTS)]  # type: ignore
    type_specific: Union[(dict, *type_specific_models.values())] = None

    @validator('type_specific')
    def check_type_specific(cls, t, values):
        if t is None:
            return None
        type = values.get("type", tuple(ELEMENTS)[0])
        schema = type_specific_models[type]
        return schema.validate(t)
