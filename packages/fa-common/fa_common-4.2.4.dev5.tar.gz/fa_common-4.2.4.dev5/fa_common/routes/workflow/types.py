from typing import Any, Dict, Optional

from fa_common.models import CamelModel
from fa_common.workflow.models import JobTemplate, WorkflowRun


class RequestCallback(CamelModel):
    workflow_id: Optional[str] = None
    metadata: Optional[Dict[str, Any] | str] = None
    template: Optional[JobTemplate] = None
    message: Optional[str] = None
    background_task_id: Optional[int] = None


class ResponseWorkflow(CamelModel):
    workflow: WorkflowRun | None = None
    background_task_id: Optional[int] = None
    message: Optional[str] = None
