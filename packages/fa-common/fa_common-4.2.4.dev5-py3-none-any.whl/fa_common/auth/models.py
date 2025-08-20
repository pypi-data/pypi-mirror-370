from datetime import UTC, date, datetime
from typing import List, Optional

from pydantic import AnyUrl, EmailStr, Field, computed_field, model_validator

from fa_common.auth.enums import AccessLevel, PermissionType
from fa_common.models import CamelModel


class AuthUser(CamelModel):
    sub: str
    name: str = "Unknown User"
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    country: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    emails: Optional[List[EmailStr]] = None
    email_verified: bool = Field(False, title="Email Verified")
    picture: Optional[AnyUrl] = None
    updated_at: Optional[datetime] = Field(None, title="Updated At")
    scopes: List[str] = []
    """Scope are now being used by the authentication system to store predictable
    permission names generated from a users roles & permissions, not to be used to pass permissions from OIDC"""
    roles: List[str] = []

    @model_validator(mode="after")
    def set_name_to_given_family(self):
        if (self.name is None or self.name == "Unknown User") and (self.given_name or self.family_name):
            self.name = f"{self.given_name} {self.family_name}"

        if self.email is None and self.emails is not None and len(self.emails) > 0:
            self.email = self.emails[0]

        return self


class PermissionDef(CamelModel):
    type: PermissionType = PermissionType.APP_ACCESS
    feature_name: str | None = None
    """Name of the app feature, required for APP_FEATURE permission"""
    app_slug: str
    """The app this permission is associated with, this should exactly match the AppDB slug."""

    @computed_field
    @property
    def name(self) -> str:
        if self.type == PermissionType.APP_ACCESS:
            return f"{self.app_slug}_access"
        elif self.type == PermissionType.APP_FEATURE:
            if not self.feature_name:
                raise ValueError("Feature name must be provided for APP_FEATURE permission")
            return f"{self.app_slug}_{self.feature_name}"
        raise ValueError("Permission type not recognised")

    @staticmethod
    def access_scope_name(app_slug: str, level: AccessLevel) -> str:
        if not level:
            raise ValueError("Level must be provided for APP_ACCESS permission")
        return f"{app_slug}_access_{level.name.lower()}"


class Permission(PermissionDef):
    """Applied permission"""

    expiry: date | None = None
    value: int | AccessLevel | None = None
    """Context sensitive field that could denote access level or some other restriction"""
    applied_by: str | None = None
    """The licence ID, User ID or other reference for what applied this permissions"""

    def get_value(self) -> int:
        """Used for comparisons of which permission is better"""
        if self.value is None:
            return -1

        return self.value if isinstance(self.value, int) else self.value.value

    def as_scopes(self) -> list[str]:
        scopes = []

        if self.type == PermissionType.APP_ACCESS:
            # Create a scope for each access level at or below the current int value excluding 0
            if not self.value:
                raise ValueError("Value must be set for APP_ACCESS permission")
            for level in AccessLevel:
                self_value = self.value if isinstance(self.value, int) else self.value.value
                if level.value <= self_value and level.value > 0:
                    scopes.append(self.access_scope_name(self.app_slug, level))
        else:
            scopes.append(self.name)

        return scopes

    def is_expired(self) -> bool:
        return self.expiry is not None and self.expiry < datetime.now(tz=UTC).date()


class BaseRole(CamelModel):
    name: str = Field(..., max_length=20, description="Unique name for the role", pattern=r"^[a-z0-9_]+$")
    description: str | None = None
    permissions: list[Permission] = []

    allow_auto_assign: bool = False
    """If true this role will be automatically assigned either always or based on an email address"""
    auto_assign_email_regex: str | None = None
    """Regex to match email addresses that should automatically be assigned this role if None all emails will be considered a match"""
