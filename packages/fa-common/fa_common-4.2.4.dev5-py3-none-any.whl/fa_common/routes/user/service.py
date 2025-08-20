from typing import Union

from beanie import WriteRules
from fastapi import Depends
from fastapi.security import SecurityScopes

from fa_common import AuthType, ForbiddenError, get_settings
from fa_common import logger as LOG
from fa_common.auth import AuthUser
from fa_common.auth.models import BaseRole, PermissionDef
from fa_common.exceptions import NotFoundError, UnauthorizedError
from fa_common.routes.files.service import delete_files_for_user
from fa_common.routes.project.service import delete_projects_for_user
from fa_common.routes.shared.models import AppDB, RoleDB
from fa_common.routes.user.models import UserDB
from fa_common.storage.utils import get_storage_client

if get_settings().AUTH_TYPE is AuthType.STANDALONE:
    from fa_common.auth import get_standalone_user as get_current_user
else:
    from fa_common.auth import get_current_user  # type:ignore


async def get_current_app_user(
    security_scopes: SecurityScopes,
    current_user: Union[AuthUser, UserDB] = Depends(get_current_user),
) -> UserDB:
    if current_user is not None and current_user.sub is not None:
        user = current_user if isinstance(current_user, UserDB) else await UserDB.find_one(UserDB.sub == current_user.sub, fetch_links=True)

        if user is not None and isinstance(user, UserDB):
            # Update roles and app roles based on OIDC roles
            if current_user.roles:
                new_app_roles = None
                new_roles = None

                new_roles = list(set(current_user.roles) - set(user.roles))
                if new_roles:
                    user.roles.extend(new_roles)

                if get_settings().USE_APP_ROLES and get_settings().MATCH_OIDC_ROLES:
                    if not user.app_roles:
                        user.app_roles = []
                        role_names = []
                    else:
                        role_names = [r.name for r in user.app_roles]  # type: ignore
                    non_app_roles = list(set(user.roles) - set(role_names))

                    if len(non_app_roles) > 0:
                        new_app_roles = await RoleDB.find({"name": {"$in": non_app_roles}}).to_list()  # type: ignore
                        if new_app_roles:
                            user.app_roles.extend(new_app_roles)  # type: ignore

            user.refresh_permissions()
            await user.save()
            for scope in security_scopes.scopes:
                if scope not in user.scopes and scope not in user.roles:
                    raise ForbiddenError(detail="Not enough permissions to access this data")

            return user

    raise UnauthorizedError(detail="The current user does not exist as a user of this application.")


async def update_user(user: UserDB, update_data: dict):
    updated_user = user.model_copy(update=update_data)
    await updated_user.save(link_rule=WriteRules.WRITE)
    updated_user.update_scopes()
    await updated_user.save()

    return updated_user


async def create_user(new_user: AuthUser) -> UserDB:
    user: UserDB = UserDB(valid_user=True, **new_user.model_dump())
    if get_settings().USE_APP_ROLES:
        user.app_roles = []

        # Apply any automatic roles
        if new_user.email:
            auto_roles = await RoleDB.auto_assigned_roles(new_user.email)
            if auto_roles:
                user.app_roles.extend(auto_roles)  # type: ignore

        # Return all roles that match existing OIDC roles
        if new_user.roles and get_settings().MATCH_OIDC_ROLES:
            matched_roles = await RoleDB.find({"name": {"$in": new_user.roles}}).to_list()
            if matched_roles:
                user.app_roles.extend(matched_roles)  # type: ignore

        user.update_scopes()

    await user.save(link_rule=WriteRules.WRITE)
    LOG.info(f"Created New User: {user.name}")

    return user


async def delete_user(user: UserDB):
    for key, storage in user.storage.items():
        if storage.app_created:
            client = get_storage_client()
            await client.delete_file(storage.bucket_name, storage.path_prefix, True)
            LOG.info(f"Deleted user storage {key}")

    await delete_files_for_user(user)
    await delete_projects_for_user(user)

    if user.id is not None:
        await user.delete()
        LOG.info(f"Deleted user {user.id}")


async def find_users(search: str | None = None, limit: int = 5, offset: int = 0):
    """Find all users with partial match on the provided `name`."""

    if search is not None:
        # partial match on the name and email
        query = {
            "$or": [
                {UserDB.name: {"$regex": search, "$options": "i"}},
                {UserDB.email: {"$regex": search, "$options": "i"}},
            ]
        }
        return await UserDB.find_many(query).limit(limit).skip(offset).to_list()
    else:
        return await UserDB.find_all().limit(limit).skip(offset).to_list()


async def user_exists(email: str) -> bool:
    """Does user with email exist in the system"""

    if email is not None:
        return await UserDB.find_one({"email": {"$regex": email, "$options": "i"}}) is not None
    return False


async def init_app_roles():
    settings = get_settings()

    if settings.ROOT_APP_SLUG:
        app = await AppDB.find_one(AppDB.slug == settings.ROOT_APP_SLUG)
        if app is None:
            app = AppDB(
                slug=settings.ROOT_APP_SLUG,
                description="Root application, automatically created",
                name=settings.PROJECT_NAME,
                allowed_permissions=[PermissionDef(app_slug=settings.ROOT_APP_SLUG)],
            )
            await app.save()
    elif settings.USE_APP_ROLES:
        raise ValueError("ROOT_APP_SLUG must be set if USE_APP_ROLES is True")


async def create_role(role: BaseRole) -> RoleDB:
    role_db = RoleDB(**role.model_dump())
    return await role_db.insert()


async def update_role(role: BaseRole) -> RoleDB:
    role_db = await RoleDB.find_one(RoleDB.name == role.name)

    if role_db is None:
        raise NotFoundError(f"Role {role.name} not found")

    updated_role = role_db.model_copy(update=role.model_dump())
    await updated_role.replace()

    return updated_role


async def delete_role(role_name: str):
    role = await RoleDB.find_one(RoleDB.name == role_name, fetch_links=True)

    if role is not None:
        # Remove the role from all users
        await UserDB.find(UserDB.app_roles.name == role.name).update_many({"$pull": {"appRoles": {"name": role.name}}})  # type: ignore

        await role.delete()
        LOG.info(f"Deleted role {role_name}")
    else:
        LOG.info(f"Role {role_name} not found")


async def list_apps(start_with: str | None = None):
    if start_with:
        return await AppDB.find({"name": {"$regex": f"^{start_with}", "$options": "i"}}).to_list()
    return await AppDB.find_all().to_list()


async def create_app(new_app: AppDB) -> AppDB:
    return await new_app.save()


async def update_app(app_slug: str, update_data: dict) -> AppDB:
    app = await AppDB.find_one(AppDB.slug == app_slug)
    if not app:
        raise NotFoundError(f"App {app_slug} not found")
    updated_app = app.model_copy(update=update_data)
    await updated_app.replace()
    return updated_app


async def get_app(app_slug: str) -> AppDB:
    app = await AppDB.find_one(AppDB.slug == app_slug)
    if not app:
        raise NotFoundError(f"App {app_slug} not found")
    return app


async def list_all_permissions() -> list[PermissionDef]:
    apps = await AppDB.find_all().to_list()
    permissions = []
    for app in apps:
        permissions.extend(app.allowed_permissions)
    return permissions
