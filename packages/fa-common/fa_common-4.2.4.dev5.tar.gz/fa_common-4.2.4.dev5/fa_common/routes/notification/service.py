import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from fa_common import logger
from fa_common.config import get_settings
from fa_common.routes.notification.enums import EmailBodyType
from fa_common.routes.notification.models import Attachment, CallbackMetaData
from fa_common.routes.workflow import service
from fa_common.workflow.enums import JobStatus


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    body_type: EmailBodyType = EmailBodyType.PLAIN,
    attachments: Optional[List[Attachment]] = None,
):
    settings = get_settings()

    if None in [settings.SENDER_EMAIL, settings.SMTP_SERVER, settings.SMTP_PORT, settings.SMTP_USER_NAME, settings.SMTP_USER_PWD]:
        logger.error("❌ Missing SMTP settings. Skipping sending an email.")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SENDER_EMAIL  # type: ignore
    msg["To"] = to_email  # type: ignore
    msg["Subject"] = subject
    if body_type == EmailBodyType.PLAIN:
        msg.attach(MIMEText(body, "plain"))
    else:
        msg.attach(MIMEText(body, "html"))

    if attachments:
        for a in attachments:
            try:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(a.content.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{a.filename}"')
                msg.attach(part)
            except Exception as e:
                logger.error(f"❌ Could not attach file {a.filename}: {e}")

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)  # type: ignore
        server.starttls()
        server.login(settings.SMTP_USER_NAME, settings.SMTP_USER_PWD)  # type: ignore
        server.sendmail(settings.SENDER_EMAIL, to_email, msg.as_string())  # type: ignore
        server.quit()
        logger.info(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"❌ Error sending email to {to_email}: {e}")


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != get_settings().MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


def notify(
    router: APIRouter,
    path: str,
    subject: str,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                date_format = "%A, %d %B %Y at %I:%M %p %Z"

                result = await func(*args, **kwargs)

                payload = kwargs["payload"]  # Expecting payload argument to always be present

                metadata = CallbackMetaData(**payload.get("metadata", {}))
                workflow_id = payload.get("workflow_id", None)
                if metadata.user_email is None:
                    logger.warning("⚠️ No recipient_email found in payload, skipping email.")
                    return

                if workflow_id is None:
                    logger.error("❌ Workflow id was expected in the callback but it is missing. Skipping sending an email.")
                    return

                if metadata.storage_location is None:
                    logger.error("❌ The storage location of the workflow is UNKNOWN. It was expected in the callback but it is missing!")

                workflow = await service.get_workflow(workflow_id=workflow_id, storage_location=metadata.storage_location)

                if workflow is not None:
                    job_successful = workflow.status in [JobStatus.SUCCEEDED, JobStatus.COMPLETED]

                    start_date_string = (
                        datetime.fromisoformat(workflow.started_at).strftime(date_format) if workflow.started_at is not None else "None"
                    )
                    finish_date_string = (
                        datetime.fromisoformat(workflow.finished_at).strftime(date_format) if workflow.finished_at is not None else "None"
                    )

                    logger.info(f"Workflow successfully retrieved: {workflow.workflow_id} - {workflow.status}")

                    status_icon = "✅"
                    status_str = JobStatus.FAILED.value if not job_successful else "COMPLETED"

                    if not job_successful:
                        status_icon = "❌"

                    if metadata.project_name:
                        stat_msg = f"The workflow for project '{metadata.project_name}'"
                    else:
                        stat_msg = f"The workflow '{workflow.workflow_id}'"

                    stat_msg = (
                        stat_msg
                        + f" submitted '{start_date_string}' has finished '{finish_date_string}' with status: "
                        + f"{status_icon} {workflow.status.value if workflow.status is not None else 'None'}.<br><br>"
                    )

                    final_subject = f"[{status_str}] {subject} - {metadata.project_name}"

                    summary_msg = f"""
                    Summary<br>
                    <hr>
                    <table>
                        <tr>
                            <td>Started:</td>
                            <td>{start_date_string}</td>
                        </tr>
                        <tr>
                            <td>Finished:</td>
                            <td>{finish_date_string}</td>
                        </tr>
                        <tr>
                            <td>Status:</td>
                            <td>{status_icon} {workflow.status.value if workflow.status is not None else "None"}</td>
                        </tr>
                        <tr>
                            <td>Project ID:</td>
                            <td>{metadata.project_id}</td>
                        </tr>
                        <tr>
                            <td>Workflow ID:</td>
                            <td>{workflow_id}</td>
                        </tr>
                        <tr>
                            <td>Storage Location</td>
                            <td>{metadata.storage_location}</td>
                        </tr>
                        <tr>
                            <td>Message:</td>
                            <td>{workflow.message}</td>
                        </tr>
                    </table><br><br>
                    """

                    button_link = metadata.ui_res_link if metadata.ui_res_link else payload.get("base_url")

                    if metadata.ui_res_link and metadata.ui_res_append_id:
                        button_link = button_link + workflow_id

                    link_to_res = f"""
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td bgcolor="#00a9ce" style="border-radius: 4px; padding: 10px 20px;">
                                <a href="{button_link}"
                                    target="_blank"
                                    style="
                                    display: inline-block;
                                    font-family: 'Segoe UI', sans-serif;
                                    font-size: 14px;
                                    color: #ffffff;
                                    text-decoration: none;
                                    font-weight: bold;
                                    ">
                                    View Results
                                </a>
                            </td>
                        </tr>
                        </table>
                        """

                    # @TODO: Extract the workflow id or title, and maybe some meta info
                    # such as when it started and when it finished, and specially, the status
                    body_html = f"""
                    <html>
                    <body>
                    Hi {metadata.user_name},<br><br>

                    {stat_msg}
                    {summary_msg if metadata.show_workflow_details else ""}

                    {link_to_res}<br><br>

                    {metadata.success_content.body if metadata.success_content and job_successful else ""}
                    {metadata.failed_content.body if metadata.failed_content and not job_successful else ""}
                    </html>
                    </body>
                    """

                    # send an additional notification to the failed_email to assist with troubleshooting.
                    if metadata.failed_email and not job_successful:
                        support_html = f"""
                            <html>
                            <body>
                            Hi, the workflow submitted by user: {metadata.user_name} ({metadata.user_email}) has failed.
                            <br><br>
                            Details below:<br><br>

                            {stat_msg}
                            {summary_msg}

                            {link_to_res}<br><br>
                            </html>
                            </body>
                            """
                        await send_email(
                            metadata.failed_email,
                            final_subject,
                            support_html,
                            body_type=EmailBodyType.HTML,
                        )

                    await send_email(
                        metadata.user_email,
                        final_subject,
                        body_html,
                        body_type=EmailBodyType.HTML,
                    )
                else:
                    logger.error("❌ Workflow id was expected in the callback but it is missing. Skipping sending an email.")
                    return

                return result
            except Exception as e:
                logger.error(f"❌ Error sending notification email. {e!s}")
                raise e

        # REGISTER CALLBACK ROUTER
        router.add_api_route(path, wrapper, methods=["POST"], dependencies=[Depends(verify_api_key)])
        return wrapper

    return decorator
