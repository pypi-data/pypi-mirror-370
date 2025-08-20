import re
from typing import List

from fastapi import APIRouter, Depends, Security
from fastapi.security import SecurityScopes

from fa_common import AuthType, DatabaseError, NotFoundError, UnknownError, get_settings
from fa_common import logger as LOG
from fa_common.auth import AuthUser
from fa_common.auth.models import BaseRole, PermissionDef
from fa_common.auth.utils import get_admin_scope
from fa_common.exceptions import UnauthorizedError
from fa_common.models import Message, MessageValue
from fa_common.routes.shared.models import AppDB, RoleDB
from fa_common.routes.user import service
from fa_common.routes.user.models import UserDB
from fa_common.routes.user.service import create_app, get_app, get_current_app_user, list_apps, update_app
from fa_common.routes.user.types import UpdateUser, UpdateUserMe

if get_settings().AUTH_TYPE is AuthType.STANDALONE:
    LOG.info("Using Standalone AuthType")
    from fa_common.auth import get_standalone_user as get_current_user
else:
    from fa_common.auth import get_current_user  # type: ignore


router = APIRouter()


@router.get("/me", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def read_user_me(
    create: bool = False,
    current_user: AuthUser = Security(get_current_user),
) -> UserDB:
    """
    Read the logged in user can optionally create the Licence user
    record from the AAD user record if it doesn't exist.

    Returns:
        [LicenceUser] -- [Current User]
    """
    try:
        app_user: UserDB = await get_current_app_user(security_scopes=SecurityScopes(), current_user=current_user)
    except UnauthorizedError as err:
        if create:
            return await service.create_user(current_user)
        raise NotFoundError(f"User {current_user.email} not found.") from err
    LOG.debug(app_user)
    return app_user


@router.patch("/me", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def update_user_me(
    user_in: UpdateUserMe,
    current_user: UserDB = Security(service.get_current_app_user),
) -> UserDB:
    """Update the logged in user.

    Returns:
        [type] -- [description]
    """
    try:
        return await service.update_user(current_user, update_data=user_in.model_dump(exclude_unset=True))
    except DatabaseError as err:
        raise UnknownError(detail=err) from err


if get_settings().ENABLE_API_KEYS:

    @router.post("/me/api-key", response_model=MessageValue[str])  # type: ignore
    async def create_api_key(
        current_user: UserDB = Security(get_current_app_user),
    ) -> MessageValue[str]:
        """Generates a new API Key for the logged in user.

        Returns:
            [type] -- [description]
        """
        try:
            api_key = await current_user.generate_api_key()
        except DatabaseError as err:
            raise UnknownError(detail=err) from err

        return MessageValue[str](
            message=f"New API Key Generated for user {current_user.name}, note only one key can be active at a time.", return_value=api_key
        )


@router.delete("/me", response_model=Message)
async def delete_user_me(current_user: UserDB = Security(get_current_app_user)):
    """Update the logged in user.

    Returns:
        [type] -- [description]
    """
    try:
        await service.delete_user(current_user)
    except DatabaseError as err:
        raise UnknownError(detail=err) from err

    return Message(message="Your user was deleted successfully")


@router.get("/exists/{email}", response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def user_exists(
    email: str,
    current_user: UserDB = Depends(get_current_app_user),
) -> bool:
    """Find users based on the search string."""
    # Basic email regex pattern
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not email or not re.fullmatch(email_regex, email):
        return False
    return await service.user_exists(email)


@router.get("", response_model=list[UserDB], response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def find_users_route(
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()]),
) -> List[UserDB]:
    """Find users based on the search string."""
    return await service.find_users(search, limit, offset)


@router.patch("/{user_sub}", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())
async def patch_user(
    user_sub: str,
    user_in: UpdateUser,
    current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()]),
) -> UserDB:
    """Update an existing `User`."""
    try:
        user = await UserDB.find_one(UserDB.sub == user_sub)
        if not user:
            raise NotFoundError("Unable to find User to update!")
    except DatabaseError as e:
        raise UnknownError(detail=e) from e
    updated_user = await service.update_user(user, update_data=user_in.model_dump(exclude_unset=True))
    return updated_user.model_dump(exclude=UserDB._api_out_exclude())  # type: ignore


auth_router = APIRouter()


@auth_router.get("/role", response_model=list[BaseRole])
async def list_roles(start_with: str | None = None):
    """Gets the names of all available modules."""
    if start_with:
        return await RoleDB.find({"name": {"$regex": f"^{start_with}", "$options": "i"}}).to_list()
    return await RoleDB.find_all().to_list()


@auth_router.get("/role/{name}", response_model=BaseRole)
async def get_role(name: str):
    """Given the name of a role, it returns its full information."""
    role = await RoleDB.find_one(RoleDB.name == name, fetch_links=False)
    if not role:
        raise NotFoundError(f"Role {name} not found")
    return role


@auth_router.put("/role", response_model=BaseRole)
async def create_role(new_role: BaseRole, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])):
    """Creates a new module."""
    return await service.create_role(new_role)


@auth_router.post("/role", response_model=BaseRole)
async def update_role(updated_role: BaseRole, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])):
    """Creates a new module."""

    return await service.update_role(updated_role)


@auth_router.delete("/role/{name}", response_model=Message)
async def delete_role(name: str, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])):
    """Creates a new module."""
    await service.delete_role(name)
    return Message(message=f"Role {name} deleted successfully")


@auth_router.get("/app", response_model=List[AppDB])
async def list_apps_route(start_with: str | None = None):
    """Gets the names of all available apps."""
    return await list_apps(start_with)


@auth_router.post("/app", response_model=AppDB)
async def create_app_route(new_app: AppDB, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])):
    """Creates a new app."""
    return await create_app(new_app)


@auth_router.patch("/app/{app_slug}", response_model=AppDB)
async def update_app_route(
    app_slug: str, update_data: dict, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Updates an existing app."""
    return await update_app(app_slug, update_data)


@auth_router.get("/app/{app_slug}", response_model=AppDB)
async def get_app_route(app_slug: str):
    """Gets the details of an app."""
    return await get_app(app_slug)


@auth_router.get("/app/permission", response_model=list[PermissionDef])
async def list_all_permissions_route():
    """Gets the names of all available permissions."""
    return await service.list_all_permissions()
