from datetime import date, datetime, time, timezone
from typing import Annotated, Any, Dict, Generic, List, TypeVar

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, computed_field, field_validator
from pydantic.functional_serializers import PlainSerializer

from fa_common.utils import sizeof_fmt, utcnow

MT = TypeVar("MT")


def camel_case(string: str) -> str:
    if not isinstance(string, str):
        raise ValueError("Input must be of type str")

    first_alphabetic_character_index = -1
    for index, character in enumerate(string):
        if character.isalpha():
            first_alphabetic_character_index = index
            break

    empty = ""

    if first_alphabetic_character_index == -1:
        return empty

    string = string[first_alphabetic_character_index:]

    titled_string_generator = (character for character in string.title() if character.isalnum())

    try:
        return next(titled_string_generator).lower() + empty.join(titled_string_generator)

    except StopIteration:
        return empty


def to_camel(string):
    if string == "id":
        return "_id"
    if string.startswith("_"):  # "_id"
        return string
    return camel_case(string)


DatetimeType = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.replace(microsecond=0, tzinfo=timezone.utc).isoformat(),
        return_type=str,
        when_used="json",
    ),
]
DateType = Annotated[date, PlainSerializer(lambda dt: dt.isoformat(), return_type=str, when_used="json")]
TimeType = Annotated[
    time,
    PlainSerializer(
        lambda dt: dt.replace(microsecond=0, tzinfo=timezone.utc).isoformat(),
        return_type=str,
        when_used="json",
    ),
]


class CamelModel(BaseModel):
    """
    Replacement for pydantic BaseModel which simply adds a camel case alias to every field
    NOTE: This has been updated for Pydantic 2 to remove some common encoding helpers.
    NOTE: Camel case handling also converts "id" to "_id" for MongoDB compatibility and general consistancy.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SimplePerson(CamelModel):
    id: str
    name: str
    email: EmailStr | None = None

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v


class SimpleProject(CamelModel):
    id: str
    name: str

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v


class File(CamelModel):
    id: str | None = None  # id can be path or database id
    """Normally equal to the full path (path/name) but could be a database id or other unique reference."""

    size: str | None = None  # e.g. '3 KB'
    size_bytes: int | None = None
    url: str | None = None  # Intenral URL e.g. s3://bucket/path/to/file
    """Internal URL to the file e.g. s3://my-bucket/path/to/file.txt."""
    public_url: str | None = None
    """Public download url normally set as part of a presigned url."""
    dir: bool = False
    path: str | None = None
    """Path to current item doesn't include the file name or bucket (e.g. /path/to/file)."""
    name: str
    """Name of the file or folder e.g. file.txt."""
    bucket: str = ""
    """Name of the bucket or root folder."""
    content_type: str | None = None
    """Mime type of the file."""

    db_ref: str | None = None
    """ID for the DB record that references this file if it exists in a database."""

    def set_size(self, bytes: int):  # noqa: A002
        self.size = sizeof_fmt(bytes)
        self.size_bytes = bytes

    @computed_field
    @property
    def extension(self) -> str:
        if self.name:
            parts = self.name.split(".")
            if len(parts) > 1:
                return parts[-1]
        return ""

    @computed_field
    @property
    def full_path(self) -> str:
        if self.path:
            return f"{self.path}/{self.name}".replace("//", "/")
        return self.name


class FileDownloadRef(CamelModel):
    name: str
    url: str
    extension: str
    size: int


class PaginationListResponse(CamelModel, Generic[MT]):
    values: list[MT]
    total: int = 0
    limit: int = 0
    offset: int = 0


class Message(CamelModel):
    message: str = ""
    warnings: List[str] | None = None


class MessageValue(Message, Generic[MT]):
    return_value: MT | None = None


class MessageValueList(Message):
    return_value: List[str]


class MessageValueFiles(Message):
    return_value: List[File]


class ErrorResponse(CamelModel):
    code: str | None = None
    detail: str | None = None
    fields: List[Dict[str, Any]] | None = None
    error: str | None = None
    errors: List[Dict[str, Any]] = []
    trace: str | None = None


class Version(CamelModel):
    version: str
    commit_id: str | None = None
    build_date: datetime | str | None = None
    framework_version: str | None = None


class StorageLocation(CamelModel):
    """"""

    bucket_name: str = ""
    """Name of the bucket, None for local storage."""
    path_prefix: str = ""
    """Absolute Path for the StorageLocation in the bucket, use '/' to separate folders."""

    description: str | None = None
    """What is this storage location for?"""

    app_created: bool = True

    @field_validator("path_prefix")
    @classmethod
    def validate_path_prefix(cls, v: str) -> str:
        """Validate the path prefix and convert double slashes to single slash."""
        if v:
            v = v.replace("//", "/")
        return v

    @computed_field
    def storage_folder(self) -> str:
        """Folder name for the storage location, last part of the path prefix."""
        if self.path_prefix:
            return self.path_prefix.split("/")[-1]
        return ""

    @computed_field
    def storage_full_path(self) -> str:
        """Full path including the bucket name and path prefix."""
        path = ""
        if self.bucket_name:
            path += self.bucket_name
        if self.path_prefix:
            if path:
                path += "/"
            return f"{path}{self.path_prefix}"
        return path


class TimeStampedModel(CamelModel):
    """
    TimeStampedModel (FOR BEANIE) to use when you need to have `created` field,
    populated at your model creation time.

    Use it as follows:

    .. code-block:: python

        class MyTimeStampedModel(Document, TimeStampedModel): # from beanie import Document

            class Collection:
                name = "my_model"

        mymodel = MyTimeStampedModel()
        mymodel.save()

        assert isinstance(mymodel.id, int)
        assert isinstance(mymodel.created, datetime)
    """

    created: datetime | None = None

    @field_validator("created", mode="before")
    @classmethod
    def set_created_now(cls, v: datetime | None) -> datetime:
        """If created is supplied (ex. from DB) -> use it, otherwise generate new."""
        if v is not None:
            return v
        now = utcnow()
        return now.replace(microsecond=0)
