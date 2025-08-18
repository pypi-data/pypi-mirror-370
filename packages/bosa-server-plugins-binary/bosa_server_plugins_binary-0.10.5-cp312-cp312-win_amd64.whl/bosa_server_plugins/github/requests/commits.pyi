from bosa_server_plugins.github.requests.common import DateRangeRequest as DateRangeRequest
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.github.tasks.get_all_pr_commits_task import CommitFields as CommitFields

class GetCommitsRequest(BasicRepositoryRequest, DateRangeRequest):
    """Request model for listing repository commits, based on the GitHub REST API."""
    sha: str | None
    path: str | None
    author: str | None
    committer: str | None
    per_page: int | None
    page: int | None

class SearchCommitsRequest(DateRangeRequest):
    """Request model for searching repository commits."""
    repositories: list[str] | None
    author: str | None
    fields: list[CommitFields] | None
    summarize: bool | None
    callback_urls: list[str] | None
