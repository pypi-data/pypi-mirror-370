from typing import Optional
from pydantic.v1 import BaseModel, Field


class FindIssuesArgument(BaseModel):
    jql_str: Optional[str] = Field(description="The JQL string to search for issues in the Jira project. The jql_str should always start with `project = HAL`. You can look for issue or issues based on `key`, `issuetype`, `status`, `assignee`, `reporter`, `updated` and `created`. You cannot search for issues based on `summary` or `description`.")


async def find_jira_issues(data: FindIssuesArgument):
    """
    Find issues in the Jira project `HAL` based on the JQL string. This function is to give an overview of the project to the user.
    """

    from jira import JIRA
    import asyncio

    cfg = data.get("config_parameters", {})  # Will automatically be provided. Can be set in register_function
    user_email = cfg.get("user_email", "")
    api_token = cfg.get("api_token", "")

    if 'jql_str' in data:
        jql_str = data.get("jql_str")
        jira = await asyncio.to_thread(JIRA, server="https://erium.atlassian.net", basic_auth=(user_email, api_token))
        found_issues = await asyncio.to_thread(jira.search_issues, jql_str, maxResults=1000)
        issues = ""
        for issue in found_issues:
            issues += f"Key: {issue.key}\n"
            #issues += f"Type: {issue.fields.issuetype.name}\n"
            #issues += f"Status: {issue.fields.status.name}\n"
            #issues += f"Priority: {issue.fields.priority.name}\n"
            issues += f"assignee: {issue.fields.assignee}\n"
            ##issues += f"reporter: {issue.fields.reporter}\n"
            #issues += f"Date of creation: {issue.fields.created}\n"
            #issues += f"Last Time updated: {issue.fields.updated}\n"
            issues += f"Summary: {issue.fields.summary}\n"
            issues += "-----------------\n"
            issues += "\n"
        return issues
    return "Missing Parameters! Please Provide all Parameters"


class GetIssueArgument(BaseModel):
    key: Optional[str] = Field(description="Search through JIRA with this key.")


async def get_jira_issue(data: GetIssueArgument):
    """
    Get a specific JIRA issue based on the key given.
    """

    from jira import JIRA
    import asyncio

    cfg = data.get("config_parameters", {})  # Will automatically be provided. Can be set in register_function
    user_email = cfg.get("user_email", "")
    api_token = cfg.get("api_token", "")

    if 'key' in data:
        issue_key = data.get("key")
        jira = await asyncio.to_thread(JIRA, server="https://erium.atlassian.net", basic_auth=(user_email, api_token))
        issue = await asyncio.to_thread(jira.issue, issue_key)
        issue_details = {
            'key': issue.key,
            'summary': issue.fields.summary,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'reporter': issue.fields.reporter.displayName,
            'status': issue.fields.status.name,
            'priority': issue.fields.priority.name if issue.fields.priority else None,
            'issue_type': issue.fields.issuetype.name,
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'sprint': [sprint.name for sprint in issue.fields.customfield_10020] if issue.fields.customfield_10020 else None,
            'description': issue.fields.description,
            'linked_issues': [(link.type.name, link.outwardIssue.key) if hasattr(link, 'outwardIssue') else (link.type.name, link.inwardIssue.key) for link in issue.fields.issuelinks],
            'comments': [{'author': comment.author.displayName, 'body': comment.body} for comment in issue.fields.comment.comments]
        }
        return issue_details
    return "Missing Parameters! Please Provide all Parameters"


class UpdateIssueArgument(BaseModel):
    issue_key: Optional[str] = Field(description="The key of the issue to be updated")
    update_dict: Optional[str] = Field(description="update_dict (str): This is a dict in a str format, it includes the fields of the issue to be updated. example `summary: ..., description: ...`. The fields you can update are summary, description, assignee, comment and priority. For priority, the value of the field should be another dict that contains the key name and the value `Highest`, `High`, `Medium`, `Low`, `Lowest` for priority.")


async def update_jira_issue(data: UpdateIssueArgument):
    """
    Update the content of an issue in the Jira project. The content of an issue includes summary, description, assignee, comment and priority.
    """

    from jira import JIRA
    import json
    import asyncio

    cfg = data.get("config_parameters", {})  # Will automatically be provided. Can be set in register_function
    user_email = cfg.get("user_email", "")
    api_token = cfg.get("api_token", "")

    if 'issue_key' in data and 'update_dict' in data:
        issue_key = data.get("issue_key")
        update_dict = json.loads(data.get("update_dict"))
        jira = await asyncio.to_thread(JIRA, server="https://erium.atlassian.net", basic_auth=(user_email, api_token))
        issue = await asyncio.to_thread(jira.issue, issue_key)
        await asyncio.to_thread(issue.update, **update_dict)
        return "Issue has been updated."
    return "Missing Parameters! Please Provide all Parameters"

#
# class AddCommentArgument(BaseModel):
#     issue_key: Optional[str] = Field(description="The key of the issue to which the comment will be added.")
#     comment: Optional[str] = Field(description="The comment text to be added to the issue.")
#
#
# async def add_comment_to_issue(data: AddCommentArgument):
#     """
#     Add a comment to an issue in the Jira project.
#     """
#
#     from jira import JIRA
#     import asyncio
#
#     cfg = data.get("config_parameters", {})  # Will automatically be provided. Can be set in register_function
#     user_email = cfg.get("user_email", "")
#     api_token = cfg.get("api_token", "")
#
#     if 'issue_key' in data and 'comment' in data:
#         issue_key = data.get("issue_key")
#         comment = data.get("comment")
#
#         jira = await asyncio.to_thread(JIRA, server="https://erium.atlassian.net", basic_auth=(user_email, api_token))
#         issue = await asyncio.to_thread(jira.issue, issue_key)
#         await asyncio.to_thread(jira.add_comment, issue, comment)
#
#         return "Comment has been added to the issue."
#     return "Missing Parameters! Please Provide all Parameters"
#
