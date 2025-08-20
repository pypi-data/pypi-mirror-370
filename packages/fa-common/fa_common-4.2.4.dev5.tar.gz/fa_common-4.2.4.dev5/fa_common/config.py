import logging
from typing import List, Optional, Set

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import AuthType, DatabaseType, StorageType, WorkflowEnums


class FACommonSettings(BaseSettings):
    VERSION: str = "4.2.4.dev5"
    API_VERSION: int = 1
    API_PRE_PATH: str = f"/api/v{API_VERSION}"

    SECURE: bool = False  # Use secure.py (set to true for prod)
    ROLLBAR_KEY: Optional[str] = None
    ROLLBAR_LOG_LEVEL: int = logging.ERROR
    FA_DEBUG: bool = False
    UNIT_TESTING: bool = False
    ENVIRONMENT: str = "local"

    APP_PATH: str = "fa_common"
    FASTAPI_APP: str = ""
    # logging configuration
    LOGGING_LEVEL: int = logging.DEBUG if FA_DEBUG else logging.INFO
    debug_timing: bool = False

    # SECRET_KEY: SecretBytes = os.urandom(32)  # type:ignore
    BUILD_DATE: Optional[str] = None
    PROJECT_NAME: str = "FastAPI Backend"
    BACKEND_CORS_ORIGINS: Set[str] = set()

    ################ STORAGE SETTINGS ##################
    STORAGE_TYPE: StorageType = StorageType.NONE
    STORAGE_ACCESS_TOKEN: Optional[str] = None
    """Access token for storage, primarily used for local testing."""
    STORAGE_ENDPOINT: Optional[str] = None
    STORAGE_SSL: bool = False

    STORAGE_ACCESS_KEY: Optional[str] = None
    """Storage access key e.g. Minio username."""
    STORAGE_SECRET_VALUE: Optional[SecretStr] = None
    """Storage secret e.g. Minio password."""

    STORAGE_SECRET_NAME: Optional[str] = None
    """Kubernetes secret name."""
    STORAGE_SECRET_KEY: Optional[str] = None
    """Kubernetes Secret key, e.g. minio password."""
    STORAGE_REGION: Optional[str] = "ap-southeast-2"

    MAX_CONTENT_LENGTH: int = 1024 * 1024 * 100  # 100MB

    BUCKET_NAME: str = ""
    BUCKET_USER_FOLDER: str = "user-storage/"
    BUCKET_PROJECT_FOLDER: str = "project-storage/"

    USE_FIREBASE: bool = False
    LOCALFS_STORAGE_PATH: Optional[str] = None
    ####################################################

    ############### WORKFLOW SETTINGS ##################
    ENABLE_WORKFLOW: bool = False
    WORKFLOW_TYPE: Optional[WorkflowEnums.Type] = WorkflowEnums.Type.ARGO

    ARGO_TOKEN: Optional[str] = None
    ARGO_URL: Optional[str] = "https://argo.csiro.easi-eo.solutions"
    ARGO_NAMESPACE: Optional[str] = "cmr-xt-argo"
    # ARGO_FILE_ACCESS_METHOD: Optional[WorkflowEnums.FileAccess.METHOD] = WorkflowEnums.FileAccess.METHOD.DIRECT
    # ARGO_FILE_ACCESS_TYPE: Optional[WorkflowEnums.FileAccess.ACCESS_TYPE] = WorkflowEnums.FileAccess.ACCESS_TYPE.SERVICE_ACCOUNT
    # ARGO_FILE_STORAGE: Optional[WorkflowEnums.FileAccess.STORAGE] = WorkflowEnums.FileAccess.STORAGE.GCS
    # FIXME: Check with Sam. This might overlap with MINIO secrets. @REVIEW. Refer to consistent naming suggestion.
    # ARGO_UPLOAD_STRATEGY: Optional[WorkflowEnums.Upload.STRATEGY] = WorkflowEnums.Upload.STRATEGY.EVERY
    # ARGO_RUN_STRATEGY: Optional[WorkflowEnums.Run.STRATEGY] = WorkflowEnums.Run.STRATEGY.GLOBAL
    # ARGO_SAVE_RUN_LOGS: Optional[bool] = True
    # ARGO_LOGGING_STRATEGY: Optional[WorkflowEnums.Logging.STRATEGY] = WorkflowEnums.Logging.STRATEGY.FROM_ARTIFACT

    WORKFLOW_UPLOAD_PATH: str = "job_data"
    ####################################################

    ################### AUTH #############################
    AUTH0_DOMAIN: str = ""
    API_AUDIENCE: str = ""
    """For AAD this is the Application ID."""
    USE_EXTERNAL_PROFILE: bool = True

    OAUTH2_JWKS_URI: str = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    OAUTH2_ISSUER: str = f"https://{AUTH0_DOMAIN}/"
    OAUTH2_AUTH_URL: str = f"https://{AUTH0_DOMAIN}/authorize?audience={API_AUDIENCE}"
    OAUTH2_SCOPES: str = '{"openid": "", "profile": "", "email": ""}'
    JWT_ALGORITHMS: List[str] = ["RS256"]
    ROLES_NAMESPACE: str = "http://namespace/roles"
    ENABLE_SCOPES: bool = True

    AUTH_TYPE: AuthType = AuthType.OAUTH2
    API_KEY_NAME: str = "api_key"
    MASTER_API_KEY: Optional[str] = None
    ENABLE_API_KEYS: bool = True
    DEFAULT_USER_SUB: Optional[str] = None  # Allows for a preconfigured default user to be added to the DB

    ADMIN_ROLE: str = "admin"
    """Default admin role, only used if USE_APP_ROLES is False."""
    USE_APP_ROLES: bool = False
    """Enable more advanced role & access management, requires Beanie to be enabled."""
    ROOT_APP_SLUG: str = "app"
    MATCH_OIDC_ROLES: bool = True
    """Roles from OIDC will be automatically matched to app roles."""

    ######################################################

    ############## DATABASE SETTINGS ####################
    DATABASE_TYPE: DatabaseType = DatabaseType.NONE  # FIRESTORE or MONGODB
    COLLECTION_PREFIX: str = ""

    MONGODB_DSN: Optional[str] = None
    MONGODB_DBNAME: Optional[str] = None
    USE_BEANIE: bool = False
    MONGO_AUTO_CONNECT: bool = True
    SQLITEDB_PATH: Optional[str] = None
    mongodb_min_pool_size: int = 0
    mongodb_max_pool_size: int = 100

    TZ: str = "UTC"
    #####################################################

    ################### EMAIL (SMTP) ####################
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = 2587
    SMTP_USER_NAME: Optional[str] = None
    SMTP_USER_PWD: Optional[str] = None
    SENDER_EMAIL: Optional[str] = None

    #####################################################

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings: Optional[FACommonSettings] = None


def get_settings(env_path=None) -> FACommonSettings:
    # Load env variables from .env file

    global settings
    if settings is None or env_path is not None:
        settings = FACommonSettings(_env_file=env_path)  # type: ignore

    return settings
