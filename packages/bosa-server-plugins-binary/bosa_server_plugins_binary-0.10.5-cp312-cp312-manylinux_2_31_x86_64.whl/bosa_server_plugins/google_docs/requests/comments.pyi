from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class BaseCommentsRequestModel(BaseRequestModel):
    """Base request model for Google Docs comments."""
    document_id: str

class ListCommentsRequest(BaseCommentsRequestModel):
    """List comment request model."""
    document_id: str
    page_size: int | None
    page_token: str | None
    include_deleted: bool | None
    start_modified_time: str | None

class SummarizeCommentsRequest(BaseCommentsRequestModel):
    """Summarize comments request model."""
