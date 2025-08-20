import contextlib
from typing import Annotated, Any
from xmlrpc.client import boolean

from beanie import Document, Indexed, Link, PydanticObjectId
from bson import ObjectId
from pydantic import Field, field_validator, model_validator

from fa_common import NotFoundError, get_settings
from fa_common.auth.models import Permission
from fa_common.auth.utils import get_admin_scope
from fa_common.models import CamelModel, SimplePerson, StorageLocation, TimeStampedModel
from fa_common.routes.shared.models import HasPermissions
from fa_common.routes.user.models import UserDB


class ProjectBase(TimeStampedModel):
    name: str = Field(..., max_length=100)
    description: str | None = ""
    dataset_links: list[str] = []
    tags: list[str] = []
    project_users: list[str] = []
    """List of user emails that have access to the project."""
    is_public: boolean = False
    storage: StorageLocation | None = None  # type: ignore


class ProjectItem(ProjectBase):
    id: PydanticObjectId | str
    owner: SimplePerson
    """Owner of the Project"""

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator("owner", mode="before")
    @classmethod
    def safe_link(cls, v: Any) -> Any:
        if isinstance(v, Link):
            return None
        return v


class ProjectDB(ProjectBase, Document, HasPermissions):
    user_id: Annotated[str, Indexed()]
    system_tags: list[str] = []
    """List of readonly tags applied by the backend, these will be returned in the tags list but will not be editable"""

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}project"

    @staticmethod
    def _api_out_exclude() -> set[str]:
        """Fields to exclude from an API output."""
        return set()

    @model_validator(mode="after")
    def validate_tags(self) -> "ProjectDB":
        """
        Validate that tags and system_tags contain only unique values
        and that no value in system_tags is duplicated in tags.
        """
        # Convert to sets to remove duplicates
        self.system_tags = list(set(self.system_tags))

        # Convert tags to set, then subtract system_tags to avoid duplication
        self.tags = list(set(self.tags) - set(self.system_tags))

        return self

    # DO NOT USE TEXT INDEXES for Unique fields

    def link_dataset(self, dataset_id: str):
        if dataset_id not in self.dataset_links:
            self.dataset_links.append(dataset_id)

    def unlink_dataset(self, dataset_id: str):
        if dataset_id in self.dataset_links:
            self.dataset_links.remove(dataset_id)

    async def initialise_project(self):
        if self.id is not None:
            raise ValueError("Project already initialised")
        settings = get_settings()
        self.id = PydanticObjectId()
        self.storage = StorageLocation(
            bucket_name=settings.BUCKET_NAME,
            path_prefix=f"{settings.BUCKET_PROJECT_FOLDER}{self.id}",
            description="Default Project file storage",
        )

        return await self.save()

    async def to_project_item(self) -> ProjectItem:
        """Convert this project to a ProjectItem."""
        owner = SimplePerson(id=self.user_id, name="Unknown", email=None)
        tags = self.tags + self.system_tags
        with contextlib.suppress(NotFoundError):
            owner = await UserDB.simple_person_lookup(self.user_id)

        return ProjectItem(owner=owner, tags=tags, **self.model_dump(exclude={"files", "storage", "tags", "system_tags"}))

    def get_storage(self) -> StorageLocation:
        if self.id is None:
            raise ValueError("Project must be saved before storage can be accessed")

        if self.storage is None:
            settings = get_settings()
            self.storage = StorageLocation(
                bucket_name=settings.BUCKET_NAME,
                path_prefix=f"{settings.BUCKET_PROJECT_FOLDER}/{self.id}",
                description="Default Project file storage",
            )
        return self.storage

    async def user_has_access(self, user: UserDB) -> bool:
        """Check if the user has access to this project."""
        if self.user_id == user.sub or self.user_id == str(user.id) or self.is_public or get_admin_scope() in user.roles:
            return True

        return bool(user.email and user.email.lower() in [email.lower() for email in self.project_users])


class CreateProject(CamelModel):
    name: str = Field(..., max_length=100)
    description: str = ""
    """Project description."""
    tags: list[str] = []
    project_users: list[str] = []


class CreateAdminProject(CreateProject):
    system_tags: list[str] = []
    """System tags are readonly tags applied by the backend, these will be returned in the tags list but will not be editable"""
    permissions: list[Permission] = []
    is_public: bool = False
    """Project is public and can be accessed by anyone with the link, primarily used for example projects."""


class UpdateProject(CamelModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    """Project description."""
    tags: list[str] | None = None
    """Tags replaces existing tags with the new array unless None is passed in which case it is ignored."""
    add_tags: list[str] | None = None
    """Add tags appends the new tags to the existing tags unless None is passed in which case it is ignored."""
    project_users: list[str] | None = None
    """Project users replaces existing project users with the new array unless None is passed in which case it is
    ignored.
    """
    add_project_users: list[str] | None = None
    """Add project users appends the new project users to the existing project users unless None is passed in which case
    it is ignored.
    """

    def get_update_dict(self) -> dict:
        return self.model_dump(exclude_unset=True, exclude_none=True, exclude={"add_tags", "add_project_users"})
