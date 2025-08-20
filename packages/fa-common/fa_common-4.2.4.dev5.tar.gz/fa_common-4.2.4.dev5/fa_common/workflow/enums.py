"""
Description: Enumerators for Workflows.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

from enum import Enum


class FileType(str, Enum):
    JSON = "json"
    YAML = "yaml"
    TXT = "txt"


class CloudBaseImage(str, Enum):
    """CloudBaseImage for download and upload."""

    AWS = "benmotevalli/aws-jq-curl"
    GUTILS = "benmotevalli/gsutil-jq-curl"


# class ModuleType(str, Enum):
#     """
#     ModuleType
#     """

#     SYNC = "sync"  # Is run via a service call
#     ASYNC = "async"  # Is executed via gitlab ci


class LocalRunModes(str, Enum):
    CONCURRENT = "concurrent"
    SEQUENTIAL = "sequential"


class JobAction(str, Enum):
    """JobAction."""

    PLAY = "play"
    RETRY = "retry"
    DELETE = "delete"
    CANCEL = "cancel"


class JobSecretTypes(str, Enum):
    """JobSecretTypes."""

    ENV = "ENV"
    MOUNT = "MOUNT"


class JobStatus(str, Enum):
    """JobStatus."""

    NOT_SET = ""
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"  # argo, gitlab
    RUNNING = "RUNNING"  # argo, gitlab
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"  # argo, gitlab
    SUCCEEDED = "SUCCEEDED"  # argo
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"
    CANCELLING = "CANCELLING"
    PAUSED = "PAUSED"
    CRASHED = "CRASHED"


class JobSubmitMode(str, Enum):
    """
    JobSubmitMode.

    ISOLATED:       runs in isolated container via Argo. The image used should be self-contained
    LOCAL:          runs on the backend api
    ISOLATED_LOCAL: runs in isolated container via Argo, but it downloads the module repo into a
                    common base image.
    """

    ISOLATED = "isolated"
    LOCAL = "local"
    ISOLATED_LOCAL = "isolated-local"


class WorkflowStoreType(str, Enum):
    """WorkflowStoreType."""

    LIVE = "live"
    STORAGE = "storage"
    ARCHIVE = "archive"
