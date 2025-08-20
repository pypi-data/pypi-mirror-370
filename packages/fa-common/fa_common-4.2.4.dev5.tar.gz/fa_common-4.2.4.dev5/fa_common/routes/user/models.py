from random import choice
from string import ascii_letters, digits
from typing import Any, Dict, List, Set

import pymongo
from beanie import Document, PydanticObjectId
from bson import ObjectId

from fa_common import BadRequestError, NotFoundError
from fa_common.auth.models import AuthUser
from fa_common.config import get_settings
from fa_common.models import SimplePerson, StorageLocation, TimeStampedModel
from fa_common.routes.shared.models import HasPermissions
from fa_common.utils import uuid4_as_str, validate_id


class UserDB(Document, TimeStampedModel, AuthUser, HasPermissions):
    """User database model."""

    valid_user: bool = True
    settings: Dict[str, Any] | None = None
    """User settings, may be app specific."""
    storage: Dict[str, StorageLocation] = {}
    """Key is use to distinguish between different apps."""
    api_key: str | None = None

    @staticmethod
    def _api_out_exclude() -> Set[str]:
        """Fields to exclude from an API output."""
        return {"updated_at", "created", "valid_user"}

    async def set_roles(self, roles: List[str]):
        for role in roles:
            self.roles.append(role)

        await self.save()  # type: ignore

    async def generate_api_key(self):
        new_key = uuid4_as_str()

        duplicates = await self.find(UserDB.api_key == new_key).to_list()
        if duplicates is not None and len(duplicates) > 0:
            raise ValueError("Generating API key encountered a duplicate, please try again.")
        self.api_key = new_key
        await self.save()  # type: ignore
        return self.api_key

    def add_custom_storage_location(self, location_id: str, location: StorageLocation):
        self.storage[location_id] = location

    def create_user_storage_location(self, location_id: str):
        if self.id is None:
            raise ValueError("Trying to set a user folder on a user without an ID")

        if location_id in self.storage:
            raise ValueError(f"Storage location {location_id} already exists")

        self.storage[location_id] = StorageLocation(
            app_created=True, bucket_name=get_settings().BUCKET_NAME, path_prefix=self.generate_storage_path(self.name, self.sub)
        )

    def get_storage_location(self, location_id: str, create=True) -> StorageLocation:
        if location_id not in self.storage:
            if create:
                self.create_user_storage_location(location_id)
            else:
                raise ValueError(f"Storage location {location_id} does not exist")

        return self.storage[location_id]

    @classmethod
    def generate_user_prefix(cls, name: str) -> str:
        if len(name) >= 3:
            return name[:3].lower()
        elif name != "":
            return name.lower()
        else:
            return "".join(choice(ascii_letters + digits) for _ in range(3))

    @classmethod
    def generate_storage_path(cls, name: str, user_id: str | PydanticObjectId) -> str:
        # # S3 + GCP bucket naming standard (S3 is more strict), all lowercase and no '_'
        # # Adding prefix to avoid potential conflicts from going all lowercase

        np = cls.generate_user_prefix(name)
        return f"{get_settings().BUCKET_USER_FOLDER}{np}-{str(user_id).lower()}"

    @classmethod
    async def get_user_by_email(cls, email: str) -> "UserDB":
        """Get user by email address"""
        user = await cls.find_one(cls.email == email)
        if not user:
            raise NotFoundError(f"User with email {email} not found")
        return user

    @classmethod
    async def get_user_by_sub_or_id(cls, sub_or_id: str | ObjectId) -> "UserDB":
        """Get user by sub"""
        try:
            _id = validate_id(sub_or_id)
            user = await cls.get(_id)
        except BadRequestError:
            # If not a valid ID, try to get by sub
            user = await cls.find_one(cls.sub == sub_or_id)
        if not user:
            raise NotFoundError(f"User with id {sub_or_id} not found")
        return user

    @classmethod
    async def simple_person_lookup(cls, sub_or_id: str) -> SimplePerson:
        """Get user by sub"""
        user = await cls.get_user_by_sub_or_id(sub_or_id)

        return SimplePerson(
            id=str(user.id),
            name=user.name,
            email=user.email,
        )

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}user"
        indexes = [pymongo.IndexModel([("sub", pymongo.ASCENDING)], unique=True)]
