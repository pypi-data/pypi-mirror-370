# from typing import Optional
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal

from beanie import Document, Indexed, Link
from bson import ObjectId
from pydantic import EmailStr, field_validator

from fa_common import CamelModel, get_settings
from fa_common.models import File, SimplePerson, SimpleProject, TimeStampedModel
from fa_common.routes.project.models import ProjectDB
from fa_common.routes.user.models import UserDB


class MetadataType(str, Enum):
    """
    The types of metadata that can be loaded directly in table headers/cells
    """

    LAB_NAME = "Lab Name"
    UNITS = "Units"
    ANALYSIS_METHOD = "Analysis Method"
    LOWER_DETECTION_LIMIT = "Lower Detection Limit"
    UPPER_DETECTION_LIMIT = "Upper Detection Limit"
    STANDARD_DESCRIPTOR = "Standard Descriptor"


class TableLoadParams(CamelModel):
    sheet: str | int | None = None
    separator: str | None = None
    encoding: str | None = None
    transpose: bool = False
    metadata_rows: dict[MetadataType, int] | None = None
    data_start_row: int = 1
    data_end_row: int | None = None
    header_start_row: int = 0


class TableDB(Document, TimeStampedModel):
    name: str
    owner: Annotated[Link[UserDB], Indexed()]
    """Owner of the Table"""
    project: Annotated[Link[ProjectDB] | None, Indexed()] = None
    """Project this table belongs to."""
    columns: list[str]
    numeric_columns: list[str] = []
    metadata_rows: dict[MetadataType, list[Any]] | None = None
    metadata_extra: dict | None = None

    data_format: Literal["json", "csv", "file", "load_from_raw", "feather_file"] | None = None
    """How is the table data stored, JSON direct in the DB, CSV string, a seperate file, or loaded from the raw file."""
    data_file: File | None = None
    """File containing the data, if applicable. This is a link to the file in the database."""
    data_params: TableLoadParams | None = None
    table_users: list[EmailStr] = []
    """List of users who have access to the file."""

    parent_file_id: str | None = None
    """File ID of the file this table was created from, if applicable."""

    total_rows: int | None = 0

    tags: list[str] = []

    @field_validator("data_format")
    @classmethod
    def validate_data_format(cls, v: str):
        if v == "feather_file":
            return "file"
        return v

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}table"


class TableDBWithData(TableDB):
    data: dict | str | None = None


class TableItem(CamelModel):
    id: str
    name: str
    owner: SimplePerson | None
    project: SimpleProject | None

    columns: list[str]
    numeric_columns: list[str] = []
    metadata_extra: dict | None = None

    data: dict | str | None = None

    data_file: File | None = None
    data_params: TableLoadParams | None = None
    table_users: list[EmailStr] = []
    """List of users who have access to the table."""

    parent_file_id: str | None = None

    total_rows: int | None = 0

    tags: list[str] = []

    created: datetime | None = None
    """When the table was created."""

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator("project", "owner", mode="before")
    @classmethod
    def safe_link(cls, v: Any) -> Any:
        if isinstance(v, Link):
            return None
        return v


class CreateTable(CamelModel):
    file_id: str
    table_name: str
    tags: list[str] = []
    metadata_extra: dict | None = None
    project_id: str | None = None
    """Project this file belongs to, if None will inherit from the file."""
    table_users: list[EmailStr] | None = None
    """Users who have access to the table, if None will inherit from the file."""
    data_format: Literal["json", "csv", "file", "load_from_raw", "auto"] = "file"
    allow_single_column: bool = False
    return_data_format: Literal["json", "csv"] | None = None
    params: TableLoadParams


class UpdateTable(CamelModel):
    name: str | None = None
    tags: list[str] | None = None
    """Keywords or categories for the file."""
    table_users: list[str] | None = None
    """List of users who have access to the file."""
    project_id: str | None = None

    metadata_extra: dict | None = None

    add_tags: list[str] | None = None
    add_table_users: list[str] | None = None

    file_id: str | None = None
    """ID of a new file to replace the table data"""
    params: TableLoadParams | None = None
    """Parameters for loading data from the new file"""
    data_format: Literal["json", "csv", "file", "load_from_raw", "auto"] | None = None
    """How is the table data stored, JSON direct in the DB, CSV string,
    a seperate file, or loaded from the raw file using saved params. Only used if fileId is provided."""

    def get_update_dict(self):
        return self.model_dump(exclude_unset=True, exclude_none=True, exclude={"add_tags", "add_table_users", "file_id", "params"})


# We'll keep this for backward compatibility but it will be deprecated
class ReplaceTableData(CamelModel):
    """Request model for replacing table data with data from a new file"""

    file_id: str
    """ID of the file containing the new data"""
    params: TableLoadParams | None = None
    """Optional parameters for loading the data, if not provided will use the existing params"""
