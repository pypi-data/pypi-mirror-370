from pydantic import BaseModel, Field, constr
from typing import Literal

AccessRightsType = Literal["workspace", "company", "public"]


class HalEDataModel(BaseModel):

    name: constr(strip_whitespace=True, min_length=1) = Field(
        ..., 
        title="HalE Name", 
        description="The name of the HalE"
    )
    access_rights: AccessRightsType = Field(
        ..., 
        title="Access Rights", 
        description="The access rights for this HalE. Must be one of: 'workspace', 'company', or 'public'"
    )
    template_board: constr(strip_whitespace=True, min_length=1) = Field(
        ..., 
        title="Board Template", 
        description="The path of the board template used for this HalE"
    )
    init_url: constr(strip_whitespace=True, min_length=1) = Field(
        ...,
        title="HalE friendly url",
        description="url under which a user can start a HalE session."
    )
