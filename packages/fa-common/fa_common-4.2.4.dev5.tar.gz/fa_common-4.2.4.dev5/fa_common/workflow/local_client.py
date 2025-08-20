import json
from copy import deepcopy
from typing import Any, List

from prefect.client.schemas import TaskRun

import fa_common.workflow.local_utils as local_utils
from fa_common import logger as LOG
from fa_common.enums import WorkflowEnums
from fa_common.exceptions import NotFoundError, UnImplementedError
from fa_common.models import StorageLocation
from fa_common.storage import get_storage_client

from .base_client import WorkflowBaseClient
from .enums import WorkflowStoreType
from .models import GetWorkflowRes, InputJobTemplate, JobOutputs, JobRun, JobTemplate, PrefectWorkflow, WorkflowRun
from .service import WorkflowService


class LocalWorkflowClient(WorkflowBaseClient):
    """
    Singleton client for interacting with local-workflows.
    Is a wrapper over the existing local-workflows python client to provide specialist functions for
    the Job/Module workflow.

    Please don't use it directly, use `fa_common.workflow.utils.get_workflow_client`.
    """

    __instance = None
    # local_workflow_client = None

    def __new__(cls) -> "LocalWorkflowClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            # app = get_current_app()
            # cls.__instance.local_workflow_client = app.local_workflow_client  # type: ignore
        return cls.__instance

    async def run_job(self, job_base: JobTemplate, verbose: bool = True) -> WorkflowRun:
        if isinstance(job_base.inputs, list):
            jobs = []
            for i, inp in enumerate(job_base.inputs):
                job = deepcopy(job_base)
                job.custom_id = str(i + 1)
                job.name = f"job-{i+1}"
                job.inputs = inp
                jobs.append(job)
        else:
            jobs = [job_base]

        await WorkflowService.workflow_submission_handle(
            job_base=job_base, workflow_id=job_base.custom_id, workflow_type=WorkflowEnums.Type.LOCAL
        )

        _ = local_utils.run_prefect_jobs(jobs, flow_name=job_base.custom_id, ignore_clean_up=False, return_state=True)
        # flow_run_name = f"{job_base.module.name}: {flow_run.id}"

        storage_location = StorageLocation(
            bucket_name=job_base.uploads.bucket_name,
            path_prefix=job_base.uploads.default_path,
        )

        return await self.get_workflow(workflow_id=job_base.custom_id, storage_location=storage_location)

    async def get_workflow(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        output: bool = False,
        file_refs: bool = True,
        verbose: bool = True,
        **kwargs,
    ) -> WorkflowRun:
        """
        This Python function defines an abstract method `get_workflow` that retrieves
        information about a workflow run.
        """
        res = await self._get_workflow_only(workflow_id, storage_location)
        if res.is_found:
            if not verbose:
                res.workflow.detail = None
            return res.workflow
        return None

    async def _get_workflow_only(self, workflow_id: str, storage_location: StorageLocation) -> GetWorkflowRes:
        workflow = None
        is_in_storage = False
        # CHECK in Storage
        storage = get_storage_client()
        file_path = f"{storage_location.path_prefix}/{workflow_id}/workflow_local.json"
        try:
            workflow_file = await storage.get_file(storage_location.bucket_name, file_path)
            flow_run_dict = json.loads(workflow_file.read().decode("utf-8"))
            workflow = PrefectWorkflow(flow_run_dict=flow_run_dict)

            # flow_run = local_utils.flow_run_dict_to_obj(flow_run_dict)
            is_in_storage = True
        except Exception as _:
            LOG.info(f"Workflow {workflow_id} does not exist in storage.")

        if not is_in_storage:
            LOG.info(f"Checking {workflow_id} in running workflows.")
            workflow = await local_utils.get_flow_runs_plus_tasks_by_name(flow_name=workflow_id)

        if workflow.flow_run is None:
            raise NotFoundError(f"Workflow {workflow_id} not found!")

        job_temp = workflow.flow_run.parameters.get("jobs")[0]
        job_base = JobTemplate(**job_temp)

        workflow_run = WorkflowRun(
            created_at=workflow.flow_run.created.isoformat() if workflow.flow_run.created else None,
            started_at=workflow.flow_run.start_time.isoformat() if workflow.flow_run.start_time else None,
            finished_at=workflow.flow_run.end_time.isoformat() if workflow.flow_run.end_time else None,
            workflow_id=str(workflow.flow_run.name),
            mode=job_base.submit_mode,
            message=workflow.flow_run.state.message,
            status=workflow.flow_run.state.type.value,
            detail=workflow.to_dict(),
        )

        return GetWorkflowRes(
            workflow=workflow_run, is_found=True, source_type=WorkflowStoreType.STORAGE if is_in_storage else WorkflowStoreType.LIVE
        )

    async def _prepare_job(self, workflow_id: str, storage_location: StorageLocation, **kwargs):
        """
        Prepars the jobs with their outputs.
        """
        output = kwargs.get("output", False)
        file_refs = kwargs.get("file_refs", False)
        include_inputs = kwargs.get("include_inputs", False)
        include_logs = kwargs.get("include_logs", False)
        job_id = kwargs.get("job_id", None)

        # VALIDATION CHECKS
        workflow = await self.get_workflow(workflow_id, storage_location, verbose=True)
        if workflow is None:
            raise NotFoundError(f"Workflow {workflow_id} not found!")

        workflow_run = PrefectWorkflow(flow_run_dict=workflow.detail)

        jobs = workflow_run.flow_run.parameters.get("jobs")
        job_ids = [x.get("name", None) for x in jobs]

        if job_id is not None and job_id not in job_ids:
            raise NotFoundError(f"Job {job_id} does not exist in workflow {workflow_id}!")

        # If getting only one job, reduce the list of job_ids to that one job.
        # Otherwise, get all jobs.
        flt_jobs = list(filter(lambda x: x.get("name") == job_id, jobs)) if job_id else jobs

        # MAPPING TASKS INTO DICT FOR EASIER SEARCH
        tasks = {}
        for task in workflow_run.task_runs:
            tasks[task.name] = task

        # GET WORKFLOW LOGS IF REQUIRED
        if include_logs:
            logs = await self.get_workflow_log(workflow_id, storage_location)

        lst_job_runs = []
        for job in flt_jobs:
            task: TaskRun = tasks[job.get("name")]
            inp = None
            file_refs_rec = None
            output_json = None
            log = None

            job_id = job.get("name")

            if include_inputs:
                inp = InputJobTemplate(**job.get("inputs", None))
            if file_refs:
                file_refs_rec = await WorkflowService.get_job_file_refs(storage_location, workflow_id, job_id)
            if output:
                output_json = await WorkflowService.get_job_output(storage_location, workflow_id, job_id)
            if include_logs:
                log = logs[task.name]

            lst_job_runs.append(
                JobRun(
                    job_id=job_id,
                    workflow_id=workflow_id,
                    inputs=inp,
                    outputs=JobOutputs(
                        files=file_refs_rec,
                        out_json=output_json,
                    ),
                    started_at=task.start_time.isoformat(),
                    finished_at=task.end_time.isoformat(),
                    duration=task.total_run_time.total_seconds(),
                    status=str(task.state.type.value),
                    log=log,
                )
            )

        return lst_job_runs

    async def get_list_of_jobs(self, workflow_id: str, storage_location: StorageLocation, **kwargs):
        workflow = await self.get_workflow(workflow_id, storage_location, verbose=True)
        if workflow is None:
            raise NotFoundError(f"Workflow {workflow_id} not found!")

        workflow_run = PrefectWorkflow(flow_run_dict=workflow.detail)

        jobs = workflow_run.flow_run.parameters.get("jobs")
        return [x.get("name", None) for x in jobs]

    async def get_all_jobs(self, workflow_id: str, storage_location: StorageLocation, **kwargs) -> List[JobRun]:
        """
        Get jobs of a workflow
        """
        output = kwargs.get("output", False)
        file_refs = kwargs.get("file_refs", False)
        include_inputs = kwargs.get("include_inputs", False)
        include_logs = kwargs.get("include_logs", False)

        return await self._prepare_job(
            workflow_id,
            storage_location,
            output=output,
            file_refs=file_refs,
            include_inputs=include_inputs,
            include_logs=include_logs,
            job_id=None,
        )

    async def get_job(self, workflow_id: str, job_id: str, storage_location: StorageLocation, **kwargs):  # -> JobRun:
        """
        Get jobs of a workflow
        """
        output = kwargs.get("output", False)
        file_refs = kwargs.get("file_refs", False)
        include_inputs = kwargs.get("include_inputs", False)
        include_logs = kwargs.get("include_logs", False)

        job_runs = await self._prepare_job(
            workflow_id,
            storage_location,
            output=output,
            file_refs=file_refs,
            include_inputs=include_inputs,
            include_logs=include_logs,
            job_id=job_id,
        )

        return job_runs[0]

    async def cancel_workflow(self, workflow_id: str) -> bool:
        try:
            flow_run = await local_utils.get_flow_runs_by_name(workflow_id)
            await local_utils.cancel_flow_run_by_id(flow_run.id)
            return True
        except Exception as e:
            LOG.error(f"An error occured when trying to cancel workflow from prefect server: " f"{workflow_id}: {e}")
            return False

    async def delete_workflow(self, workflow_id: str, storage_location: StorageLocation, **kwargs) -> bool:
        """
        :param force_data_delete: if True, if workflow does not exist in the records,
        it would yet continue with deletion of artifacts and output data.
        """

        try:
            LOG.info(f"Deleting workflow: {workflow_id} from prefect server.")
            flow_run = await local_utils.get_flow_runs_by_name(workflow_id)
            await local_utils.delete_flow_run_by_id(flow_run.id)
        except Exception as e:
            LOG.warning(f"An error occured when trying to delete workflow from prefect server: " f"{workflow_id}: {e}")

        try:
            LOG.info(f"Deleting all output files and data related to workflow: " f"{workflow_id} from data storage.")
            storage = get_storage_client()
            folder_path = f"{storage_location.path_prefix}/{workflow_id}"
            # storage.add_project_base_path(bucket_id, f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}")
            LOG.info(f"folder_path: {folder_path}")
            await storage.delete_file(storage_location.bucket_name, folder_path, True)
        except Exception as e:
            LOG.warning(f"An error occured when trying to delete output data of workflow: " f"{workflow_id}: {e}")
            return False

        return True

    async def retry_workflow(self, workflow_id: str):
        """Retry the workflow."""
        # FixME: Retry not working
        raise UnImplementedError("The current retry function not working.")
        LOG.info(f"Retrying workflow: {workflow_id}.")
        flow_run = await local_utils.get_flow_runs_by_name(workflow_id)
        if flow_run is not None:
            await local_utils.retry_flow_run_by_id(flow_run.id)
            return
        raise NotFoundError(f"Workflow {workflow_id} was not found in Prefect Server.")

    async def retry_job(self, workflow_id: str, job_id: str):
        """
        Knowing workflow_id, job_id -> extract task_run_id
        Check if task_run_id exist.
        If so, retry the job.
        If not -> what to do?
        """
        raise UnImplementedError("To be implemented.")

    async def cancel_job(self, workflow_id: str, job_id: str):
        raise UnImplementedError("To be implemented.")

    async def get_workflow_log(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        **kwargs,
    ) -> dict[Any, Any]:
        """
        This abstract method defines an asynchronous function to retrieve
        the workflow log based on the workflow ID, with optional parameters
        for bucket ID and namespace.
        """
        storage = get_storage_client()
        file_path = f"{storage_location.path_prefix}/{workflow_id}/workflow_logs.json"
        try:
            workflow_file = await storage.get_file(storage_location.bucket_name, file_path)
            return json.loads(workflow_file.read().decode("utf-8"))
        except Exception as _:
            LOG.info(f"Workflow logs for {workflow_id} does not exist in storage.")

        LOG.info(f"Checking {workflow_id} in running workflows.")
        flow_run = await local_utils.get_flow_runs_by_name(flow_name=workflow_id)

        if flow_run is None:
            raise NotFoundError(f"Workflow {workflow_id} not found!")

        flow_logs_raw = await local_utils.get_flow_logs_by_id(flow_run.id)
        return await local_utils.format_flow_run_logs(flow_run, flow_logs_raw)
