"""
@REVIEW:
- Below service functions works for both Argo and Gitlab.
- They are moved from gitlab_service.
"""

import json
from io import BytesIO
from typing import List, Union

from fastapi import UploadFile

from fa_common import File, get_settings
from fa_common.enums import WorkflowEnums
from fa_common.exceptions import NotFoundError
from fa_common.models import StorageLocation
from fa_common.storage import get_storage_client

from .models import ArgoNode, JobRun, JobTemplate


class WorkflowService:
    @classmethod
    async def get_job_output(
        cls, storage_location: StorageLocation, workflow_id: Union[int, str], job_id: Union[int, str]
    ) -> Union[dict, List, None]:
        # client = get_workflow_client()
        storage = get_storage_client()
        file_path = f"{storage_location.path_prefix}/{workflow_id}/{job_id}/outputs.json"
        # storage.add_project_base_path(bucket_id, f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/outputs.json")
        file = await storage.get_file(
            storage_location.bucket_name,
            file_path,
        )
        if file is None:
            return None
        return json.load(file)

    @classmethod
    async def get_job_file_refs(
        cls, storage_location: StorageLocation, workflow_id: Union[str, int], job_id: Union[str, int]
    ) -> List[File]:
        storage = get_storage_client()
        folder_path = f"{storage_location.path_prefix}/{workflow_id}/{job_id}/"

        # storage.add_project_base_path(bucket_id, f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/")
        return await storage.list_files(
            storage_location.bucket_name,
            folder_path,
        )

    @classmethod
    async def add_data_to_argo_node(
        cls,
        node: ArgoNode,
        storage_location: StorageLocation,
        workflow_uname: str,
        config_upload_loc: WorkflowEnums.Upload.LocName,
        output: bool = True,
        file_refs: bool = True,
    ) -> JobRun:
        if node.phase == "Succeeded" and node.template_name == WorkflowEnums.Templates.RUN:
            node.set_pod_task_names()
            subfolder = node.pod_name if config_upload_loc == WorkflowEnums.Upload.LocName.POD_NAME else node.task_name

            if file_refs:
                node.files = await cls.get_job_file_refs(storage_location, workflow_uname, subfolder)
            if output and node.output_json is None:
                node.output_json = await cls.get_job_output(storage_location, workflow_uname, subfolder)
        return node

    @classmethod
    def get_workflow_storage_location_from_settings_proj(cls, project_id: str):
        """
        If workflow apis are used in a project, use this to get back the StorageLocation object from
        project settings.
        """
        storage = get_storage_client()
        st = get_settings()
        return StorageLocation(bucket_name=st.BUCKET_NAME, path_prefix=storage.get_standard_workflow_upload_path_project(project_id))

    @classmethod
    def get_workflow_storage_location_from_settings_user(cls, user_id: str):
        """
        If workflow apis are used in a project, use this to get back the StorageLocation object from
        project settings.
        """
        storage = get_storage_client()
        st = get_settings()
        return StorageLocation(bucket_name=st.BUCKET_NAME, path_prefix=storage.get_standard_workflow_upload_path_user(user_id))

    @classmethod
    async def workflow_submission_handle(cls, job_base: JobTemplate, workflow_id: str, workflow_type: WorkflowEnums.Type):
        """
        This method intends to initiate workflow_argo.json in the designated
        folder
        """
        upload_info = job_base.uploads
        stat_io = BytesIO()
        stat_io.write(workflow_id.encode("utf-8"))
        stat_io.seek(0)

        parent_path = upload_info.default_path
        remote_path = "/".join([parent_path, workflow_id]).replace("//", "/")

        filename = "init.argo" if workflow_type == WorkflowEnums.Type.ARGO else "init.local"
        upload_item = UploadFile(filename=filename, file=stat_io)
        await get_storage_client().upload_file(upload_item, upload_info.bucket_name, remote_path)

    @classmethod
    async def get_workflow_type(
        cls,
        workflow_id: str,
        storage_location: StorageLocation,
        **kwargs,
    ) -> WorkflowEnums.Type:
        """
        This function returns the type of workflow, ie: LOCAL or ARGO
        """
        argo_path = f"{storage_location.path_prefix}/{workflow_id}/init.argo"
        local_path = f"{storage_location.path_prefix}/{workflow_id}/init.local"

        storage_client = get_storage_client()

        if await storage_client.file_exists(storage_location.bucket_name, argo_path):
            return WorkflowEnums.Type.ARGO

        if await storage_client.file_exists(storage_location.bucket_name, local_path):
            return WorkflowEnums.Type.LOCAL

        raise NotFoundError(
            f"Could not identify the workflow type for {workflow_id}."
            f"Please ensure init file exists in below path: {storage_location.path_prefix}/{workflow_id}"
        )
