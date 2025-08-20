import abc
from typing import Dict, Iterable
from pydantic.v1 import BaseModel


class Document(BaseModel):
    content: str
    metadata: Dict[str, str] = dict()


class Chunker(abc.ABC):

    @abc.abstractmethod
    async def chunk(self) -> Iterable[Document]:
        raise NotImplementedError
        yield None

