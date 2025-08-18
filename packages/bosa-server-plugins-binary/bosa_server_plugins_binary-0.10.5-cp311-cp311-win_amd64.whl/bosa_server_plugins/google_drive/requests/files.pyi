from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel, InputFile as InputFile
from pydantic import BaseModel

class SearchFileRequest(BaseRequestModel):
    """Search file request model."""
    page_size: int | None
    page_token: str | None
    query: str | None
    order_by: str | None
    corpora: str | None
    drive_id: str | None
    include_items_from_all_drives: bool | None
    spaces: str | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class GetFileRequest(BaseRequestModel):
    """Get file request model."""
    id: str
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class CreateFileRequest(BaseRequestModel):
    """Create file request model from multipart/form-data."""
    file: InputFile
    resumeable: bool | None
    parent_folder_id: str | None
    description: str | None
    use_content_as_indexable_text: bool | None
    ignore_default_visibility: bool | None
    keep_revision_forever: bool | None
    ocr_language: str | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class CreateFolderRequest(BaseRequestModel):
    """Create folder request model."""
    name: str
    parent_folder_id: str | None
    description: str | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class UpdateFileRequest(BaseRequestModel):
    """Update file request model from multipart/form-data."""
    id: str
    file: InputFile | None
    resumable: bool | None
    name: str | None
    description: str | None
    add_parents: str | None
    remove_parents: str | None
    keep_revision_forever: bool | None
    ocr_language: str | None
    use_content_as_indexable_text: bool | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class UpdateFolderRequest(BaseRequestModel):
    """Update folder request model."""
    id: str
    name: str | None
    description: str | None
    add_parents: str | None
    remove_parents: str | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class DeleteFileRequest(BaseModel):
    """Delete file request model."""
    id: str
    supports_all_drives: bool | None

class CopyFileRequest(BaseRequestModel):
    """Copy file request model."""
    id: str
    name: str | None
    description: str | None
    parent_folder_id: str | None
    keep_revision_forever: bool | None
    ignore_default_visibility: bool | None
    ocr_language: str | None
    supports_all_drives: bool | None
    include_permissions_for_view: str | None
    include_labels: str | None

class GetFolderTotalFileByTypeSummaryRequest(BaseRequestModel):
    """Get total file by type summary request model."""
    folder_id: str
    callback_urls: list[str] | None
