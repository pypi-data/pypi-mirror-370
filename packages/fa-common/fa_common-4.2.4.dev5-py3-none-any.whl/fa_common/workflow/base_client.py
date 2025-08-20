"""
Description: This class is used as base client for workflows.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fa_common.models import StorageLocation

from .models import JobTemplate, WorkflowRun


class WorkflowBaseClient(ABC):
    """Abstract workflow class."""

    @abstractmethod
    async def run_job(self, job_base: JobTemplate, verbose: bool = True) -> WorkflowRun:
        """
        The `run_job` function is an asynchronous function that runs a job in a
        workflow project using a specified module and job data, with options for runner,
        files, synchronization, and upload.

        :param files: The `files` parameter is a list of files that you want to include
        in the job. It can be either a list of `File` objects or a list of lists of `File`
        objects. If a single set of input file exists for the jobs, then use a list. If
        you wish to loop over a set of input files, then use of list of lists, where each
        inner list represent one set of input files.
        """

    @abstractmethod
    async def get_workflow(
        self,
        workflow_id: str,
        storage_location: StorageLocation | None = None,
        output: bool = False,
        file_refs: bool = True,
        namespace: Optional[str] = None,
        verbose: bool = True,
    ) -> WorkflowRun:
        """
        This Python function defines an abstract method `get_workflow` that retrieves
        information about a workflow run.
        """

    @abstractmethod
    async def delete_workflow(self, workflow_id: str, storage_location: StorageLocation, **kwargs) -> bool:
        """
        :param force_data_delete: if True, if workflow does not exist in the records,
        it would yet continue with deletion of artifacts and output data.
        """

    # @abstractmethod
    # async def _delete_workflow_artifacts(self, workflow_id: str, **kwargs):
    #     """This method deletes artifacts of a workflow."""

    @abstractmethod
    async def retry_workflow(self, workflow_id: str, user_id: Optional[str] = None):
        """Retry the workflow."""

    @abstractmethod
    async def get_workflow_log(
        self,
        workflow_id: str,
        storage_location: StorageLocation,
        namespace: str | None = None,
    ) -> dict[Any, Any]:
        """
        This abstract method defines an asynchronous function to retrieve
        the workflow log based on the workflow ID, with optional parameters
        for bucket ID and namespace.
        """
