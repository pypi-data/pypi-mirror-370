from fastapi import FastAPI

from fa_common import get_current_app, get_settings, logger
from fa_common.enums import WorkflowEnums


def setup_workflow(app: FastAPI) -> None:
    settings = get_settings()

    if settings.WORKFLOW_TYPE == WorkflowEnums.Type.ARGO:
        setup_argo(app)
        return

    if settings.WORKFLOW_TYPE == WorkflowEnums.Type.NONE:
        logger.info("Workflow is set to NONE. However, Local Workflows is always accessible!")
        return

    if settings.WORKFLOW_TYPE == WorkflowEnums.Type.LOCAL:
        return

    raise ValueError("WORKFLOW_TYPE Setting is not a valid workflow option.")


def setup_argo(app: FastAPI) -> None:
    """Helper function to setup argo workflows."""
    settings = get_settings()
    if settings.ARGO_TOKEN is not None and settings.ARGO_URL is not None:
        import argo_workflows

        config = argo_workflows.Configuration()
        config.host = settings.ARGO_URL

        argo = argo_workflows.ApiClient(config)
        access_token = f"Bearer {settings.ARGO_TOKEN}"

        argo.set_default_header("Authorization", access_token)

        app.argo_workflow_client = argo

        logger.info("Argo client has been setup")

    else:
        raise ValueError("Insufficient configuration to create argo client need (ARGO_URL and ARGO_TOKEN).")


def get_workflow_client(mode: WorkflowEnums.Type):
    settings = get_settings()

    if mode == WorkflowEnums.Type.ARGO:
        if settings.WORKFLOW_TYPE == WorkflowEnums.Type.ARGO:
            return get_argo_client()

        raise ValueError("Argo workflow is not set for this project, but it was attempted to get its client.")

    if mode == WorkflowEnums.Type.LOCAL:
        from .local_client import LocalWorkflowClient

        return LocalWorkflowClient()

    raise ValueError("Unknown workflow type. Please input mode to either LOCAL or ARGO.")


def get_argo_client():
    """
    Gets instance of ArgoClient for you to make argo workflow calls.
    :return: ArgoClient.
    """
    try:
        app = get_current_app()
        if app.argo_workflow_client is not None:
            from .argo_client import ArgoClient

            logger.info("Trying to create an ArgoClient instance.")
            return ArgoClient()
    except Exception as err:
        raise ValueError("Problem returning Argo client, may not be initialised.") from err
    raise ValueError("Argo client has not been initialised.")
