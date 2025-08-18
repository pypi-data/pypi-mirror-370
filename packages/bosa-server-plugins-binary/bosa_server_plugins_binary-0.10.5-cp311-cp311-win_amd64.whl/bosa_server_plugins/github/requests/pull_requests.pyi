from bosa_server_plugins.github.gql.issue import GQLIssueOrderBy as GQLIssueOrderBy
from bosa_server_plugins.github.gql.pull_request import GQLPullRequestState as GQLPullRequestState
from bosa_server_plugins.github.helper.common import RestDirection as RestDirection
from bosa_server_plugins.github.helper.pull_requests import PullRequestFields as PullRequestFields, RestPrOrderBy as RestPrOrderBy, RestPrState as RestPrState
from bosa_server_plugins.github.requests.common import DateRangeRequest as DateRangeRequest
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest

class SearchPullRequestsRequest(DateRangeRequest):
    """Search Pull Requests Request."""
    repositories: list[str] | None
    merged: bool | None
    draft: bool | None
    author: str | None
    labels: list[str] | None
    state: RestPrState | None
    sort: RestPrOrderBy | None
    direction: RestDirection | None
    fields: list[PullRequestFields] | None
    summarize: bool | None

class GetPullRequestRequest(BasicRepositoryRequest):
    """Request model for getting a single pull request."""
    pull_number: int

class GQLListPullRequestsRequest(BasicRepositoryRequest):
    """Request model for listing pull requests."""
    order_by: GQLIssueOrderBy | None
    direction: str | None
    per_page: int | None
    states: list[GQLPullRequestState] | None
    labels: list[str] | None
    head: str | None
    base: str | None
    cursor: str | None
    from_last: bool | None
