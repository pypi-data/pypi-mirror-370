from fastapi import Depends

from fa_common.auth.models import AuthUser
from fa_common.auth.utils import get_api_key
from fa_common.config import get_settings
from fa_common.routes.user.models import UserDB


async def get_api_key_app_user(api_key=Depends(get_api_key)) -> AuthUser | None:
    """API Key function that support user specific API Keys."""
    user = None
    if api_key is not None and api_key != "":
        if get_settings().MASTER_API_KEY is not None and api_key == get_settings().MASTER_API_KEY:
            if get_settings().DEFAULT_USER_SUB:
                # Return a pre-configured default user from the DB
                user = await UserDB.find_one(UserDB.sub == get_settings().DEFAULT_USER_SUB)
            else:
                user = AuthUser(
                    sub="standalone", name="User", email="default-user@app.au", email_verified=False, scopes=["read:me"], updated_at=None
                )

        else:
            user = await UserDB.find_one(UserDB.api_key == api_key)
    return AuthUser(**user.model_dump()) if isinstance(user, UserDB) else user
