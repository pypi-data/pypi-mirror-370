from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, List

import regex
from beanie import Document, Indexed, Link
from pydantic import model_validator
from pymongo import ASCENDING, IndexModel
from pytz import UTC

from fa_common import CamelModel, get_settings
from fa_common.auth.models import AccessLevel, BaseRole, Permission, PermissionDef, PermissionType
from fa_common.models import TimeStampedModel
from fa_common.routes.modules.models import ModuleDocument


class ProjectStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"
    ERROR = "ERROR"


class TableSort(CamelModel):
    column: str
    ascending: bool = True


class TableLoadParams(CamelModel):
    sheet: str | int | None = None
    separator: str | None = None
    encoding: str | None = None
    transpose: bool = False
    header_start_row: int = 0
    data_start_row: int = 1
    data_end_row: int | None = None


class TableInfo(CamelModel):
    columns: list[str]
    numeric_columns: list[str] = []
    total_rows: int | None = 0
    data: dict | str | None = None


class ColumnDefinition(CamelModel):
    name: str
    position: int


class ColumnDefinitionRange(ColumnDefinition):
    length: int

    def get_name(self, number: int) -> str:
        return f"{self.name}_{number}"

    def get_position(self, number: int) -> int:
        return self.position + number

    def get_all_names(self) -> List[str]:
        return [self.get_name(i) for i in range(self.length)]

    def get_all_postions(self) -> List[int]:
        return [self.get_position(i) for i in range(self.length)]


class RoleDB(Document, BaseRole):
    # users: list[BackLink["UserDB"]] = Field(original_field="app_roles")  # Back links don't work very well as of 5/11/24
    """Back link to users with this role. Use primary for cleaning up user roles on delete"""

    @classmethod
    async def auto_assigned_roles(cls, email: str) -> list["RoleDB"]:
        roles = []
        auto_roles = await cls.find(cls.allow_auto_assign == True).to_list()  # noqa

        for role in auto_roles:
            if not role.auto_assign_email_regex or regex.match(role.auto_assign_email_regex, email) is not None:
                roles.append(role)
        return roles

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}roles"
        indexes = [IndexModel([("name", ASCENDING)], name="role_name_index", unique=True)]


class AppDB(Document, TimeStampedModel):
    """
    TODO: Extend this model to provide fields required for the app gallery and module management
    """

    slug: Annotated[str, Indexed(unique=True)]
    """Unique identifier for the app used for scopes"""
    name: str
    description: str | None = None
    allowed_permissions: list[PermissionDef]
    """List of permission definitions that this app uses"""
    root_app: bool = False
    module: Link[ModuleDocument] | None = None
    route_path: str | None = None
    """Path used for routing to this app"""
    navigation_order: int = 100
    """Order in which this app should appear in navigation"""

    @model_validator(mode="before")
    @classmethod
    def check_name(cls, data: Any) -> Any:
        if isinstance(data, dict) and "slug" not in data and "name" in data:
            data["slug"] = data["name"].lower().replace(" ", "_")
            # truncate to 20 characters or less
            data["slug"] = data["slug"][:20] if len(data["slug"]) > 20 else data["slug"]
            # Set default route path if not provided
            if "route_path" not in data:
                data["route_path"] = f"/{data['slug']}"
        return data

    def get_access_scope(self, level: AccessLevel) -> str:
        for perm in self.allowed_permissions:
            if perm.type == PermissionType.APP_ACCESS:
                return f"{self.slug}_access_{level.name.lower()}"
        raise ValueError("No access permission found for this app")

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}apps"


class HasPermissions(CamelModel):
    app_roles: list[Link[RoleDB]] | None = None
    permissions: list[Permission] = []
    scopes: list[str] = []

    def apply_permissions(self, permissions: list[Permission]):
        """
        if items in permissions have a name that is unique within self.permissions then add it to the list, if the name is a duplicate keep
        the permission with the latest expiry or the highest value
        """
        for perm in permissions:
            found = False
            replaced = False
            top_value = -2
            top_expiry: date | None = datetime.now(tz=UTC).date()
            for i, existing_perm in enumerate(self.permissions):
                if existing_perm.name == perm.name:
                    found = True
                    if (
                        (existing_perm.expiry is not None and (perm.expiry is None or perm.expiry > existing_perm.expiry))
                        or existing_perm.expiry == perm.expiry
                        and perm.get_value() >= existing_perm.get_value()
                    ):
                        # If new permission has better or the same expiry and better or same value
                        replaced = True
                        self.permissions[i] = perm
                        break
                    top_value = max(top_value, existing_perm.get_value())
                    top_expiry = None if (top_expiry or existing_perm.expiry is None) else max(top_expiry, existing_perm.expiry)  # type: ignore

            if not found or (not replaced and (perm.expiry == top_expiry or perm.get_value() == top_value)):
                # Not found or has something that is better
                self.permissions.append(perm)

        self.refresh_permissions()

    def remove_permissions_by_ref(self, reference: str):
        """Remove permissions that were applied by a specific reference"""
        self.permissions = [perm for perm in self.permissions if perm.applied_by != reference]
        self.refresh_permissions()

    def refresh_permissions(self):
        for perm in self.permissions:
            if perm.is_expired():
                self.permissions.remove(perm)

        self.update_scopes()

    def update_scopes(self):
        """Update the scopes based on the roles and app roles. Scopes are used for API permissions"""
        scopes = set()

        if self.permissions is not None:
            for perm in self.permissions:
                scopes.update(perm.as_scopes())

        if self.app_roles is not None:
            for role in self.app_roles:
                if isinstance(role, RoleDB):
                    for perm in role.permissions:  # type: ignore
                        scopes.update(perm.as_scopes())

        self.scopes = list(scopes)

    async def get_accessible_apps(self) -> list[AppDB]:
        """Get list of apps that the user has access to based on their permissions"""
        apps = await AppDB.find().to_list()
        accessible_apps = []

        for app in apps:
            access_scope = app.get_access_scope(AccessLevel.READ)
            if any(access_scope in scope for scope in self.scopes):
                accessible_apps.append(app)

        return accessible_apps

    async def has_app_access(self, app_slug: str, level: AccessLevel = AccessLevel.READ) -> bool:
        """Check if user has access to a specific app at the specified level"""
        app = await AppDB.find_one(AppDB.slug == app_slug)
        if not app:
            return False

        try:
            access_scope = app.get_access_scope(level)
            return any(access_scope in scope for scope in self.scopes)
        except ValueError:
            return False
