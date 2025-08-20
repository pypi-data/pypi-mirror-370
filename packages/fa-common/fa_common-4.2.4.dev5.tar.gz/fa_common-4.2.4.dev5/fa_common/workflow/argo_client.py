"""
The `ArgoClient` class is a singleton client in Python for interacting with Argo workflows,
providing specialized functions for job/module workflows and handling workflow submissions, runs,
retrievals, logs, and deletions.
"""

import json
from copy import deepcopy
from typing import Dict, List, Optional, Union

import httpx
from argo_workflows import ApiClient
from argo_workflows.api import workflow_service_api
from argo_workflows.exceptions import (
    ApiException,
    ForbiddenException,
    NotFoundException,
)

from fa_common import get_current_app
from fa_common import logger as LOG
from fa_common.enums import WorkflowEnums
from fa_common.exceptions import BadRequestError, NotFoundError
from fa_common.models import StorageLocation
from fa_common.storage import get_storage_client

from .argo_utils import ArgoTemplateGenerator
from .base_client import WorkflowBaseClient
from .enums import JobStatus, JobSubmitMode, WorkflowStoreType
from .models import ArgoNode, ArgoWorkflowRun, GetWorkflowRes, InputJobTemplate, JobOutputs, JobRun, JobTemplate, WorkflowRun
from .service import WorkflowService


class ArgoClient(WorkflowBaseClient):
    """
    Singleton client for interacting with argo-workflows.
    Is a wrapper over the existing argo-workflows python client to provide specialist functions for
    the Job/Module workflow.

    Please don't use it directly, use `fa_common.workflow.utils.get_workflow_client`.
    """

    __instance = None
    argo_workflow_client: ApiClient
    workflow_service: workflow_service_api.WorkflowServiceApi
    template_generator: ArgoTemplateGenerator
    api_headers: dict
    api_url: str

    def __new__(cls) -> "ArgoClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.argo_workflow_client = app.argo_workflow_client  # type: ignore
            cls.__instance.workflow_service = workflow_service_api.WorkflowServiceApi(cls.__instance.argo_workflow_client)
            cls.__instance.template_generator = ArgoTemplateGenerator()
            cls.__instance.api_headers = cls.__instance.argo_workflow_client.default_headers
            cls.__instance.api_url = f"{cls.__instance.argo_workflow_client.configuration.host}/api/v1"
        return cls.__instance

    ######
    #     # #    # #    #
    #     # #    # ##   #
    ######  #    # # #  #
    #   #   #    # #  # #
    #    #  #    # #   ##
    #     #  ####  #    #

    # @retry(times=1, delay=5)

    def _get_job_config(self, job: JobTemplate):
        return job.template_config if job.template_config is not None else self.template_generator.config

    async def submit(self, argo_workflow, namespace: str, verbose: bool = False, verify_ssl=True) -> WorkflowRun:
        """
        This Python async function submits an Argo workflow and handles any ApiException
        that may occur.

        :param argo_workflow: `argo_workflow` is an object representing an Argo workflow
        that will be submitted for execution. It contains the necessary information and
        specifications for the workflow to be executed by the Argo workflow service

        :return: The `submit` method returns an `ArgoWorkflowRun` object that is populated
        with specific fields from the API response. The `ArgoWorkflowRun` object is created
        by calling the `populate_from_res` method with the API response and specifying the
        fields to include in the object.
        """
        try:
            res = await self.api_post(
                route=f"workflows/{namespace}",
                body={"workflow": argo_workflow},
                verify_ssl=verify_ssl,
            )
            # api_response = await force_async(self.workflow_service.create_workflow)(
            #     namespace="cmr-xt-argo",
            #     body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(
            #         workflow=argo_workflow, _check_type=False
            #     ),
            #     _check_return_type=False,
            # )

            if res.status_code == 400:
                raise BadRequestError(res.read())

            detail = ArgoWorkflowRun.populate_from_res(res.json(), fields=["metadata", "status"])  # self.format_workflow_resp(api_response)
            workflow = WorkflowRun(workflow_id=detail.metadata.name, mode=JobSubmitMode.ISOLATED, detail=detail)

            workflow = workflow.on_submit_res()
            if not verbose:
                workflow.detail = None
            return workflow

        except ApiException as err:
            LOG.warning(f"Workflow submission Error caught: {err}")  # , retrying in 5 secs: {err}")
            raise err

    def _get_template(self, job_base: JobTemplate):
        if isinstance(job_base.inputs, list):
            jobs = []
            for i, inp in enumerate(job_base.inputs):
                job = deepcopy(job_base)
                job.custom_id = str(i + 1)
                job.name = f"{job.name}-subjob-{i+1}"
                job.inputs = inp
                jobs.append(job)
        else:
            jobs = [job_base]

        return self.template_generator.create(
            jobs=jobs,
            job_base=job_base,
        )

    async def run_job(self, job_base: JobTemplate, verbose: bool = False) -> WorkflowRun:
        template = self._get_template(job_base=job_base)

        config = self._get_job_config(job_base)

        workflow = await self.submit(template, config.base.namespace, verbose=verbose, verify_ssl=config.base.verify_ssl)

        await WorkflowService.workflow_submission_handle(
            job_base=job_base, workflow_id=workflow.workflow_id, workflow_type=WorkflowEnums.Type.ARGO
        )

        return workflow

        # return template

    async def run_batch_jobs(self, job_base: JobTemplate, jobs: List[JobTemplate]) -> WorkflowRun:
        config = self._get_job_config(job_base)
        template = self.template_generator.create(
            jobs=jobs,
            job_base=job_base,
        )
        return await self.submit(template, config.base.namespace, config.base.verify_ssl)

    async def retry_workflow(self, workflow_id: str, user_id: Optional[str] = None):
        # @TODO: to be implemented
        pass

    async def resubmit(self, storage_location: StorageLocation, workflow_id: str, namespace: str, verify_ssl=True) -> WorkflowRun:
        """Resubmit a workflow again."""
        obj = await self.get_workflow_template(storage_location, workflow_id, namespace)
        template = obj.model_dump(by_alias=True)
        template["metadata"] = {"generateName": obj.metadata.generate_name}
        template["apiVersion"] = "argoproj.io/v1alpha1"
        template["kind"] = "Workflow"

        if "jobs" in template:
            del template["jobs"]

        # return template

        return await self.submit(template, namespace, verify_ssl=verify_ssl)

    """
      #####
     #     # ###### #####
     #       #        #
     #  #### #####    #
     #     # #        #
     #     # #        #
      #####  ######   #

    """

    async def get_workflow(
        self,
        workflow_id: str,
        storage_location: StorageLocation | None = None,
        output: bool = False,
        file_refs: bool = True,
        namespace: Optional[str] = "cmr-xt-argo",
        verbose: bool = False,
    ) -> WorkflowRun:
        """"""

        async def add_outputs(workflow: WorkflowRun):
            if workflow.detail.status is not None and workflow.detail.status.nodes:
                for i, node in enumerate(workflow.detail.status.nodes):
                    workflow.detail.status.nodes[i] = await WorkflowService.add_data_to_argo_node(
                        node,
                        storage_location,
                        workflow.detail.metadata.name,
                        self.template_generator.config.upload.loc_name,
                        output,
                        file_refs,
                    )
            return workflow

        result = await self._get_workflow_only(workflow_id, namespace, storage_location)
        if result.is_found:
            workflow = await add_outputs(result.workflow)
            if not verbose:
                workflow.detail = None
            return workflow

        raise NotFoundError(detail=f"Could not find the workflow: {workflow_id} from namespace: {namespace}")

    async def _prepare_job(
        self,
        workflow: WorkflowRun,
        node: ArgoNode,
        storage_location: StorageLocation,
        include_inputs: bool,
        output: bool,
        file_refs: bool,
        logs,
    ):
        """
        This function gathers all info for a job and returns JobRun object
        """

        # @TODO: The job status should be converted to standard forms. A mapping is required.

        workflow_id = workflow.workflow_id
        inp_job = None
        default_path = None
        custom_path = None
        params = {}
        for p in node.inputs.parameters:
            params[p.name] = p.value

        # Handle Inputs
        if include_inputs:
            if node.inputs.artifacts:
                for node_par in workflow.detail.status.nodes:
                    if node_par.children and node.id in node_par.children:
                        for p in node_par.inputs.parameters:
                            params[p.name] = p.value

            inp_job = InputJobTemplate(
                files=json.loads(params.get("files-json")) if params.get("files-json") else None,
                parameters=json.loads(params.get("JOB_PARAMETERS")) if params.get("JOB_PARAMETERS") else None,
            )

        # Handle Output locations
        if node.children:
            for child_id in node.children:
                for node_child in workflow.detail.status.nodes:
                    if node_child.id == child_id and node_child.template_name == WorkflowEnums.Templates.UPLOAD:
                        for p in node_child.inputs.parameters:
                            params[p.name] = p.value

        if params.get("upload-base-path") and params.get("upload-base-path") != "":
            default_path = f'{params["upload-base-path"]}/{workflow_id}/{node.pod_name}'
        if params.get("upload-custom-path") and params.get("upload-custom-path") != "":
            custom_path = f'{params["upload-custom-path"]}/{workflow_id}/{node.pod_name}'

        node = await WorkflowService.add_data_to_argo_node(
            node,
            storage_location,
            workflow.detail.metadata.name,
            self.template_generator.config.upload.loc_name,
            output,
            file_refs,
        )

        # @TODO: For status: check also related downloads and uploads
        return JobRun(
            job_id=node.pod_name,
            workflow_id=workflow_id,
            name=node.display_name,
            inputs=inp_job,
            status=node.phase.upper(),  # This requires mapping to enfornce consistent status
            started_at=node.started_at,
            finished_at=node.finished_at,
            outputs=JobOutputs(
                default_path=default_path,
                custom_path=custom_path,  # None for now.
                files=node.files,
                out_json=node.output_json,
            ),
            log=logs.get(node.pod_name) if logs else None,
        )

    def _check_node_run(self, argo_workflow: ArgoWorkflowRun, node: ArgoNode):
        if node.template_name == WorkflowEnums.Templates.RUN and not ArgoWorkflowRun.is_retry_node(node.name):
            # A run node with no retry
            if node.children is None:
                node.set_pod_task_names()
                return node
            else:
                # checking the children
                # and select only those
                # that are retry
                node_retry = None
                for n_id in node.children:
                    n_child = argo_workflow.find_node(n_id)
                    if ArgoWorkflowRun.is_retry_node(n_child.name) and node.name in n_child.name:
                        node_retry = n_child
                        node_retry.parent = node.id

                # if node_retry is None, then it means
                # children are other nodes, e.g. download node
                if node_retry is None:
                    node.set_pod_task_names()
                    return node
                else:
                    node_retry.set_pod_task_names()
                    return node_retry
        return None

    async def get_list_of_jobs(self, workflow_id: str, storage_location: StorageLocation, namespace: str):
        """
        Get list of Job ids.
        """
        workflow = await self.get_workflow(
            workflow_id=workflow_id, storage_location=storage_location, namespace=namespace, file_refs=False, output=False, verbose=True
        )

        lst_jobs = []
        for node in workflow.detail.status.nodes:
            node_run = self._check_node_run(workflow.detail, node)
            if node_run is not None:
                lst_jobs.append(node_run.pod_name)

        return lst_jobs

    async def get_all_jobs(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        namespace: str,
        output: bool = False,
        file_refs: bool = False,
        include_inputs: bool = False,
        include_logs: bool = False,
    ) -> List[JobRun]:
        """
        Get jobs of a workflow
        """
        workflow = await self.get_workflow(
            workflow_id=workflow_id, storage_location=storage_location, namespace=namespace, file_refs=False, output=False, verbose=True
        )

        logs = None
        if include_logs:
            logs = await self.get_workflow_log(workflow_id=workflow_id, storage_location=storage_location, namespace="cmr-xt-argo")

        lst_jobs = []
        for node in workflow.detail.status.nodes:
            node_run = self._check_node_run(workflow.detail, node)
            if node_run is not None:
                node_run.set_pod_task_names()

                job = await self._prepare_job(
                    workflow=workflow,
                    node=node_run,
                    storage_location=storage_location,
                    include_inputs=include_inputs,
                    output=output,
                    file_refs=file_refs,
                    logs=logs,
                )
                lst_jobs.append(job)

        return lst_jobs

    async def get_job(
        self,
        workflow_id: str,
        job_id: str,
        storage_location: StorageLocation,
        namespace: str,
        output: bool = False,
        file_refs: bool = False,
        include_inputs: bool = False,
        include_logs: bool = False,
    ) -> JobRun:
        """
        Get jobs of a workflow
        """
        workflow = await self.get_workflow(
            workflow_id=workflow_id, storage_location=storage_location, namespace=namespace, file_refs=False, output=False, verbose=True
        )

        logs = None
        if include_logs:
            logs = await self.get_workflow_log(workflow_id=workflow_id, storage_location=storage_location, namespace="cmr-xt-argo")

        for node in workflow.detail.status.nodes:
            if node.template_name == WorkflowEnums.Templates.RUN:
                node.set_pod_task_names()
                if node.pod_name == job_id:
                    return await self._prepare_job(
                        workflow=workflow,
                        node=node,
                        storage_location=storage_location,
                        include_inputs=include_inputs,
                        output=output,
                        file_refs=file_refs,
                        logs=logs,
                    )

        raise NotFoundError(f"Error: Job {job_id} was not found for Workflow {workflow_id}!")

    async def get_workflow_template(
        self,
        storage_location: StorageLocation,
        workflow_id: str,
        namespace: str,
    ):
        raw_result = await self._get_workflow_only(workflow_id, namespace, storage_location=storage_location, get_raw_results=True)
        # return raw_result
        # is_in_storage is dummy here. We are interested in detail.
        workflow = self._format_workflow_resp(raw_result.workflow, is_in_storage=False, fields=["spec", "metadata"])
        return workflow.detail

    async def get_workflows_all(
        self,
        source: WorkflowStoreType,
        namespace: str,
        storage_location: Optional[StorageLocation] = None,
        has_details: bool = False,
    ) -> Union[List[str], List[WorkflowRun]]:
        """
        This async function retrieves all workflows based on the specified
        parameters and returns either a list of workflow names or a list of
        detailed workflow runs.

        :param source: The `source` parameter is used to specify the type of
        Argo workflow store to retrieve workflows from. It is an enumeration
        type with possible values of `LIVE` or `ARCHIVED`
        :type source: WorkflowStoreType

        :param namespace: The `namespace` parameter in the `get_workflows_all`
        function specifies the namespace in which to search for workflows. In
        Kubernetes, namespaces are used to organize and isolate resources within
        a cluster. In this case, the function will look for workflows specifically
        within the "cmr-xt-argo", defaults to cmr-xt-argo
        :type namespace: str (optional)

        :param storage_location: To make workflow functions independent of project set up,
        we pass StorageLocation object.
        :type storage_location: StorageLocation

        :param has_details: The `has_details` parameter is a boolean flag that
        indicates whether additional details should be included in the response for
        each workflow run. If `has_details` is set to `True`, the response will
        include more information about each workflow run. If it is set to `False`,
        the response will only, defaults to False
        :type has_details: bool (optional)
        """

        def format_list_workflows(response, is_in_storage) -> List[ArgoWorkflowRun]:
            if response.status_code != 200:
                raise ApiException(status=response.status_code, reason=response.text)

            if "items" not in response.json():
                raise ApiException(status=response.status_code, reason=response.text)

            if has_details:
                return [self._format_workflow_resp(item, is_in_storage) for item in response.json().get("items", [])]

            return [item.get("metadata").get("name") for item in response.json().get("items", [])]

        if source == WorkflowStoreType.LIVE:
            LOG.info("Getting Live Workflows.")
            return format_list_workflows(await self.api_get(f"workflows/{namespace}"), is_in_storage=False)

        if source == WorkflowStoreType.ARCHIVE:
            LOG.info("Getting Archived Workflows.")
            return format_list_workflows(await self.api_get(f"archived-workflows?namespace={namespace}"), is_in_storage=False)

        if source == WorkflowStoreType.STORAGE:
            if storage_location is None:
                raise ValueError("Storage location must be provided to get workflow from storage.")
            storage = get_storage_client()
            folder_path = storage_location.path_prefix  # storage.get_standard_workflow_upload_path(bucket_id)

            LOG.info("Getting workflows from Storage.")

            workflow_names = await storage.get_immediate_folder_names(storage_location.bucket_name, folder_path)
            if has_details:
                lst_workflows = []
                for name in workflow_names:
                    wrk = await self._get_workflow_only(
                        workflow_id=name,
                        namespace=namespace,
                        storage_location=storage_location,
                    )
                    lst_workflows.append(self._format_workflow_resp(wrk.workflow.model_dump(), is_in_storage=True))

                return lst_workflows
            return workflow_names

        raise ValueError("Unacceptable source type.")

    async def _is_workflow_live(self, workflow_id: str, namespace: str):
        try:
            res = await self._get_workflow_by_store_type(workflow_id, namespace, source=WorkflowStoreType.LIVE)
            LOG.info(f"Workflow: {workflow_id} exists in live records.")
            return True, res
        except Exception as e:
            return False, e

    async def _is_workflow_archived(self, workflow_id: str, namespace: str):
        try:
            res = await self._get_workflow_by_store_type(workflow_id, namespace, source=WorkflowStoreType.ARCHIVE)
            LOG.info(f"Workflow: {workflow_id} exists in archive records.")
            return True, res
        except Exception as e:
            return False, e

    async def _is_workflow_stored(
        self,
        workflow_id: str,
        namespace: str,
        storage_location: StorageLocation,
    ):
        try:
            res = await self._get_workflow_by_store_type(
                workflow_id,
                namespace,
                source=WorkflowStoreType.STORAGE,
                storage_location=storage_location,
            )
            LOG.info(f"Workflow: {workflow_id} exists in storage records.")
            return True, res
        except Exception as e:
            return False, e

    def _format_workflow_resp(self, resp, is_in_storage, fields=["metadata", "status"]):
        resp_dict = resp if isinstance(resp, dict) else resp.json()

        if isinstance(resp_dict, dict):
            if "metadata" in resp_dict:
                detail = ArgoWorkflowRun.populate_from_res(resp_dict, fields)
                workflow = WorkflowRun(workflow_id=detail.metadata.name, mode=JobSubmitMode.ISOLATED, detail=detail)
                return workflow.on_get_res(is_in_storage)

            if "message" in resp_dict:
                raise NotFoundException(reason=resp_dict["message"])

        return resp

    async def _get_workflow_only(
        self,
        workflow_id: str,
        namespace: str,
        storage_location: StorageLocation | None = None,
        get_raw_results: bool = False,
    ) -> GetWorkflowRes:
        """
        This methods goes through all sources where a workflow may be stored, i.e.:
        1. Live Records (mainly applicable when workflow is running)
        2. Archived Records (managed by Argo instance itself, but only lives for 1 week in EASI)
        3. Cloud Storage (Once workflow completed, a json copy of it is stored in the project
        folder.
        The location is project specific and depends on how it is configured.
        )
        """
        for source_type in WorkflowStoreType:
            try:
                res = await self._get_workflow_by_store_type(
                    workflow_id, namespace, source=source_type, get_raw_results=get_raw_results, storage_location=storage_location
                )
                LOG.info(f"Workflow: {workflow_id} exists in {source_type.value} records.")
                return GetWorkflowRes(workflow=res, is_found=True, source_type=source_type)
            except KeyError:
                LOG.info(f"Workflow: {workflow_id} does not exist in {source_type.value} records.")
            except Exception as e:
                LOG.info(f"Workflow: {workflow_id} does not exist in {source_type.value} records." f"Reason: {e}")

                #
        return GetWorkflowRes(workflow=None, is_found=False, source_type=None)

    async def _get_workflow_by_store_type(
        self,
        workflow_id: str,
        namespace: str,
        source: WorkflowStoreType = WorkflowStoreType.LIVE,
        get_raw_results: bool = False,
        storage_location: StorageLocation | None = None,
    ) -> WorkflowRun | Dict:
        """
        :param workflow_id: The id of the completed workflow from which you want to
        fetch log information. int is applicable for gitlab workflows. For argo, is
        either name or uuid.

        :param source: where to get the workflow from. If workflow is running, it
        should get from `workflows` endpoint. In this case, `workflow_id` is the
        workflow's unique name.

        If workflow completed, it should get from `archived-workflows` endpoint. In this case,
        `workflow_id` is the workflow's unique id (uid).

        If workflow is stored in storage (e.g. S3). Then, workflow name is used.

        :param storage_location: Usually, identifies the allocated folder for a specific user within
        a specific project. Unless, project is structured in another way.

        Note: when workflow is running, this parameter is useless as the logs are recieved live.
        """
        resp = None
        is_in_storage = False
        if source == WorkflowStoreType.LIVE:
            resp = await self.api_get(f"workflows/{namespace}/{workflow_id}")

        if source == WorkflowStoreType.ARCHIVE:
            raise NotImplementedError("Archived workflow retrieval is not longer supported.")
        #     resp = await self.api_get(f"archived-workflows/{workflow_id.uid}?namespace={namespace}")

        if source == WorkflowStoreType.STORAGE:
            if storage_location is None:
                raise ValueError("Storage location must be provided to get workflow from storage.")

            is_in_storage = True
            storage = get_storage_client()
            # upload_base_path = storage.get_standard_workflow_upload_path(bucket_id)
            file_path = f"{storage_location.path_prefix}/{workflow_id}/workflow.json"

            workflow_file = await storage.get_file(storage_location.bucket_name, file_path)

            resp = json.loads(workflow_file.read().decode("utf-8"))

        if get_raw_results:
            return resp

        response = self._format_workflow_resp(resp, is_in_storage)
        if response is not None:
            return response

        raise NotFoundError(detail=f"Could not find the workflow: {workflow_id} from namespace: {namespace}")

    #
    #        ####   ####   ####
    #       #    # #    # #
    #       #    # #       ####
    #       #    # #  ###      #
    #       #    # #    # #    #
    #######  ####   ####   ####

    async def get_workflow_log(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        namespace: str | None = None,
    ):
        """This method is used to retrieve logs for a specific workflow."""

        # Check workflow is Live
        is_live, workflow = await self._is_workflow_live(workflow_id, namespace)

        # Get Live
        live_logs = {}
        if is_live and (
            workflow.detail.status.phase.upper() == JobStatus.RUNNING or workflow.detail.status.phase.upper() == JobStatus.PENDING
        ):
            LOG.info("Getting live logs...")
            try:
                res = await self.api_get(f"workflows/{namespace}/{workflow_id}/log?logOptions.container=main")
                live_logs = self._format_live_log(res)
                if isinstance(live_logs, dict):
                    LOG.info(f"Number of logs from Live: {len(live_logs.keys())}")

            except ForbiddenException as ex:
                LOG.error(f"Workflow: {workflow_id} is yet live, but log is not accessible")
                raise ForbiddenException(f"Workflow: {workflow_id} is yet live, but log is not accessible") from ex
            # Handle if it's yet live but not found
        else:
            is_archived, workflow = await self._is_workflow_archived(workflow_id, namespace)
            if not is_archived:
                is_stored, workflow = await self._is_workflow_stored(workflow_id, namespace, storage_location)
                if not is_stored:
                    LOG.error(f"Workflow: {workflow_id} was not found.")
                    raise NotFoundException(f"Workflow: {workflow_id} was not found.")

        # Get from Storage
        storage = get_storage_client()
        stored_logs = {}

        LOG.info("Getting stored log...")
        for node in workflow.detail.status.nodes:
            try:
                if node.type.lower() == "pod" and node.template_name in self.template_generator.config.logs_to_include:
                    node.set_pod_task_names()
                    if node.pod_name not in live_logs:
                        file_path = f"{storage_location.path_prefix}/{workflow_id}/{node.pod_name}/main.log"
                        # file_path = storage.add_project_base_path(
                        #     bucket_id,
                        #     f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id}/{node.pod_name}/main.log",
                        # )
                        log_file = await storage.get_file(storage_location.bucket_name, file_path)
                        if log_file:
                            stored_logs[node.pod_name] = log_file.read().decode("utf-8")
            except ForbiddenException as err:
                LOG.error(f"Was not able to access the log for {node.pod_name} from storage. {err}")

        LOG.info(f"Number of logs from storage: {len(stored_logs.keys())}")
        stored_logs.update(live_logs)
        return stored_logs
        #     return stored_logs
        # except Exception as e:
        #     raise ValueError(f"Was not able to access the log for {node.pod_name} from storage.")

    @classmethod
    def _format_live_log(cls, res):
        try:
            json_objects = res.text.strip().split("\n")
            logs = {}
            for json_obj in json_objects:
                obj = json.loads(json_obj)
                key = obj["result"]["podName"]
                val = obj["result"]["content"]
                if key in logs:
                    logs[key] += val + "\n"
                else:
                    logs[key] = val
            return logs
        except Exception:
            LOG.warning(f"Log is not in the expected format: {res.text}")
            return res.text

    ######
    #     # ###### #      ###### ##### ######
    #     # #      #      #        #   #
    #     # #####  #      #####    #   #####
    #     # #      #      #        #   #
    #     # #      #      #        #   #
    ######  ###### ###### ######   #   ######

    async def delete_workflow(self, workflow_id: str, storage_location: StorageLocation, **kwargs) -> bool:
        """_summary_

        Parameters
        ----------
        workflow_id : str
            _description_
        storage_location : StorageLocation | None, optional
            _description_, by default None
        namespace : str, optional
        force_data_delete : bool, optional
        Returns
        -------
        bool
            _description_
        """

        namespace = kwargs.get("namespace", "cmr-xt-argo")
        # force_data_delete = kwargs.get("force_data_delete", True)

        if await self._delete_workflow_clean_up(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace):
            return await self._delete_workflow_only(workflow_id=workflow_id, storage_location=storage_location, namespace=namespace)
        return False

    async def _delete_workflow_only(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        namespace: str,
    ) -> bool:
        """
        This method only deletes the workflow meta data record. It wouldn't clean up
        the files associated to the workflow.
        """
        # Delete Workflow from LIVE records.
        is_running, _ = await self._is_workflow_live(workflow_id, namespace)
        if is_running:
            try:
                # Using force delete, as most of the time a normal delete does not work!
                await self.api_delete(f"workflows/{namespace}/{workflow_id}?force=true")
                LOG.info(f"Workflow: {workflow_id} deleted from workflows records.")
            except Exception as e:
                LOG.warning(f"Error in deleting workflow: {workflow_id} from workflows records. {e}")

        # Delete Archived Workflow
        is_archived, _ = await self._is_workflow_archived(workflow_id, namespace)
        if is_archived:
            try:
                raise NotImplementedError("Archived workflow deletion is no longer supported.")
                # Using force delete, as most of the time a normal delete does not work!
                # await self.api_delete(f"archived-workflows/{workflow_id.uid}?namespace={namespace}")
                # LOG.info(f"Workflow: {workflow_id} deleted from archived workflow records.")
            except Exception as e:
                LOG.warning(f"Error in deleting workflow: {workflow_id} from archived workflows. {e}")

        # Delete Workflow from STORAGE -@TODO ?
        is_stored, _ = await self._is_workflow_stored(workflow_id, namespace, storage_location)
        if is_stored:
            storage = get_storage_client()
            file_path = f"{storage_location.path_prefix}/{workflow_id}/workflow.json"
            await storage.delete_file(storage_location.bucket_name, file_path, True)

        # Check if workflow yet exist
        # try:
        #     workflow = await self.get_workflow(
        #         workflow_id=workflow_id, storage_location=storage_location, file_refs=False, namespace=namespace
        #     )
        #     # if workflow.metadata.uid == workflow_id.uid:
        #     #     LOG.info(f"Workflow: {workflow_id} still exists in the records after deletion attempts!")
        #     #     return False
        # except Exception:
        #     LOG.info(f"Workflow: {workflow_id} deleted from all records.")
        return True

    async def _delete_workflow_clean_up(
        self, workflow_id: str, storage_location: StorageLocation, namespace: str, verify_ssl: bool = True
    ) -> bool:
        """This methods aims to clean up all files associated with the workflow."""

        # Delete Artifacts
        LOG.info("Initiating deleting artifacts.")
        res_art_del = await self._delete_workflow_artifacts(workflow_id, namespace=namespace, verify_ssl=verify_ssl)
        if res_art_del.detail.metadata.name is None:
            LOG.info(f"An error occured when submitting the workflow to delete " f"the artifacts for workflow: {workflow_id}")
            return False
        else:
            LOG.info(f"Deleting Artifacts successfully submitted for workflow: {workflow_id}.")

        # Delete bucket
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

    async def _delete_workflow_artifacts(self, workflow_id: str, **kwargs):
        """:param workflow_id: is the unique name of the workflow.
        :parm namespace: is the namespace where the workflow is running.
        :param verify_ssl: is a boolean flag to verify ssl or not.
        """
        namespace = kwargs.get("namespace", "cmr-xt-argo")
        verify_ssl = kwargs.get("verify_ssl", True)
        manifest = self.template_generator.delete_workflow_artifacts(workflow_uname=workflow_id)
        return await self.submit(manifest, namespace, verify_ssl)

    ######                             #                #     #
    #     #   ##    ####  ######      # #   #####  #    ##   ## ###### ##### #    #  ####  #####   ####
    #     #  #  #  #      #          #   #  #    # #    # # # # #        #   #    # #    # #    # #
    ######  #    #  ####  #####     #     # #    # #    #  #  # #####    #   ###### #    # #    #  ####
    #     # ######      # #         ####### #####  #    #     # #        #   #    # #    # #    #      #
    #     # #    # #    # #         #     # #      #    #     # #        #   #    # #    # #    # #    #
    ######  #    #  ####  ######    #     # #      #    #     # ######   #   #    #  ####  #####   ####

    def gen_api_endpoint(self, route):
        """Returns back api endpoint for argo."""
        return f"{self.api_url}/{route}"

    async def api_get(self, route, verify_ssl=True):
        """Handles get request to argo's api."""
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.get(self.gen_api_endpoint(route), headers=self.api_headers)

    async def api_delete(self, route, verify_ssl=True):
        """Handles delete request to argo's api."""
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.delete(self.gen_api_endpoint(route), headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.delete(
                self.gen_api_endpoint(route),
            )

    async def api_put(self, route, body={}, verify_ssl=True):
        """Handles update request to argo's api."""
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.put(self.gen_api_endpoint(route), json=body, headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.put(self.gen_api_endpoint(route), json=body)

    async def api_post(self, route, body={}, verify_ssl=True):
        """Handles post request to argo's api."""
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.post(self.gen_api_endpoint(route), json=body, headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.post(self.gen_api_endpoint(route), json=body)
