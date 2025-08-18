from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.gql.common import GQLIssueOrderBy as GQLIssueOrderBy
from bosa_server_plugins.github.gql.label import GQLLabel as GQLLabel, label_fragment as label_fragment
from bosa_server_plugins.github.gql.project import CONTENTLESS_PROJECT_ITEM_FRAGMENT as CONTENTLESS_PROJECT_ITEM_FRAGMENT, PROJECT_FRAGMENT as PROJECT_FRAGMENT
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class GQLPullRequestState(str, Enum):
    """Pull request state model."""
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'

class GQLPullRequest(BaseModel):
    """Pull request model."""
    assignees: list[str] | None
    author: str | None
    body: str
    body_html: str
    body_text: str
    closed: bool
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    merged_at: datetime | None
    number: int
    title: str
    url: str
    state: str
    labels: list[GQLLabel] | None
    project_details: GQLProjectDetails | None
    @classmethod
    def from_dict(cls, data: dict) -> GQLPullRequest:
        """Create a GQLPullRequest from a dictionary.

        Args:
            data: The dictionary to create the pull request from.

        Returns:
            GQLPullRequest: The created pull request.
        """

class GQLIssueSimple(BaseModel):
    """Issue simple model."""
    id: str
    title: str
    parent_number: int | None
    parent_url: str | None
    project_details: GQLProjectDetails | None
    @classmethod
    def from_dict(cls, data: dict) -> GQLIssueSimple:
        """Create a GQLIssueSimple from a dictionary.

        Args:
            data: The dictionary to create the issue simple from.

        Returns:
            GQLIssueSimple: The created issue simple.
        """

class GQLPullRequestComplete(GQLPullRequest):
    """Pull request complete model."""
    closing_issues_references: list[GQLIssueSimple] | None
    @classmethod
    def from_dict(cls, data: dict) -> GQLPullRequestComplete:
        """Create a GQLPullRequestComplete from a dictionary.

        Args:
            data: The dictionary to create the pull request complete from.

        Returns:
            GQLPullRequestComplete: The created pull request complete.
        """

pull_request_fragment: Incomplete
pull_request_full_fragment: Incomplete

def gql_get_pull_request(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, pull_request_id: int) -> GQLPullRequestComplete:
    """Get a pull request by ID.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        pull_request_id: The ID of the pull request

    Returns:
        GQLPullRequestComplete: The created pull request complete.
    """
def gql_list_pull_requests(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, states: list[GQLPullRequestState] | None = None, labels: list[str] | None = None, head: str | None = None, base: str | None = None, per_page: int = 100, cursor: str | None = None, from_last: bool = False, order_by: GQLIssueOrderBy = ..., direction: str = 'DESC') -> tuple[list[GQLPullRequestComplete], GithubApiCursorMeta]:
    """Get a list of pull requests in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        states: List of states to filter by (OPEN, CLOSED, MERGED)
        labels: List of labels to filter by
        head: The head ref name to filter by
        base: The base ref name to filter by
        per_page: Number of pull requests per page
        cursor: Cursor for pagination
        from_last: Whether to paginate from the end
        order_by: Field to order by
        direction: Direction to order by

    Returns:
        tuple[list[GQLPullRequestComplete], GithubApiCursorMeta]: A tuple containing the list of pull requests
        and pagination metadata
    """
