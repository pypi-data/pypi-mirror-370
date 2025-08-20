import uuid
from datetime import datetime
from typing import List, Optional

import httpx
import pytz
from fastapi import BackgroundTasks
from prefect.client.schemas import FlowRun as PrefectFlowRun

from fa_common import get_logger
from fa_common.config import get_settings
from fa_common.enums import WorkflowEnums
from fa_common.exceptions import BadRequestError, UnImplementedError
from fa_common.models import StorageLocation
from fa_common.routes.modules.models import ModuleDocument
from fa_common.routes.modules.types import ModuleVersion
from fa_common.routes.project.service import get_project_for_user
from fa_common.routes.user.models import UserDB
from fa_common.workflow.argo_client import ArgoClient
from fa_common.workflow.enums import JobSubmitMode
from fa_common.workflow.local_client import LocalWorkflowClient
from fa_common.workflow.models import JobTemplate, WorkflowCallBack, WorkflowRun
from fa_common.workflow.service import WorkflowService
from fa_common.workflow.utils import get_workflow_client

from .types import RequestCallback

logger = get_logger()


def generate_unique_flow_name() -> str:
    timestamp = datetime.now(pytz.utc).strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]  # Shorten UUID for readability
    return f"{timestamp}_{unique_id}"


async def run_workflow(background_tasks: BackgroundTasks, job: JobTemplate, in_background: bool) -> WorkflowRun:
    module_name = job.module.name
    module_ver = job.module.version
    if isinstance(module_ver, ModuleVersion):
        module_ver = module_ver.name

    job.module = await ModuleDocument.get_version(module_name, module_ver)

    if job.submit_mode in (JobSubmitMode.LOCAL, JobSubmitMode.ISOLATED_LOCAL) and in_background:
        workflow_client: LocalWorkflowClient = get_workflow_client(mode=WorkflowEnums.Type.LOCAL)  # type: ignore
        job.custom_id = generate_unique_flow_name()
        background_tasks.add_task(run_local_job_in_background, job, workflow_client)  # type: ignore

        return WorkflowRun(
            workflow_id=job.custom_id,
            mode=job.submit_mode,
            message="Local Job started in background.",
            detail=None,  # , template=job),
        )

    if job.submit_mode == JobSubmitMode.ISOLATED:
        workflow_client: ArgoClient = get_workflow_client(mode=WorkflowEnums.Type.ARGO)
    elif job.submit_mode in (JobSubmitMode.LOCAL, JobSubmitMode.ISOLATED_LOCAL):
        workflow_client: LocalWorkflowClient = get_workflow_client(mode=WorkflowEnums.Type.LOCAL)  # type: ignore
        job.custom_id = generate_unique_flow_name()
    else:
        raise BadRequestError(f"Unknown submit mode: {job.submit_mode}")

    res: WorkflowRun = await workflow_client.run_job(job_base=job)
    return res


async def get_workflow(
    workflow_id: str,
    storage_location: StorageLocation | None = None,
    output: bool = False,
    file_refs: bool = False,
    namespace: Optional[str] = None,
    verbose: bool = False,
) -> WorkflowRun:
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.get_workflow(
        storage_location=storage_location, workflow_id=workflow_id, output=output, file_refs=file_refs, namespace=namespace, verbose=verbose
    )


async def get_workflow_log(
    workflow_id: str,
    storage_location: StorageLocation,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.get_workflow_log(
        workflow_id=workflow_id,
        storage_location=storage_location,
        namespace=namespace,
    )


async def delete_workflow(
    workflow_id: str,
    storage_location: StorageLocation,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.delete_workflow(
        workflow_id=workflow_id,
        storage_location=storage_location,
        namespace=namespace,
        force_data_delete=True,
    )


async def callback(items: List[WorkflowCallBack], result: PrefectFlowRun):
    for item in items:
        headers = {"x-api-key": item.api_key} if item.api_key else {}
        # workflow_json = json.dumps(result.model_dump(), cls=CustomJSONEncoder)
        data = RequestCallback(workflow_id=result.workflow_id, metadata=item.metadata, message="Local Job completed!")
        async with httpx.AsyncClient() as client:
            await client.post(item.url, json=data.model_dump(), headers=headers)


async def run_local_job_in_background(job: JobTemplate, workflow_client: LocalWorkflowClient):
    # logger.info(f"Starting background job for job ID: {id(job)}")
    try:
        result = await workflow_client.run_job(job_base=job)
        logger.info(f"Workflow {result.workflow_id} completed!")
        if job.callbacks:
            await callback(items=job.callbacks, result=result)
            logger.info("Callback has been executed successfully.")
    except Exception as e:
        logger.error(f"Error occurred: {e!s}")
        raise


async def validate_workflow_params(
    current_user: UserDB, workflow_id: str, project_id: Optional[str] = None
) -> tuple[StorageLocation, str | None, WorkflowEnums.Type]:
    """Gets the correct storage location, namespace, and mode for the workflow or raises an error if user/project is invalid.

    Parameters
    ----------
    current_user : UserDB
        _description_
    project_id : Optional[str], optional
        _description_, by default None
    mode : WorkflowEnums.Type | None, optional
        _description_, by default None

    Returns
    -------
    tuple[StorageLocation, str | None, WorkflowEnums.Type]
        _description_

    Raises
    ------
    BadRequestError
        _description_
    """
    # @NOTE: updated this method. Now mode should be automatically recognised based on
    # the workflow that is ran.

    settings = get_settings()
    # mode = mode if mode is not None else settings.WORKFLOW_TYPE
    # if mode is None:
    #     raise BadRequestError("A default workflow mode is not set in the settings and none was provided.")
    namespace = settings.ARGO_NAMESPACE

    if project_id is not None:
        project = await get_project_for_user(current_user, project_id)  # noqa
        storage_location = WorkflowService.get_workflow_storage_location_from_settings_proj(project_id)
    else:
        storage_location = WorkflowService.get_workflow_storage_location_from_settings_user(current_user.sub)

    return storage_location, namespace


async def get_job_list(
    workflow_id: str,
    storage_location: StorageLocation,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.get_list_of_jobs(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace)


async def get_all_jobs(
    workflow_id: str,
    storage_location: StorageLocation,
    output: bool = False,
    file_refs: bool = False,
    include_inputs: bool = False,
    include_logs: bool = False,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.get_all_jobs(
        workflow_id=workflow_id,
        storage_location=storage_location,
        output=output,
        file_refs=file_refs,
        include_inputs=include_inputs,
        include_logs=include_logs,
        namespace=namespace,
    )


async def get_job(
    workflow_id: str,
    storage_location: StorageLocation,
    job_id: str,
    output: bool = False,
    file_refs: bool = False,
    include_inputs: bool = False,
    include_logs: bool = False,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.get_job(
        workflow_id=workflow_id,
        job_id=job_id,
        storage_location=storage_location,
        output=output,
        file_refs=file_refs,
        include_inputs=include_inputs,
        include_logs=include_logs,
        namespace=namespace,
    )


async def cancel_workflow(
    workflow_id: str,
    storage_location: StorageLocation,
    namespace: Optional[str] = None,
):
    mode = await WorkflowService.get_workflow_type(workflow_id=workflow_id, storage_location=storage_location)
    if mode == WorkflowEnums.Type.ARGO:
        raise UnImplementedError(
            "Canceling workflows are not available for Argo. Please just use Delete endpoint to cancel an Argo workflow."
        )
    workflow_client = get_workflow_client(mode=mode)
    return await workflow_client.cancel_workflow(workflow_id=workflow_id, namespace=namespace)
