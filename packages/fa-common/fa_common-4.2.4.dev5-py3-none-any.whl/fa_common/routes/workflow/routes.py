from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Path

from fa_common import ErrorResponse, get_logger
from fa_common.models import Message
from fa_common.routes.user.models import UserDB
from fa_common.routes.user.service import get_current_app_user
from fa_common.routes.workflow import service
from fa_common.workflow.models import JobTemplate, WorkflowRun

logger = get_logger()

router = APIRouter()


@router.post("/run", response_model=WorkflowRun)
async def run_workflow(
    background_tasks: BackgroundTasks,
    job: JobTemplate,
    in_background: bool = True,
    current_user: UserDB = Depends(get_current_app_user),
) -> WorkflowRun:
    return await service.run_workflow(background_tasks, job, in_background)


@router.post(
    "/cancel/{workflow_id}",
    responses={
        400: {"description": "Error retrieving workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def cancel_workflow(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    namespace: str | None = None,
    current_user: UserDB = Depends(get_current_app_user),
) -> WorkflowRun:
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )
    return await service.cancel_workflow(workflow_id, storage_location, namespace)


# @router.post("/run/callback")
# async def run_workflow_callback(data: RequestCallback, api_key: str = Depends(service.verify_api_key)):
#     logger.info(f"Run callback received: {data}")
#     return data


def register_callback_endpoint(callback_endpoint, prefix: str = ""):
    """Use this function to implement callback endpoint in the project."""
    router.add_api_route(
        f"{prefix}/run/callback",
        callback_endpoint,
        methods=["POST"],
        # response_model=WorkflowCallbackResponse
    )


# @router.get("")
# async def get_workflow(
#     uid: Optional[str] = None,
#     name: Optional[str] = None,
#     mode: WorkflowEnums.Type = WorkflowEnums.Type.ARGO,
#     bucket_name: Optional[str] = None,
#     bucket_path: Optional[str] = None,
#     output: bool = False,
#     file_refs: bool = False,
#     namespace: Optional[str] = None,
#     current_user: UserDB = Depends(get_current_app_user),
# ):
#     return await service.get_workflow(uid, name, mode, bucket_name, bucket_path, output, file_refs, namespace)


@router.get(
    "/{workflow_id}",
    response_model=WorkflowRun,
    responses={
        400: {"description": "Error retrieving workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def get_workflow(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    output: bool = False,
    file_refs: bool = False,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )
    return await service.get_workflow(
        workflow_id=workflow_id, storage_location=storage_location, output=output, file_refs=file_refs, namespace=namespace
    )


@router.get(
    "/log/{workflow_id}",
    responses={
        200: {"description": "JSON Log from the workflow"},
        400: {"description": "Error accessing workflow logs"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def get_workflow_log(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )
    return await service.get_workflow_log(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace)


# @router.get("/log")
# async def get_workflow_log(
#     uid: Optional[str] = None,
#     name: Optional[str] = None,
#     mode: WorkflowEnums.Type = WorkflowEnums.Type.ARGO,
#     bucket_name: Optional[str] = None,
#     bucket_path: Optional[str] = None,
#     namespace: Optional[str] = None,
#     current_user: UserDB = Depends(get_current_app_user),
# ):
#     return await service.get_workflow_log(uid, name, mode, bucket_name, bucket_path, namespace)


@router.delete(
    "/{workflow_id}",
    response_model=Message,
    responses={
        400: {"description": "Error deleting workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def delete_workflow(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )
    result = await service.delete_workflow(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace)
    if not result:
        return ErrorResponse(code="400", detail=f"Failed to delete workflow {workflow_id}")

    return Message(message=f"Workflow {workflow_id} deleted successfully.")


@router.get(
    "/list-jobs/{workflow_id}",
    responses={
        400: {"description": "Error retrieving workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def get_job_list(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )
    return await service.get_job_list(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace)


@router.get(
    "/jobs/{workflow_id}",
    responses={
        400: {"description": "Error retrieving workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def get_all_jobs(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    output: bool = False,
    file_refs: bool = False,
    include_inputs: bool = False,
    include_logs: bool = False,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )

    return await service.get_all_jobs(
        workflow_id=workflow_id,
        storage_location=storage_location,
        output=output,
        file_refs=file_refs,
        include_inputs=include_inputs,
        include_logs=include_logs,
        namespace=namespace,
    )


@router.get(
    "/job/{workflow_id}/{job_id}",
    responses={
        400: {"description": "Error retrieving workflow"},
        404: {"description": "Project not found"},
        401: {"description": "Unauthorized to access project"},
    },
)
async def get_job(
    workflow_id: Annotated[str, Path(..., description="The primary identifier or unique name of the workflow")],
    project_id: Optional[str] = None,
    job_id: Optional[str] = None,
    output: bool = False,
    file_refs: bool = False,
    include_inputs: bool = False,
    include_logs: bool = False,
    current_user: UserDB = Depends(get_current_app_user),
):
    storage_location, namespace = await service.validate_workflow_params(
        current_user=current_user, workflow_id=workflow_id, project_id=project_id
    )

    return await service.get_job(
        workflow_id=workflow_id,
        job_id=job_id,
        storage_location=storage_location,
        output=output,
        file_refs=file_refs,
        include_inputs=include_inputs,
        include_logs=include_logs,
        namespace=namespace,
    )
