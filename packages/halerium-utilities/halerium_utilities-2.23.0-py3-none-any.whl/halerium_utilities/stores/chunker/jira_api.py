import datetime
from typing import Iterable

from jira import JIRA
from pydantic.v1 import BaseModel, Field

from halerium_utilities.stores.chunker import Chunker, Document


class JiraAPIArguments(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    jira: JIRA = Field(default=None, required=True, description="The jira API instance")

    filter_after: datetime.datetime = Field(default=None, required=False, description="Return only tickets after this date")
    filter_project: str = Field(default=None, required=False, description="The project name to filter for. Warning: No injection protection!")
    filter_custom: str = Field(default=None, required=False, description="Any other custom filter")

    add_comments: bool = Field(default=True, description="If comments of the ticket shall be added to the content of the ticket.")


class JiraAPIChunker(Chunker):

    def __init__(self, params: JiraAPIArguments):
        self.params = params

    def chunk(self) -> Iterable[Document]:
        filters = []
        if self.params.filter_project:
            filters.append(f"project = '{self.params.filter_project}'")
        if self.params.filter_after is not None:
            filters.append(f"created >= '{self.params.filter_after.strftime('%Y-%m-%d %H:%M')}'")
        if self.params.filter_custom:
            filters.append(f"({self.params.filter_custom})")

        jql_query = " && ".join(filters) + " order by created asc"

        query_size = 100
        i = 0

        while True:
            issues = self.params.jira.search_issues(jql_query, startAt=i * query_size, maxResults=query_size)
            i += 1

            for issue in issues:
                content = f"# JIRA Ticket\n\n## {issue.fields.summary}\n\n{issue.fields.description}\n\n### Properties\n"

                metadata = dict()
                for name, value in vars(issue.fields).items():
                    if name not in ["summary", "description"]:
                        if isinstance(value, str) and value.count("\n") == 0 and len(value) > 0:
                            content += f"- {name}: {value}\n"
                            metadata[name] = value

                if self.params.add_comments:
                    content += "\n\n### Comments\n\n"
                    for comment in issue.fields.comment.comments:
                        content += f"Author: {comment.author.displayName}\n"
                        content += f"Date: {comment.created}\n"
                        content += f"Message:\n```\n{comment.body}\n```\n\n"

                yield Document(content=content.strip(), metadata=metadata)

            if len(issues) == 0:
                break
