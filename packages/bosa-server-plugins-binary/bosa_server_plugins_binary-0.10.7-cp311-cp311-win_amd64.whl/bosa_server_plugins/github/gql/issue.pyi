from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.gql.common import GQLDirection as GQLDirection, GQLIssueOrderBy as GQLIssueOrderBy, construct_page_query as construct_page_query
from bosa_server_plugins.github.gql.label import GQLLabel as GQLLabel
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from bosa_server_plugins.github.gql.pull_request import GQLPullRequest as GQLPullRequest, pull_request_fragment as pull_request_fragment
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from datetime import datetime
from pydantic import BaseModel

class GQLIssueFilter(BaseModel):
    """Issue filter model."""
    assignee: str | None
    created_by: str | None
    mentioned: str | None
    labels: list[str] | None
    milestone: str | None
    milestone_number: str | None
    since: str | None
    states: list[str] | None
    def to_dict(self) -> dict:
        """Convert the issue filter to a dictionary.

        Returns:
            dict: The dictionary representation of the issue filter.
        """

class GQLIssueOrder(BaseModel):
    """Issue order model."""
    field: GQLIssueOrderBy
    direction: str

class GQLMilestone(BaseModel):
    """Milestone model."""
    id: str
    number: int
    title: str
    description: str
    closed: bool
    state: str
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    due_on: datetime | None
    @classmethod
    def from_dict(cls, data: dict) -> GQLMilestone:
        """Create a GQLMilestone from a dictionary.

        Args:
            data: The dictionary to create the milestone from.

        Returns:
            GQLMilestone: The created milestone.
        """

class GQLIssue(BaseModel):
    """Issue model."""
    id: str
    assignees: list[str] | None
    number: int
    body: str
    closed: bool
    closed_at: datetime | None
    closed_by: list[GQLPullRequest] | None
    labels: list[GQLLabel] | None
    milestone: GQLMilestone | None
    project_details: GQLProjectDetails | None
    author: str | None
    created_at: datetime
    updated_at: datetime
    title: str
    parent_number: int | None
    parent_url: str | None
    @classmethod
    def from_dict(cls, data: dict) -> GQLIssue:
        """Create a GQLIssue from a dictionary.

        Args:
            data: The dictionary to create the issue from.

        Returns:
            GQLIssue: The created issue.
        """

issues_fragment: Incomplete

def gql_get_issue(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, issue_id: int) -> GQLIssue:
    """Get an issue by ID.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        issue_id: The ID of the issue

    Returns:
        GQLIssue: The created issue.
    """
def gql_list_issues(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, order_by: GQLIssueOrderBy = 'UPDATED_AT', direction: GQLDirection = 'DESC', per_page: int = 100, cursor: str = None, from_last: bool = False, filter_by: GQLIssueFilter = None) -> tuple[list[GQLIssue], GithubApiCursorMeta]:
    """Get a list of issues in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        order_by: The order by field
        direction: The direction of the order
        per_page: The number of issues per page
        cursor: The cursor to start from
        from_last: Whether to start from the last page
        filter_by: The filter to apply to the issues

    Returns:
        tuple[list[GQLIssue], int]: A tuple containing the list of issues and the total count
    """
