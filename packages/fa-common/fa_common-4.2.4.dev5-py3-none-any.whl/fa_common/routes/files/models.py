# from typing import Optional
from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr

from fa_common import CamelModel, get_settings
from fa_common.models import File, TimeStampedModel


class FileDB(Document, TimeStampedModel):
    owner_id: Annotated[str, Indexed()]
    """Sub/ID of user who created the file."""
    project_id: Annotated[str | None, Indexed()] = None
    """Project this file belongs to."""
    tags: list[str] = []
    """Keywords or categories for the file."""
    file_ref: File
    """Reference to the file in the storage system."""
    file_users: list[EmailStr] = []
    """List of users who have access to the file."""
    sheets: list[str | int] | None = None
    """Sheets from an Excel file."""

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}file"


class UpdateFile(CamelModel):
    tags: list[str] | None = None
    """Keywords or categories for the file."""
    file_users: list[str] | None = None
    """List of users who have access to the file."""
    project_id: str | None = None

    add_tags: list[str] | None = None

    add_file_users: list[str] | None = None

    def get_update_dict(self):
        return self.model_dump(exclude_unset=True, exclude_none=True, exclude={"add_tags", "add_file_users"})
