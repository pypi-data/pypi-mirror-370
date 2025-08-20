from typing import Optional

from fastapi import APIRouter, Security
from pydantic import ValidationError

from fa_common import get_settings
from fa_common.auth.utils import get_admin_scope
from fa_common.models import Message
from fa_common.routes.user.models import UserDB
from fa_common.routes.user.service import get_current_app_user
from fa_common.workflow.models import JobTemplate

from .enums import ModuleEntityNames
from .models import ModuleDocument
from .service import gen_module_entity_schemas, get_param_settings
from .types import Module, ModuleValidationResponse, ModuleVersion

router = APIRouter()


@router.get("")
async def get_all_module_names():
    """Gets the names of all available modules."""
    return await ModuleDocument.get_all()
    # return await ModuleService.get_module_list()


@router.get("/schemas/{entity_name}")
async def get_module_schemas_api(entity_name: ModuleEntityNames):
    return gen_module_entity_schemas(entity_name)


@router.post("/schema/validate/{entity_name}", response_model=ModuleValidationResponse)
async def validate_new_module_creation(entity_name: ModuleEntityNames, inputs: dict):
    try:
        if entity_name == ModuleEntityNames.MODULE:
            Module.parse_obj(inputs)
        if entity_name == ModuleEntityNames.MODULE_VERSION:
            ModuleVersion.parse_obj(inputs)
        if entity_name == ModuleEntityNames.JOB_TEMPLATE:
            JobTemplate.parse_obj(inputs)
        return ModuleValidationResponse(message=f"{entity_name.value} entries validated!", validated=True)

    except Exception as e:
        return ModuleValidationResponse(message="Validation Failed", error=str(e), validated=False)


@router.get("/{name}")
async def get_specific_module(name: str):
    """Given the name of the module, it returns its full information."""
    return await ModuleDocument.get(name)


@router.get("/{name}/versions")
async def get_versions_of_a_module(name: str):
    """
    Given the name of the module, it returns back the names of
    all available versions for this module.
    """
    return await ModuleDocument.get_versions(name)


@router.get("/{name}/{version}")
async def get_specific_version_of_a_module(name: str, version: str, fuse: bool = True):
    """
    Given the name of a Module and a specific version of it,
    it will return full information of the version. Note that
    it will fuse the version data with the basic version data
    (priority given to the version data).
    """
    return await ModuleDocument.get_version(name, version, fuse=fuse)


@router.post("")
async def create_new_module(new_module: Module, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])):
    """Creates a new module."""
    return await ModuleDocument.insert_new(new_module)


@router.delete("/{name}")
async def delete_module(name: str, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])) -> Message:
    """Deletes an existing module."""
    return await ModuleDocument.delete_module(name)


@router.put("/overwrite/{name}")
async def overwrite_module(
    name: str, update_module: Module, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Completely overwrites an existing module."""
    return await ModuleDocument.overwrite(curr_name=name, module=update_module)


@router.patch("/{module_name}")
async def update_name_description_module(
    module_name: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()]),
):
    """Updates only name and description of a module."""
    return await ModuleDocument.update_meta(curr_name=module_name, new_name=name, description=description)


@router.put("/{name}/base-version")
async def update_base_version(
    name: str, version: ModuleVersion, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Updates the base version data of the module."""
    return await ModuleDocument.update_base_version(name, version)


@router.put("/{name}/new")
async def add_new_version(
    name: str, version: ModuleVersion, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Adds a new version to the module."""
    return await ModuleDocument.add_new_version(name, version)


@router.put("/{name}/{version_name}")
async def update_module_version(
    name: str, version_name: str, version: ModuleVersion, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Updates a specific version of a module."""
    return await ModuleDocument.update_version(name, version_name, version)


@router.put("/{name}/{version_name}/delete")
async def delete_module_version(
    name: str, version_name: str, current_user: UserDB = Security(get_current_app_user, scopes=[get_admin_scope()])
):
    """Deletes an existing version of a module."""
    return await ModuleDocument.delete_version(name, version_name)


@router.get("/{name}/{version}/params/settings")
async def get_module_param_settings(name: str, version: str, module_bucket_name: Optional[str] = None):
    """
    Gets the settings for a module's parameters and returns schema and uiSchema objects
    that can be used with Json Forms.

    It also returns parameter settings which has additional metadata defined for parameters
    aiding in further tailoring the ui.
    """
    if not module_bucket_name:
        st = get_settings()
        module_bucket_name = st.BUCKET_NAME
    param_settings, _, schema, ui_schema = await get_param_settings(name, version, module_bucket_name)

    return {
        "param_settings": param_settings,
        "schema": schema,
        "uiSchema": ui_schema,
    }


@router.post("/{name}/{version}/params/validate")
async def get_param_catalogue(name: str, version: str, inputs: dict, module_bucket_name: Optional[str] = None):
    """Validates the inputs against the module's parameter definition."""
    if not module_bucket_name:
        st = get_settings()
        module_bucket_name = st.BUCKET_NAME
    _, class_reg, _, _ = await get_param_settings(name, version, module_bucket_name)
    InputParameterValue = class_reg.get("InputParameterValue")
    try:
        InputParameterValue.parse_obj(inputs)
        return {"message": "Inputs validated", "validated": True}
    except ValidationError as e:
        return {"message": f"Validation Failed. detail: {e}", "validated": False}
        # raise BadRequestError(detail=f"Input validation error: {e.errors()}")
