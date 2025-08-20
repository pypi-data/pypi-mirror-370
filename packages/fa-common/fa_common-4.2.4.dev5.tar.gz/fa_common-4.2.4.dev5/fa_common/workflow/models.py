"""
Description: models for Workflows.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union

from dateutil import parser
from prefect.client.schemas import FlowRun as PrefectFlowRun
from prefect.client.schemas import TaskRun as PrefectTaskRun
from pydantic import ConfigDict, Field, model_validator

from fa_common import CamelModel, get_settings
from fa_common.enums import WorkflowEnums
from fa_common.models import File
from fa_common.routes.modules.types import ModuleResponse
from fa_common.storage import get_storage_client

from .enums import CloudBaseImage, JobStatus, JobSubmitMode, WorkflowStoreType


class InputJobTemplate(CamelModel):
    """InputJobTemplate."""

    files: Optional[List[File]] = []
    parameters: Union[str, dict] = '"{"message": "no inputs!"}"'


class JobSecrets(CamelModel):
    """
    :param: name: name of secret
    :param: mount_path: where to mount the secret.
    """

    name: Optional[str] = None
    mount_path: Optional[str] = None


class PrefectWorkflow:
    flow_run: Optional[PrefectFlowRun] = None
    task_runs: Optional[List[PrefectTaskRun]] = None

    def __init__(self, flow_run=None, task_runs=None, flow_run_dict=None):
        if flow_run_dict:
            self.to_obj(flow_run_dict)
            return
        self.flow_run = flow_run
        self.task_runs = task_runs

    def to_dict(self):
        flow_run_dict = self.flow_run.dict()
        flow_run_dict["task_runs"] = [task.dict() for task in self.task_runs]
        return flow_run_dict

    def to_obj(self, flow_run_dict: dict):
        self.flow_run = PrefectFlowRun(**flow_run_dict)
        self.task_runs = [PrefectTaskRun(**task) for task in flow_run_dict["task_runs"]]


class WorkflowCallBack(CamelModel):
    """
    This class defines callback attributes. Callback executes
    in the Archive Node as this node runs onExit event hook.
    Callback can be used to notify client that a workflow is completed
    and it can be used to handle post-workflow logics.

    Note that callback should be implemented in the backend
    api. The callback api then is called in the workflow.

    :param: url: callback url (implemented in the backend api)
    :param: metadata: A json string used to input metadata that you want to
    receive back on the callback, e.g. project_name.
    :param: env_secrets: can be used to pass required secrets for the
    callback, e.g. API key.
    :param: env_vars: can be used to pass required secrets for the
    callback, e.g. API key. With env_vars, the secrets can directly
    be passed from the backend api.
    """

    url: str  # URL for callback
    metadata: Optional[Union[str, Dict]] = ""
    # env_secrets: List[str] = []
    api_key: Optional[str] = None
    # env_vars: Dict = {}


class JobUploads(CamelModel):
    """
        IMPORTANT NOTE:
                All remote paths, ie: `default_path`, `custom_path`, are paths
        within a bucket.
        The props with `uri` aims to construct the full uri from
        the above paths and the bucket_name.

    :param: `default_path`: this is the default path (e.g.constructed from
    WORKFLOW_UPLOAD_PATH). All logs and workflow steps are stored here.
    Also, this is the default path where outputs of a job are stored.

    :param: `custom_path`: if defined, the main outputs of the job
    is stored in this location, instead of the default location.

    :param: `copy_paths`: this is used, if a copy of the main outputs
    are required in other locations as well.

    :param: `selected_outputs`: if empty, copies all outputs. Note
    the paths in selected_outputs are subpaths of the outputs folder
    within the container (defined by output_path in JobTemplate). These
    paths can point to either file or folder.

        :param: `bucket_name`: required for
    """

    default_path: str = ""
    custom_path: Optional[str] = None
    selected_outputs: Optional[List[str]] = []
    bucket_name: str
    zip_outputs: bool = False

    @property
    def is_custom_upload(self):
        return self.custom_path is not None and self.custom_path != ""

    @property
    def has_all_outputs(self):
        return len(self.selected_outputs) == 0 if self.selected_outputs is not None else False

    @property
    def custom_path_uri(self):
        if self.custom_path:
            storage_client = get_storage_client()
            return storage_client.get_uri(self.bucket_name, self.custom_path)
        return None

    @property
    def default_path_uri(self):
        storage_client = get_storage_client()
        return storage_client.get_uri(self.bucket_name, self.default_path)


class JobResource(CamelModel):
    cpu_req: Union[str, float]
    mem_req: str
    cpu_limit: Union[str, float]
    mem_limit: str
    eps_req: Optional[str] = None
    eps_lim: Optional[str] = None


class JobOutputs(CamelModel):
    default_path: Optional[str] = None
    custom_path: Optional[str] = None
    files: Optional[List[File]] = None
    out_json: Optional[Union[List, dict]] = None


class JobRun(CamelModel):
    """JobRun."""

    job_id: Union[str, int]
    workflow_id: Union[str, int]
    inputs: Optional[InputJobTemplate] = None
    status: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration: Optional[float] = None
    name: str = ""
    outputs: Optional[JobOutputs] = None
    # output: Optional[Union[List, dict]] = None
    log: Optional[bytes] = None
    model_config = ConfigDict(use_enum_values=True)

    def get_compare_time(self) -> datetime:
        """Get_compare_time."""
        if self.started_at is None:
            if self.status not in ["failed", "canceled", "skipped"]:
                return datetime.min.replace(tzinfo=timezone.utc)
            else:
                return datetime.now(tz=timezone.utc)
        else:
            return parser.isoparse(self.started_at)


######                                                                            #
#     # ######  ####      ######  ####  #####       # #   #####   ####   ####
#     # #      #    #     #      #    # #    #     #   #  #    # #    # #    #
######  #####  #    #     #####  #    # #    #    #     # #    # #      #    #
#   #   #      #  # #     #      #    # #####     ####### #####  #  ### #    #
#    #  #      #   #      #      #    # #   #     #     # #   #  #    # #    #
#     # ######  ### #     #       ####  #    #    #     # #    #  ####   ####


class CloudStorageConfig(CamelModel):
    """Workflow config attributes for Cloud Storage."""

    access_method: WorkflowEnums.FileAccess.Method = WorkflowEnums.FileAccess.Method.DIRECT
    access_type: WorkflowEnums.FileAccess.AccessType = WorkflowEnums.FileAccess.AccessType.WITH_ROLE
    access_secret_name: Optional[str] = None
    access_secret_key: Optional[str] = None
    save_logs: bool = True
    retry: Optional[int] = 0

    def __init__(self, **data):
        super().__init__(**data)  # Call the superclass __init__ to handle Pydantic model initialization
        settings = get_settings()
        # Directly assign the values post-initialization if not provided
        if self.access_secret_name is None:
            self.access_secret_name = settings.STORAGE_SECRET_NAME
        if self.access_secret_key is None:
            self.access_secret_key = settings.STORAGE_SECRET_KEY

    @property
    def has_secret(self) -> bool:
        """
        Checks if access type is set with secret or via a trust relationship
        through a service account.
        """
        return self.access_type == WorkflowEnums.FileAccess.AccessType.WITH_SECRET

    @property
    def cloud_base_image(self) -> str:
        """What cloud base image to use."""
        settings = get_settings()
        # TODO: Reimplment GCP support through minio
        # if settings.STORAGE_TYPE == WorkflowEnums.FileAccess.STORAGE.FIREBASE_STORAGE:
        #     return CloudBaseImage.GUTILS.value
        if settings.STORAGE_TYPE == WorkflowEnums.FileAccess.STORAGE.MINIO:
            return CloudBaseImage.AWS.value
        return None

    def set(self, **kwargs):
        """Sets attributes."""
        for key, value in kwargs.items():
            if key == "has_secret":
                raise AttributeError("has_secret is a computed property and cannot be set directly.")
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")

    def set_default(self):
        """Resets attributes to default values."""
        default_instance = CloudStorageConfig()
        for attr in vars(default_instance):
            setattr(self, attr, getattr(default_instance, attr))
        self.has_secret = self.access_type == WorkflowEnums.FileAccess.AccessType.WITH_SECRET


class UploadConfig(CloudStorageConfig):
    """Workflow config attributes for Upload Template."""

    strategy: WorkflowEnums.Upload.Strategy = WorkflowEnums.Upload.Strategy.EVERY
    loc_name: WorkflowEnums.Upload.LocName = WorkflowEnums.Upload.LocName.POD_NAME


class RunConfig(CamelModel):
    """Workflow config attributes for Run Template."""

    strategy: WorkflowEnums.Run.Strategy = WorkflowEnums.Run.Strategy.UNI_GLOBAL
    max_all_jobs_dependency: Optional[int] = 0
    save_logs: bool = True
    logging_strategy: WorkflowEnums.Logging.Strategy = WorkflowEnums.Logging.Strategy.FROM_ARTIFACT
    commands_pre: Optional[str] = "echo empty pre-command"
    commands_post: Optional[str] = "echo empty post-command"
    # Retry occurs on Error which is different to Failed
    retry: Optional[int] = 0
    enable_on_demand: Optional[bool] = False
    terminate_grace_sec: int = 60

    @property
    def is_unified(self) -> bool:
        """
        Checks if access type is set with secret or via a trust relationship
        through a service account.
        """
        return "uni" in self.strategy.value


class UsePvc(CamelModel):
    enabled: bool = False
    size: str = "2Gi"


class BaseConfig(CamelModel):
    """Workflow config attributes for Base Template."""

    continue_on_run_task_failure: bool = True
    is_error_tolerant: bool = False
    service_account_name: Optional[str] = "argo-workflow-patch"
    namespace: Optional[str] = "cmr-xt-argo"
    verify_ssl: Optional[bool] = True
    enable_pdb: Optional[bool] = True
    enable_rollbar: bool = False
    use_pvc: UsePvc = UsePvc()

    @property
    def has_argo_token(self) -> bool:
        """Checks if argo token is provided. useful for local dev."""
        st = get_settings()
        return not (st.ARGO_TOKEN is None or st.ARGO_TOKEN == "")

    @property
    def is_argo_local(self) -> bool:
        st = get_settings()
        return "localhost" in st.ARGO_URL


class ArgoTemplateConfig(CamelModel):
    """Workflow config attributes."""

    config_type: Literal["argo"] = "argo"
    download: CloudStorageConfig = CloudStorageConfig()
    upload: UploadConfig = UploadConfig()
    run: RunConfig = RunConfig()
    base: BaseConfig = BaseConfig()
    retry_on_exit: int = 0

    @property
    def logs_to_include(self) -> List:
        """Which logs to include."""
        lst_logs = []
        if self.run.save_logs:
            lst_logs.append(WorkflowEnums.Templates.RUN)
        if self.download.save_logs:
            lst_logs.append(WorkflowEnums.Templates.DOWNLOAD)
        if self.upload.save_logs:
            lst_logs.append(WorkflowEnums.Templates.UPLOAD)

        return lst_logs


class NodeResourceDuration(CamelModel):
    """NodeResourceDuration."""

    cpu: Optional[int] = None
    memory: Optional[int] = None


class Parameters(CamelModel):
    """Parameters."""

    name: Optional[str] = None
    value: Optional[Union[str, int]] = None


class ArgoArtifactRepoS3(CamelModel):
    """ArgoArtifactRepoS3."""

    key: str


class ArgoArtifacts(CamelModel):
    """ArgoArtifacts."""

    name: Optional[str] = None
    path: Optional[str] = None
    s3: Optional[ArgoArtifactRepoS3] = None


class ArgoNodeInOut(CamelModel):
    """ArgoNodeInOut."""

    parameters: Optional[List[Parameters]] = None
    artifacts: Optional[List[ArgoArtifacts]] = None


# class WorkflowId(CamelModel):
#     """WorkflowId."""

#     uid: Optional[str | int] = None
#     name: Optional[str] = None


class ArgoNode(CamelModel):
    """ArgoNode represents each node in the workflow."""

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    type: Optional[str] = None
    template_name: Optional[str] = None
    template_scope: Optional[str] = None
    phase: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: Optional[str] = None
    resources_duration: Optional[NodeResourceDuration] = None
    children: Optional[List[str]] = None
    outbound_nodes: Optional[List[str]] = None
    inputs: Optional[ArgoNodeInOut] = None
    outputs: Optional[ArgoNodeInOut] = None
    message: Optional[str] = None
    parent: Optional[str] = None

    # Extra Amendments
    pod_name: Optional[str] = None
    task_name: Optional[str] = None  # This is the task name initially defined in the manifest
    output_json: Optional[Union[List, dict]] = None
    files: Optional[List[File]] = None
    log: Optional[bytes] = None
    model_config = ConfigDict(use_enum_values=True)

    def set_pod_task_names(self):
        """
        Argo Node represents each node in the workflow. Most of these nodes
        are tasks. A task is run in a kube pod, however the pod_name is not
        directly returned when getting workflow from Argo's api. This method
        will set the pod_name of each task from available fields in the
        get workflow response.
        """
        if self.id is not None and self.name is not None:
            # Set pod-name
            match = re.match(r"^(.*?)-(\d+)$", self.id if self.id is not None else "")
            if match:
                prefix, id_number = match.groups()
                self.pod_name = f"{prefix}-{self.template_name}-{id_number}"

            # Set task-name
            parts = self.name.split(".")
            self.task_name = parts[-1] if len(parts) > 1 else ""
        # @FIXME else case

    def get_compare_time(self) -> datetime:
        """Get_compare_time."""
        if self.started_at is None:
            if self.status not in ["Failed"]:
                return datetime.min.replace(tzinfo=timezone.utc)
            else:
                return datetime.now(tz=timezone.utc)
        else:
            return parser.isoparse(self.started_at)


class ArgoWorkflowMetadata(CamelModel):
    """ArgoWorkflowMetadata."""

    name: Optional[str] = None
    generate_name: Optional[str] = None
    namespace: Optional[str] = None
    uid: Optional[str] = None
    creation_timestamp: Optional[str] = None


class ArgoWorkflowStatus(CamelModel):
    """ArgoWorkflowStatus."""

    phase: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: Optional[str] = None
    nodes: Optional[List[ArgoNode]] = []


T = TypeVar("T", bound="ArgoWorkflowRun")


class ArgoWorkflowRun(CamelModel):
    """ArgoWorkflowRun."""

    metadata: Optional[ArgoWorkflowMetadata] = None
    status: Optional[ArgoWorkflowStatus] = None
    spec: Optional[dict] = {}
    jobs: Optional[List[JobRun]] = []

    def find_node(self, _id):
        for node in self.status.nodes:
            if node.id == _id:
                return node

    def find_node_by_name(self, name):
        for node in self.status.nodes:
            if node.name == name:
                return node

    @classmethod
    def is_retry_node(cls, name):
        retry_suffix_pattern = re.compile(r"\(\d+\)$")
        return retry_suffix_pattern.search(name)

    def on_submit_res(self):
        overall_status = JobStatus.SUBMITTED
        message = f"Workflow {self.metadata.name} created at {self.metadata.creation_timestamp}"
        started_at = None
        finished_at = None
        return overall_status, message, started_at, finished_at

    def on_get_res(self, is_in_storage: bool):
        message = ""
        started_at = None
        finished_at = None
        if is_in_storage:
            overall_status = JobStatus.COMPLETED
            message = f"Workflow {self.metadata.name} Completed.\n"
        else:
            overall_status = JobStatus.RUNNING
            message = f"Workflow {self.metadata.name} is running.\n"
            if self.status.finished_at:
                overall_status = JobStatus.COMPLETED
                message = f"Workflow {self.metadata.name} is Completed.\n"

        for node in self.status.nodes:
            # Skip retry child nodes like task-name(1)
            if self.is_retry_node(node.name):
                continue

            if "main" in node.template_name:
                started_at = node.started_at
                finished_at = node.finished_at
                message += f"Main Workflow started at {node.started_at}"  #
                message += f", completed at {node.finished_at}.\n" if node.finished_at else " and is running.\n"
                if node.resources_duration:
                    message += f"Resource usage: cpu={node.resources_duration.cpu}, memory={node.resources_duration.memory}.\n"
                continue

            # NOTE: FOR POSSIBLE PHASE STATS FOR ARGO VISIT: https://argo-workflows.readthedocs.io/en/latest/fields/#workflowstatus
            # Phase a simple, high-level summary of where the node is in its lifecycle.
            # Can be used as a state machine. Will be one of these values
            # "Pending", "Running" before the node is completed,
            # or "Succeeded", "Skipped", "Failed", "Error", or "Omitted" as a final state.
            if node.phase.lower() == "error" or node.phase.lower() == "failed":
                overall_status = JobStatus.FAILED
                err_msg = "Unknown Error!"
                if node.message:
                    err_msg = node.message
                message += f"Workflow {self.metadata.name} failed at {node.name} with error: {err_msg}"
                continue
            message += f"Status of Node {node.name}: {node.phase} \n"

        return overall_status, message, started_at, finished_at

    @classmethod
    def populate_from_res(cls: Type[T], res, fields) -> T:
        """
        This method populates ArgoWorkflowRun attributes
        from the response received from getting the
        workflow.
        """
        try:
            res_dict = res if isinstance(res, dict) else res.to_dict()

            init_args: Dict[str, Any] = {}
            if "metadata" in fields:
                init_args["metadata"] = ArgoWorkflowMetadata(**res_dict.get("metadata", {}))
            if "status" in fields:
                status = res_dict.get("status", {})
                if ("nodes" in status) and (isinstance(status["nodes"], dict)):
                    nodes = []
                    for _, v in status["nodes"].items():
                        nodes.append(v)
                    status["nodes"] = nodes
                init_args["status"] = ArgoWorkflowStatus(**status)
            if "spec" in fields:
                init_args["spec"] = res_dict.get("spec", {})

            return cls(**init_args)
        except Exception as e:
            raise ValueError("Could not parse response") from e


######  #######  #####           # ####### ######     ######
#     # #       #     #          # #     # #     #    #     # ###### ###### # #    # # ##### #  ####  #    #  ####
#     # #       #     #          # #     # #     #    #     # #      #      # ##   # #   #   # #    # ##   # #
######  #####   #     #          # #     # ######     #     # #####  #####  # # #  # #   #   # #    # # #  #  ####
#   #   #       #   # #    #     # #     # #     #    #     # #      #      # #  # # #   #   # #    # #  # #      #
#    #  #       #    #     #     # #     # #     #    #     # #      #      # #   ## #   #   # #    # #   ## #    #
#     # #######  #### #     #####  ####### ######     ######  ###### #      # #    # #   #   #  ####  #    #  ####


class GetWorkflowRes(CamelModel):
    """GetWorkflowRes."""

    workflow: Any = None
    is_found: bool = False
    source_type: Optional[WorkflowStoreType] = None


class LocalTemplateConfig(CamelModel):
    config_type: Literal["local"] = "local"
    standalone_base_path: Optional[str] = None


class LocalTaskParams(CamelModel):
    standalone_base_path: Optional[str] = None
    module_path: Optional[str] = None
    module_name: Optional[str] = None
    module_bucket: Optional[str] = None
    module_remote_path: Optional[str] = None
    module_version: Optional[str] = None
    module_run_mode: Optional[str] = None
    module_run_cmd: Optional[Union[str, List[str]]] = None
    working_dir: Optional[str] = None
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    use_tmp_dir: Optional[bool] = True
    flow_template_folder: Optional[str] = None
    template_file_name: str = "setup.yaml"
    ignore_copy_dirs: Optional[List[str]] = ["venv", ".venv", "__pycache__"]


class JobTemplate(CamelModel):
    """JobTemplate is definition of individual job (and not necessarily a task)."""

    custom_id: Optional[str] = None
    name: Optional[str] = None
    module: ModuleResponse
    submit_mode: JobSubmitMode
    inputs: Optional[Union[List[InputJobTemplate], InputJobTemplate]] = None
    dependency: Optional[List[str]] = []
    uploads: Optional[JobUploads] = None
    template_config: Optional[Union[ArgoTemplateConfig, LocalTemplateConfig]] = Field(..., discriminator="config_type")
    resources: Optional[JobResource] = None
    env_vars: Dict = {}
    callbacks: Optional[List[WorkflowCallBack]] = []


class WorkflowRun(CamelModel):
    status: Optional[JobStatus] = None
    message: Optional[str] = ""
    mode: JobSubmitMode
    workflow_id: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    detail: Optional[Union[Dict[str, Any], ArgoWorkflowRun]] = None

    @model_validator(mode="before")
    @classmethod
    def validate_detail(cls, values):
        if isinstance(values, dict) and "detail" in values and "mode" in values:
            detail = values["detail"]
            mode = values["mode"]

            # Convert mode to string for comparison if it's an enum
            mode_str = mode.value if hasattr(mode, "value") else str(mode)

            # Only try to convert to ArgoWorkflowRun for isolated modes (Argo workflows)
            # For local modes, keep detail as dictionary
            if isinstance(detail, dict) and ("isolate" in mode_str.lower()):
                # Check if the detail has a structure that looks like an Argo workflow
                # Argo workflows should have metadata and/or status fields
                has_argo_structure = "metadata" in detail or "status" in detail or "spec" in detail

                if has_argo_structure:
                    try:
                        values["detail"] = ArgoWorkflowRun.model_validate(detail)
                    except Exception as e:
                        # Leave as raw dict if it doesn't match ArgoWorkflowRun
                        print(f"Warning: Some fields missing in ArgoWorkflowRun: {e}")
                # If it doesn't have Argo structure, leave as dict even for isolated modes
        return values

    def on_submit_res(self):
        if "isolate" in self.mode.value:
            self.status, self.message, self.started_at, self.finished_at = self.detail.on_submit_res()
        return self

    def on_get_res(self, is_in_storage):
        if "isolate" in self.mode.value:
            self.status, self.message, self.started_at, self.finished_at = self.detail.on_get_res(is_in_storage)
        return self
