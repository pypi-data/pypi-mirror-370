from beanie import Document

from fa_common.config import get_settings
from fa_common.models import TimeStampedModel
from fa_common.workflow.models import InputJobTemplate, JobTemplate


class WorkflowInputDB(Document, TimeStampedModel):
    """Baseclass for Input parameters and persistent state of a workflow or module. This should be inherited by specific workflow
    implementations such as Landscape+ or Datamosaic see @https://beanie-odm.dev/tutorial/inheritance/"""

    def populate_job_template(self, job_template: JobTemplate):
        """Populate the job template with the input parameters from the model"""

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}workflow_state"
        is_root = True


class WorkflowInputGeneric(WorkflowInputDB):
    inputs: InputJobTemplate = InputJobTemplate()
    """List of FileDB id's that are associated with the workflow"""

    # FIXME when a schema exists as a type add it here
    def validate_schema(self, schema: dict):
        """The intent of this function is validate the generically populated model against a schema defined in the module to test
        it's compatibility as an input into a workflow that uses that module"""
