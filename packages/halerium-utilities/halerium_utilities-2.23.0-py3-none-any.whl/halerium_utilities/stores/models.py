from pydantic import BaseModel
from typing import List, Literal, Optional, Union


class SearchParam(BaseModel):
    filter_type: Literal["exact_match", "wildcard"]
    case_insensitive: bool = False
    key: str
    value: str


class RangeParam(BaseModel):
    field: str
    gte: Union[str, float]
    lte: Union[str, float]


class FilterPayload(BaseModel):
    filter: Optional[List[Union[RangeParam, SearchParam]]] = None
