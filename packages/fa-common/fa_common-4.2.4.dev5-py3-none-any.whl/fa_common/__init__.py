from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

from .config import AuthType, DatabaseType, FACommonSettings, get_settings
from .enums import StorageType, WorkflowEnums
from .exception_handlers import setup_exception_handlers
from .exceptions import (
    AlreadyExistsError,
    BadRequestError,
    DatabaseError,
    ForbiddenError,
    HTTPException,
    InternalServerError,
    NotFoundError,
    StorageError,
    UnauthorizedError,
    UnImplementedError,
    UnknownError,
)
from .models import CamelModel, ErrorResponse, File, FileDownloadRef, Message, MessageValue, MessageValueFiles, MessageValueList
from .utils import (
    async_get,
    deprecated,
    deprecated_class,
    force_async,
    force_sync,
    get_current_app,
    get_logger,
    get_now,
    get_remote_schema,
    get_timezone,
    logger,
    resolve_dotted_path,
    retry,
    sizeof_fmt,
    utcnow,
)

__author__ = "Samuel Bradley"
__email__ = "sam.bradley@csiro.au"
__version__ = "4.2.4.dev5"


async def start_app(app: FastAPI):
    from fa_common.db import setup_db
    from fa_common.storage import setup_storage

    await setup_db(app)
    setup_storage(app)
    if get_settings().ENABLE_WORKFLOW:
        try:
            from fa_common.workflow import setup_workflow

            setup_workflow(app)
        except ValueError as err:
            logger.error(
                "Workflow dependencies are missing, if you are planning to use workflows make sure the optional"
                + " dependencies are installed"
            )
            raise err from err

    if get_settings().USE_BEANIE and get_settings().USE_APP_ROLES:
        from fa_common.routes.user.service import init_app_roles

        await init_app_roles()


async def stop_app(app: FastAPI):
    pass


def create_app(
    env_path: str | None = None,
    disable_gzip: bool = False,
    on_start: Callable[[FastAPI], Awaitable[None]] | None = None,
    on_stop: Callable[[FastAPI], Awaitable[None]] | None = None,
    **kwargs,
) -> FastAPI:
    settings = get_settings(env_path)

    if settings.ROLLBAR_KEY is not None:
        import rollbar

        rollbar.init(settings.ROLLBAR_KEY, environment=settings.ENVIRONMENT, handler="async", include_request_body=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting App")
        await start_app(app)
        if on_start is not None:
            await on_start(app)
        yield
        logger.info("Stopping App")
        await stop_app(app)
        if on_stop is not None:
            await on_stop(app)

    app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_PRE_PATH}/openapi.json", lifespan=lifespan, **kwargs)

    if settings.ENABLE_API_KEYS:
        from fa_common.auth.utils import get_api_key_user
        from fa_common.routes.user.utils import get_api_key_app_user

        app.dependency_overrides[get_api_key_user] = get_api_key_app_user

    if settings.ROLLBAR_KEY is not None:
        from rollbar.contrib.fastapi import add_to as rollbar_add_to
        # should be added as the first middleware

        rollbar_add_to(app)

    # CORS
    origins = []
    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        origins_raw = settings.BACKEND_CORS_ORIGINS
        for origin in origins_raw:
            use_origin = origin.strip()
            origins.append(use_origin)
        logger.info(f"Allowing Origins {origins}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=1800,  # 30 minutes - reduces preflight requests during long downloads
        )

    setup_exception_handlers(app)

    # Adds support for GZIP response
    if not disable_gzip:
        app.add_middleware(GZipMiddleware, minimum_size=5000)

    if settings.SECURE:
        import secure

        secure_headers = secure.Secure()

        @app.middleware("http")
        async def set_secure_headers(request, call_next):
            response = await call_next(request)
            secure_headers.framework.fastapi(response)
            return response

    if settings.ROLLBAR_KEY is not None:
        from rollbar.contrib.fastapi import LoggerMiddleware

        app.add_middleware(LoggerMiddleware)

    return app
