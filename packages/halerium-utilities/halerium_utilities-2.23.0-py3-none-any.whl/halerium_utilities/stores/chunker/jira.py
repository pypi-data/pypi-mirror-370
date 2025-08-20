from typing import Iterable
from pydantic.v1 import BaseModel, Field
from bs4 import BeautifulSoup

from halerium_utilities.stores.chunker import Chunker, Document


class JiraXMLArguments(BaseModel):
    filename: str = Field(default=None, required=True, description="Path of the file in Halerium", title="Filename")
    chunk_size: int = Field(default=10000, description="The chunking size", title="Chunk Size")
    chunk_overlap: int = Field(default=5000, description="The overlap of the chunks", title="Chunk Overlap")

    add_comments: bool = Field(default=True, description="If comments of the ticket shall be added to the content of the ticket.")


class JiraXMLChunker(Chunker):

    def __init__(self, params: JiraXMLArguments):
        self.params = params

    def chunk(self) -> Iterable[Document]:
        with open(self.params.filename, 'r') as f:
            file = f.read()

        soup = BeautifulSoup(file, 'xml')

        issues = soup.rss.channel.find_all('item')

        for item in issues:
            content = f"# JIRA Ticket\n\n## {item.title.get_text().strip()}\n\n### Properties\n"

            metadata = dict()
            for child in item.children:
                if child.name is not None and child.name != "title":
                    value = child.get_text().strip()
                    if value.count("\n") == 0 and len(value) > 0:
                        content += f"- {child.name}: {value}\n"
                        metadata[child.name] = value

            if self.params.add_comments:
                content += "\n\n### Comments\n\n"
                for comment in item.comments.find_all("comment"):
                    html_soup = BeautifulSoup(comment.get_text(), 'html.parser')
                    message = html_soup.get_text().strip()

                    content += f"Author: {comment.attrs.get('author', 'Unknown')}\n"
                    content += f"Date: {comment.attrs.get('created', 'Unknown')}\n"
                    content += f"Message:\n```\n{message}\n```\n\n"

            yield Document(content=content.strip(), metadata=metadata)


