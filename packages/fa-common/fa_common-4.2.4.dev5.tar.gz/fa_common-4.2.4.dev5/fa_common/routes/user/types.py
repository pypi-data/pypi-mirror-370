from pydantic import AnyUrl

from fa_common.auth.models import BaseRole, PermissionDef
from fa_common.models import CamelModel


class UpdateUserMe(CamelModel):
    name: str | None = None
    picture: AnyUrl | None = None
    country: str | None = None
    nickname: str | None = None


class UpdateUser(UpdateUserMe):
    app_roles: list[BaseRole] = []
    permissions: list[PermissionDef] = []
