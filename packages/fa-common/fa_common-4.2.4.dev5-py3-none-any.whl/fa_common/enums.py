"""
@SUGGESTION:
 - Keeping enums separate from models. enums are constants and they do not have any dependencies.
 - Noticed that sometimes keeping them together could cause circular dependencies.
 - If agreed, we can start refactoring this.
"""

from enum import Enum


class CommonRoles(str, Enum):
    """Common roles for users, not intended to be exhaustive, should be used as string values."""

    ADMIN = "admin"
    CSIRO = "csiro"
    STUDENT = "student"

    def __str__(self):
        return str(self.value)


class StorageType(str, Enum):
    MINIO = "MINIO"
    LOCALFS_STORAGE = "LOCALFS_STORAGE"
    NONE = "NONE"


class DatabaseType(str, Enum):
    """Supported backend database types."""

    MONGODB = "MONGODB"
    SQLITEDB = "SQLITEDB"
    NONE = "NONE"


class AuthType(str, Enum):
    """Supported user login authorisation types."""

    OAUTH2 = "OAUTH2"
    STANDALONE = "STANDALONE"


class WorkflowEnums:
    class Type(str, Enum):
        ARGO = "ARGO"
        NONE = "NONE"
        LOCAL = "LOCAL"

    class Templates(str, Enum):
        UPLOAD = "upload-template"
        DOWNLOAD = "download-template"
        RUN = "run-template"
        ARCHIVE = "archive-workflow-template"

    class TemplateFormats(str, Enum):
        TEXT = "text"
        YAML = "yaml"
        JSON = "json"

    class FileAccess:
        STORAGE = StorageType

        class Method(str, Enum):
            DIRECT = "direct"
            SIGNED_URL = "signed-url"

        # class STORAGE(str, Enum):
        #     GCS = "gcs"
        #     S3 = "S3"

        class AccessType(str, Enum):
            WITH_ROLE = "WITH_ROLE"
            WITH_SECRET = "WITH_SECRET"

    class Upload:
        class Strategy(str, Enum):
            ONE_GO = "one-go"  # This option uploads outputs of all jobs once all jobs are completed successfully.
            EVERY = "every"  # This option uploads outputs of each job the moment it is done successfully.

        class LocName(str, Enum):
            TASK_NAME = "task-name"
            POD_NAME = "pod-name"

    class Run:
        class Strategy(str, Enum):
            NODAL = "nodal"
            GLOBAL = "global"
            UNI_GLOBAL = "unified-global"
            UNI_NODAL = "unified-nodal"

        class ImagePullPolicy(str, Enum):
            ALWAYS = "Always"
            IF_NOT_PRESENT = "IfNotPresent"
            NEVER = "Never"

    class Logging:
        class Strategy(str, Enum):
            FROM_ARTIFACT = "from-artifact"  # This option outputs the log as an artifact and passes it to the upload task.
            FROM_POD = "from-pod"  # This option directly refers to the argo log location within the pod.
