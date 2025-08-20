from copy import deepcopy
from enum import Enum
from typing import Any, List, Optional

from pydantic import Field, create_model

from fa_common.enums import WorkflowEnums
from fa_common.models import CamelModel, StorageLocation

from .enums import ModuleRunModes, ModuleType, ModuleUsability, ModuleVisibility, UIElementType
from .utils import camel_case_nested, deep_merge, parse_type


class UIElement(CamelModel):
    """
    This class aids in definition of how a parameter should
    be represented at UI level.

    :param: name: The type of element to be used on UI.
    """

    name: UIElementType
    style: Optional[str] = None


class Parameter(CamelModel):
    name: str
    display_name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    ui_element: Optional[UIElement] = None
    group: Optional[str] = None
    display_units: Optional[List[str] | str] = None
    help_tip: Optional[str] = None
    is_required: Optional[bool] = True
    is_categorical: Optional[bool] = False
    value_type: str
    options: Optional[List[Any]] = None
    default_value: Optional[Any] = None
    parameters: Optional[List["Parameter"]] = None


class InputParameterValueConfig(CamelModel):
    class Config:
        extra = "forbid"
        validate_assignment = True
        json_encoders = {Optional[type]: lambda v: v if v is not None else ...}


class ParameterSettings(CamelModel):
    parameters: List[Parameter]

    def create_value_classes(self, parameter_settings: "ParameterSettings", parent_name: str = "InputParameterValue", class_registry=None):
        """
        This method maps the parameter catalogue definition for a run to
        another class identified by `parent_name` that is a pydantic model of
        (field, value type). The output of this method defines the form of
        input job parameters and it can be used for validation purposes.

        Note: Diff between ParameterSettings and output of this method (e.g. InputParameterValue)

        `ParameterSettings`: enables definition of parameter objects in
        a normalized fashion. It provides considerable flexibility to define
        parameters. This definition enables auto population at UI level as well
        as input parameter form for a module.

        `InputParameterValue`: defines the pydantic model of input parameters for
        a module (job). It is populated from ParameterSettings.
        """
        if class_registry is None:
            class_registry = {}

        fields = {}
        for param in parameter_settings.parameters:
            if param.value_type == "object" or param.value_type.startswith("List[object]"):
                nested_class_name = f"{camel_case_nested(param.name)}Value"
                nested_catalogue = ParameterSettings(parameters=param.parameters)
                nested_class = self.create_value_classes(nested_catalogue, nested_class_name, class_registry)
                field_type = List[nested_class] if param.value_type.startswith("List[object]") else nested_class
            else:
                field_type = parse_type(param.value_type)

            if param.options:
                enum_name = f"{camel_case_nested(param.name)}Enum"  # f"{param.name.capitalize()}Enum"
                enum_values = {opt.upper(): opt for opt in param.options}
                enum_type = Enum(enum_name, enum_values)
                field_type = enum_type

            if param.is_required:
                if param.default_value is not None:
                    fields[param.name] = (field_type, Field(default=param.default_value))
                else:
                    fields[param.name] = (field_type, Field(...))
            else:
                if param.default_value is not None:
                    fields[param.name] = (Optional[field_type], Field(default=param.default_value))
                else:
                    fields[param.name] = (Optional[field_type], Field(default=None))

        created_class = create_model(parent_name, __base__=InputParameterValueConfig, **fields)
        class_registry[parent_name] = created_class
        return created_class

    def populate_input_param_vals(self):
        """Populates InputParameterValue"""
        if self:
            class_registry = {}
            self.create_value_classes(self, "InputParameterValue", class_registry)
            return class_registry
            # return class_registry.get('InputParameterValue')
        raise ValueError("Parameter Catalogue is undefined for this run version.")


class RunModule(CamelModel):
    """
    IMPORTANT NOTE:
        At present, `cmd` supports one command for isolated images.

        Attributes:
        -----------
        `runner`: Basically, the path to the executable of the runner. This would be
        relative to the standalone location. Examples
            win-exe:    main.exe
            win-venv:   .venv/Scripts/python.exe
            linux-exe:  main
            linux-venv: .venv/bin/python

        `cmd`:  List of commands to be executed. Note that there is a special placeholder
        to refer to the `runner` within cmd string. To refer to the runner, simply
        use `<<runner>>`. Examples:
            1. runner: main.exe
               cmd:    <<runner>> input/param.json
            2. runner: .venv/bin/python
               cmd: chmod +x <<runner>> && <<runner>> input/param.json

        In both above examples, the code will replace the runner with the allocated placeholders
        in the `cmd` string.
    """

    runner: Optional[str] = None
    cmd: Optional[List[str]] = None
    mode: ModuleRunModes
    input_path: Optional[str] = None
    working_dir: Optional[str] = None
    output_path: Optional[str] = None
    parameter_settings: Optional[ParameterSettings] = None


class JobSecrets(CamelModel):
    name: str
    mount_path: str


class ModuleImage(CamelModel):
    url: str
    run_meta: Optional[RunModule] = None
    image_pull_secrets: Optional[List[str]] = []
    image_pull_policy: Optional[WorkflowEnums.Run.ImagePullPolicy] = WorkflowEnums.Run.ImagePullPolicy.IF_NOT_PRESENT
    env_secrets: Optional[List[str]] = []
    mount_secrets: Optional[List[JobSecrets]] = []
    env_configs: Optional[List[str]] = []


class ModuleRepository(CamelModel):
    bucket: StorageLocation
    run_meta: Optional[RunModule] = None
    use_tmp_dir: bool
    base_image: Optional[str] = None
    ignore_copy: Optional[List[str]] = None


class ModuleMeta(CamelModel):
    """
    Contains Module's metadata.

    A single version could include both a repo_ref and an image_ref.
    Note an image_ref can only be run through argo (or a remote workflow runner).
    While, repo_ref can be run both locally or through a base image that downloads the
    repo ref and runs it in a remote workflow runner (eg. argo).
    """

    visibility: Optional[ModuleVisibility] = None
    usability: Optional[List[ModuleUsability]] = []
    type: Optional[List[ModuleType]] = None
    image_ref: Optional[ModuleImage] = None
    repo_ref: Optional[ModuleRepository] = None


class ModuleVersion(CamelModel):
    name: str
    description: Optional[str] = ""
    module_meta: Optional[ModuleMeta] = None


class Module(CamelModel):
    name: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    versions: Optional[List[ModuleVersion]] = []
    base_version: Optional[ModuleVersion] = None
    # module_meta: Optional[ModuleMeta] = None

    def get_fused_version_meta(self, version_name: str) -> ModuleVersion:
        """
        Retrieves a version by its label and fuses its properties with module-level metadata.

        Parameters:
            version_label (str): The label of the version to retrieve.

        Returns:
            Optional[ModuleVersion]: A new ModuleVersion instance with fused properties,
                                     or None if the version is not found.
        """
        # Find the specified version
        version = next((v for v in self.versions if v.name == version_name), None)
        if not version:
            raise ValueError(f"Version {version_name} was not found!")

        # # Create a new ModuleVersion instance to avoid mutating the original
        # fused_version = ModuleVersion(name=version.name, label=version.labels)

        # Merge version and base_version
        if self.base_version:
            return deep_merge(deepcopy(self.base_version), deepcopy(version))

        return version


class ModuleResponse(CamelModel):
    name: str
    version: str | ModuleVersion


class ModuleListResponse(CamelModel):
    name: str
    description: Optional[str] = ""
    created: str
    tags: Optional[List[str]] = []
    versions: List[str]
    has_base_version: bool = False


class ModuleValidationResponse(CamelModel):
    message: str = ""
    error: Optional[str] = None
    validated: bool = False
