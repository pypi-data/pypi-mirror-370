from typing import Any, Optional

from pydantic import ConfigDict

from fa_common.models import CamelModel, StorageLocation

from .enums import EmailBodyType


class ExtraContent(CamelModel):
    type: EmailBodyType = EmailBodyType.PLAIN
    body: str = ""


class CallbackMetaData(CamelModel):
    """
    storage_location: Should contain the base path to
                      where the workflows are stored.
    project_id:       The project id.
    project_name:     Project name, included in email text.
    user_id:          The submitting user's id
    user_email:       Email address of the submitting user
    user_name:        The submitting users name, included in email text
    ui_res_link:      Provide a custom link to the workflow results
    ui_res_append_id  Set to true to append the completed workflow id to the
                      end of the provided result link. ui_res_link value
                      should be constructed to account for this addition.
    success_content:  Extra content to be included when the job is succesful
    failed_email:     Additional email address to send to when the
                      job has failed.
    failed_content:   Extra content to be included when the job has failed.
    workflow_details: More detailed workflow details.  Will always be included
                      when the job has failed.
    """

    storage_location: StorageLocation | None = None
    project_id: Optional[str] = None
    project_name: Optional[str] = ""
    user_id: Optional[str] = ""
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    ui_res_link: Optional[str] = None
    ui_res_append_id: Optional[bool] = False
    success_content: Optional[ExtraContent] = None
    failed_email: Optional[str] = None
    failed_content: Optional[ExtraContent] = None
    show_workflow_details: Optional[bool] = True


class Attachment(CamelModel):
    filename: str
    content: Any

    model_config = ConfigDict(arbitrary_types_allowed=True)
