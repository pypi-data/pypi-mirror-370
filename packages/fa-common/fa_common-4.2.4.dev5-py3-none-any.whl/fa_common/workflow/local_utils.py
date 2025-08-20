import asyncio
import contextlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from typing import List
from uuid import UUID

from fastapi import UploadFile
from prefect import flow, get_run_logger, task
from prefect.client.orchestration import get_client
from prefect.client.schemas import FlowRun
from prefect.client.schemas.filters import FlowRunFilter, LogFilter, TaskRunFilter
from prefect.client.schemas.objects import Log
from prefect.runtime import flow_run, task_run
from prefect.states import State, StateType
from prefect.task_runners import ConcurrentTaskRunner

from fa_common.exceptions import JobExecutionError
from fa_common.models import File
from fa_common.routes.modules.enums import ModuleRunModes
from fa_common.storage import get_storage_client
from fa_common.workflow.enums import FileType
from fa_common.workflow.models import JobUploads, LocalTaskParams

from .models import JobTemplate, PrefectWorkflow

dirname = os.path.dirname(__file__)


# Custom JSON encoder to handle UUID and datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, timedelta):
            return str(obj)
        return super().default(obj)


def custom_json_decoder(obj):
    for key, value in obj.items():
        if isinstance(value, str):
            with contextlib.suppress(ValueError):
                obj[key] = datetime.fromisoformat(value)
            with contextlib.suppress(ValueError):
                obj[key] = UUID(value)
        if isinstance(value, list):
            with contextlib.suppress(ValueError):
                obj[key] = set(value)
        if isinstance(value, str) and "days" in value:
            with contextlib.suppress(ValueError):
                obj[key] = timedelta(days=float(value.split()[0]))
    return obj


# ========================================================
#     # ####### #       ######  ####### ######   #####
#     # #       #       #     # #       #     # #     #
#     # #       #       #     # #       #     # #
####### #####   #       ######  #####   ######   #####
#     # #       #       #       #       #   #         #
#     # #       #       #       #       #    #  #     #
#     # ####### ####### #       ####### #     #  #####
# ========================================================
def filter_attributes(obj):
    import inspect
    import uuid
    from collections.abc import Iterable

    def is_simple(value):
        """Check if the value is a simple data type or a collection of simple data types."""
        if isinstance(value, (int, float, str, bool, type(None), uuid.UUID)):
            return True
        if isinstance(value, dict):
            return all(is_simple(k) and is_simple(v) for k, v in value.items())
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return all(is_simple(item) for item in value)
        return False

    result = {}
    for attr in dir(obj):
        # Avoid magic methods and attributes
        if attr.startswith("__") and attr.endswith("__"):
            continue
        value = getattr(obj, attr)
        # Filter out methods and check if the attribute value is simple
        if not callable(value) and not inspect.isclass(value) and is_simple(value):
            result[attr] = value
    return result


# ========================================================
#     # ####### #       ######  ####### ######   #####
#     # #       #       #     # #       #     # #     #
#     # #       #       #     # #       #     # #
####### #####   #       ######  #####   ######   #####
#     # #       #       #       #       #   #         #
#     # #       #       #       #       #    #  #     #
#     # ####### ####### #       ####### #     #  #####
# ========================================================


def delete_directory(dir_path):
    """
    Deletes a directory along with all its contents.

    Args:
    dir_path (str): Path to the directory to be deleted.
    """
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist.")
        return

    try:
        shutil.rmtree(dir_path)
        print(f"Directory {dir_path} has been deleted successfully.")
    except Exception as e:
        print(f"Failed to delete {dir_path}. Reason: {e}")


# from config import ModuleSettings, set_global_settings


def ensure_directories_exist(directories):
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist, creating...")
            os.makedirs(directory, exist_ok=True)  # The exist_ok=True flag prevents raising an error if the directory already exists.
            print(f"Directory {directory} created.")
        else:
            print(f"Directory {directory} already exists.")


def write_storage_files(file_content: BytesIO, target_path: str, filename: str):
    with open(os.path.join(target_path, filename), "wb") as file:
        file_content.seek(0)
        file.write(file_content.read())


def extract_zip_from_bytesio(file_content: BytesIO, target_path: str):
    file_content.seek(0)
    with zipfile.ZipFile(file_content, "r") as zip_ref:
        # Iterate over all the files and directories in the zip file
        for member in zip_ref.namelist():
            # Determine the full local path of the file
            file_path = os.path.normpath(os.path.join(target_path, member))

            # Check if the file has a directory path, if it does, create the directory
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # If the current member is not just a directory
            if not member.endswith("/"):
                # Open the zip file member, create a corresponding local file
                source = zip_ref.open(member)
                with open(file_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                source.close()

    print("Extraction complete.")


def copy_directory(src, dest, ignore_dirs=["venv", ".venv", "__pycache__"]):
    """
    Copies all files and directories from src to dest, ignoring specified directories.

    Args:
    src (str): Source directory path.
    dest (str): Destination directory path.
    ignore_dirs (list): Directories to ignore.
    """
    if not os.path.exists(dest):
        os.makedirs(dest)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            if item not in ignore_dirs:
                copy_directory(s, d, ignore_dirs)
        else:
            shutil.copy2(s, d)


"""
 #######                         ######                   #######
 #       #       ####  #    #    #     # #    # #    #    #     # #####  #####  ####
 #       #      #    # #    #    #     # #    # ##   #    #     # #    #   #   #
 #####   #      #    # #    #    ######  #    # # #  #    #     # #    #   #    ####
 #       #      #    # # ## #    #   #   #    # #  # #    #     # #####    #        #
 #       #      #    # ##  ##    #    #  #    # #   ##    #     # #        #   #    #
 #       ######  ####  #    #    #     #  ####  #    #    ####### #        #    ####

"""


async def get_flow_run_by_id(flow_run_id):
    """
    Fetch flow run by providing its id
    """
    async with get_client() as client:
        return await client.read_flow_run(
            flow_run_id=flow_run_id,
        )


async def get_flow_runs_by_name(flow_name: str, limit: int = 1) -> FlowRun:
    """
    Fetch flow runs for a specific flow name, sorted by start time (most recent first).
    """
    async with get_client() as client:
        flow_filter = FlowRunFilter(name={"any_": [flow_name]})
        flow_runs = await client.read_flow_runs(
            flow_run_filter=flow_filter,
            limit=limit,
        )

        if flow_runs:
            return flow_runs[0]

        return None


async def get_flow_runs_plus_tasks_by_name(flow_name: str):
    flow_run_stat = await get_flow_runs_by_name(flow_name)
    if flow_run_stat is not None:
        task_run_stats = await get_task_runs_by_flow_run_id(flow_run_stat.id)
        return PrefectWorkflow(flow_run=flow_run_stat, task_runs=task_run_stats)

    return PrefectWorkflow()


async def get_flow_runs_plus_tasks_by_id(flow_id: str):
    flow_run_stat = await get_flow_run_by_id(flow_id)
    task_run_stats = await get_task_runs_by_flow_run_id(flow_id)
    return PrefectWorkflow(flow_run=flow_run_stat, task_runs=task_run_stats)


async def get_flow_logs_by_id(flow_run_id):
    async with get_client() as client:
        return await client.read_logs(log_filter=LogFilter(flow_run_id={"any_": [flow_run_id]}))

        # log_entries = [
        #     {"timestamp": log.timestamp, "level": log.level, "message": log.message}
        #     for log in logs
        # ]
        # return {"flow_run_id": flow_run_item.id, "logs": log_entries}


async def get_flow_logs_by_name(flow_name: str):
    """
    Fetch flow run logs by flow name. Assuming flow_name is unique.
    """
    flow_run_item = await get_flow_runs_by_name(flow_name, limit=1)
    return await get_flow_logs_by_id(flow_run_item.id)


async def get_task_logs_by_id(task_run_id):
    async with get_client() as client:
        return await client.read_logs(log_filter=LogFilter(task_run_id={"any_": [task_run_id]}))


async def get_task_run_name(task_run_id):
    async with get_client() as client:
        task_run = await client.read_task_run(task_run_id)
        return task_run.name


async def get_task_runs_by_flow_run_id(flow_run_id):
    async with get_client() as client:
        task_runs = await client.read_task_runs(task_run_filter=TaskRunFilter(flow_run_id={"any_": [flow_run_id]}))
        return task_runs


async def get_flow_status_by_name(flow_name: str):
    """
    Fetch flow run status by flow name. Assuming flow_name is unique.
    """
    flow_run_item = await get_flow_runs_by_name(flow_name, limit=1)
    return {"flow_run_id": flow_run_item.id, "status": flow_run_item.state.name}


def flow_run_to_json(workflow: PrefectWorkflow):
    # flow_run_dict = flow_run_stat.dict()
    # if task_run_stats:
    #     flow_run_dict['task_runs'] = [task_run_stat.dict() for task_run_stat in task_run_stats]
    return json.dumps(workflow.to_dict(), cls=CustomJSONEncoder).encode("utf-8")


def flow_run_dict_to_obj(flow_run_dict: dict) -> FlowRun:
    return FlowRun(**flow_run_dict)


async def cancel_flow_run_by_id(flow_run_id):
    async with get_client() as client:
        cancelling_state = State(type=StateType.CANCELLING)
        await client.set_flow_run_state(flow_run_id=flow_run_id, state=cancelling_state)


async def delete_flow_run_by_id(flow_run_id):
    async with get_client() as client:
        await client.delete_flow_run(flow_run_id)


async def retry_task_run_by_id(task_run_id):
    async with get_client() as client:
        retrying_state = State(type=StateType.PENDING)
        await client.set_task_run_state(task_run_id=task_run_id, state=retrying_state)


async def retry_flow_run_by_id(flow_run_id):
    async with get_client() as client:
        retrying_state = State(type=StateType.PENDING)
        await client.set_flow_run_state(flow_run_id=flow_run_id, state=retrying_state)


"""
  #####  #     # ######     #######    #     #####  #    #  #####
 #     # #     # #     #       #      # #   #     # #   #  #     #
 #       #     # #     #       #     #   #  #       #  #   #
  #####  #     # ######        #    #     #  #####  ###     #####
       # #     # #     #       #    #######       # #  #         #
 #     # #     # #     #       #    #     # #     # #   #  #     #
  #####   #####  ######        #    #     #  #####  #    #  #####

"""


async def init_working_directory(info: LocalTaskParams):
    logger = get_run_logger()
    module_runner = f"{info.module_path}/{info.module_version}"
    copy_directory(module_runner, info.working_dir, info.ignore_copy_dirs)

    logger.info(info.working_dir)
    chk_dirs = [
        info.working_dir,
        os.path.join(info.working_dir, info.input_path),
        os.path.join(info.working_dir, info.output_path),
    ]
    ensure_directories_exist(chk_dirs)


async def download_files(work_dir, sub_dir, files: List[File]):
    """
    The function `download_files` downloads files from a storage client and writes them to a specified
    directory.

    :param work_dir: The `work_dir` parameter represents the directory where the downloaded files will
    be stored. It is the main directory where the `sub_dir` will be created to store the downloaded
    files
    :param sub_dir: The `sub_dir` parameter in the `download_files` function represents the subdirectory
    within the `work_dir` where the downloaded files will be stored. It is used to specify the relative
    path within the `work_dir` where the files should be saved
    :param files: The `files` parameter is a list of `File` objects that contains information about the
    files to be downloaded. Each `File` object likely has attributes such as `bucket` (the storage
    bucket where the file is located) and `path` (the path to the file within the bucket)
    :type files: List[File]
    """
    storage_client = get_storage_client()
    target_path = os.path.join(work_dir, sub_dir)
    for file in files:
        file_content = await storage_client.get_file(file.bucket, file.id)
        if file_content:
            filename = os.path.basename(file.id)
            write_storage_files(file_content, target_path, filename)


async def download_module(info: LocalTaskParams):
    logger = get_run_logger()
    from fa_common.storage import get_storage_client

    storage_client = get_storage_client()
    target_path = os.path.join(info.module_path, info.module_version)

    if os.path.exists(target_path):
        logger.info(f"Module version already exists: {info.module_path}/{info.module_version}/")
        return

    # @NOTE: the "/" at the tail is quite important
    lst_objs = await storage_client.list_files(info.module_bucket, f"{info.module_remote_path}/{info.module_version}/")
    lst_files = list(filter(lambda f: not f.dir, lst_objs))

    if len(lst_files) == 0:
        raise ValueError(
            f"No content was found in the modules remote path: {info.module_bucket}/{info.module_remote_path}/{info.module_version}"
        )

    ensure_directories_exist([info.module_path, target_path])

    for file in lst_files:
        file_content = await storage_client.get_file(info.module_bucket, file.id)
        if file_content:
            if ".zip" in file.id:
                extract_zip_from_bytesio(file_content, target_path)
            else:
                filename = os.path.basename(file.id)
                write_storage_files(file_content, target_path, filename)
            logger.info("Module Ready to Use!")
            return
    raise ValueError(f"Module Not Found: {info.module_remote_path}/{info.module_version}")


async def write_params_to_file(info: LocalTaskParams, input_params, filetype: FileType = FileType.JSON, filename="param.json"):
    """
    Writes the input parameters required for a module in the pre-defined input path.

    Useful for scenarios where the module expects the input_params as input_file rather
    than directly passing the params.

    :param: input_params: dict of parameters
    """
    if filetype == FileType.JSON:
        with open(os.path.join(os.path.join(info.working_dir, info.input_path), filename), "w") as f:
            json.dump(input_params, f, indent=2)
        return

    if filetype == FileType.TXT:
        raise NotImplementedError("TXT file type handling not implemented.")

    if filetype == FileType.YAML:
        raise NotImplementedError("YAML file type handling not implemented.")

    raise ValueError("Unknown filetype")


async def run_standalone(info: LocalTaskParams):
    logger = get_run_logger()

    commands = [f"cd {info.working_dir}", *info.module_run_cmd]
    full_command = " && ".join(commands)

    try:
        result = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        result.check_returncode()
        # Adding 1 sec buffer to make sure the process is complete.
        await asyncio.sleep(1)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed with exit code %s", e.returncode)
        logger.error("Output:\n%s", e.stdout)
        logger.error("Errors:\n%s", e.stderr)
        raise Exception(f"Subprocess failed with exit code {e.returncode}. Check logs for more details.") from e
        # raise Exception(f"Subprocess failed with exit code {e.returncode}")


def execute_function_from_script(script_name, func_name, script_path, *args, **kwargs):
    """
    Fetch and execute a function directly from a Python script located in a specific directory.

    Args:
        module_name (str): The name to assign to the module (does not need to match the file name).
        task_name (str): The name of the function to execute from the script.
        plugin_path (str): Full path to the Python script.
        *args: Positional arguments passed to the function.
        **kwargs: Keyword arguments passed to the function.

    Returns:
        Any: The result of the function execution.
    """
    import importlib.util

    try:
        # Construct full module file path
        module_path = os.path.join(script_path, script_name + ".py")

        # Load the module spec and module from the file location
        spec = importlib.util.spec_from_file_location(script_name, module_path)
        if spec is None:
            raise ImportError(f"Could not load spec for {script_name} at {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the function from the loaded module
        func = getattr(module, func_name)
        if not callable(func):
            raise TypeError(f"Attribute {func_name} of module {script_name} is not callable")

        # Execute the function with arguments
        return func(*args, **kwargs)
    except ImportError as e:
        raise ImportError(f"Unable to load module '{script_name}': {e}") from e
    except AttributeError as e:
        raise AttributeError(f"The script '{script_name}' does not have a function named '{func_name}': {e}") from e


def format_log_levels(level):
    if level == 10:
        return "DEBUG"
    if level == 20:
        return "INFO"
    if level == 30:
        return "WARNING"
    if level == 40:
        return "ERROR"
    if level == 50:
        return "CRITICAL"
    return "UNKNOWN"


def format_log_record(log: Log):
    return f"{format_log_levels(log.level)} ({log.timestamp.isoformat()}): {log.message}\n"


async def upload_outputs(info: LocalTaskParams, upload_items: JobUploads):
    from pathlib import Path

    logger = get_run_logger()
    if upload_items.bucket_name is None:
        raise ValueError("For local runs, storage bucket name should be defined.")

    storage_client = get_storage_client()
    folder_path = Path(os.path.join(info.working_dir, info.output_path))

    # with open(f"{folder_path}/logs.json", "w") as file:
    #         json.dump(task_logs, file, indent=4)

    count = 0
    for item in folder_path.rglob("*"):
        count += 1
        if item.is_file():
            parent_path = upload_items.custom_path if item.name in upload_items.selected_outputs else upload_items.default_path
            relative_path = item.relative_to(folder_path).parent.as_posix()
            if relative_path == ".":
                remote_path = "/".join([parent_path, flow_run.get_name(), task_run.get_name()]).replace("//", "/")
            else:
                remote_path = "/".join([parent_path, flow_run.get_name(), task_run.get_name(), relative_path]).replace("//", "/")
            # file_path = item.name
            file_path = os.path.join(folder_path, item.name)
            logger.info(f"Uploading {file_path} to remote destination {remote_path} in {upload_items.bucket_name}")
            with open(file_path, "rb") as f:
                upload_item = UploadFile(filename=item.name, file=f)
                await storage_client.upload_file(upload_item, upload_items.bucket_name, remote_path)

    if count > 0:
        logger.info(f"All files uploaded to {os.path.join(parent_path, flow_run.get_name())}")
    else:
        logger.info(f"There was no output file to upload for {flow_run.get_name()}")

    # Dumping the logs
    task_logs = await get_task_logs_by_id(task_run.get_id())
    logs = ""
    for log in task_logs:
        logs += format_log_record(log)

    with open(f"{folder_path}/logs.txt", "w") as file:
        file.write(logs)

    parent_path = upload_items.default_path
    file_path = os.path.join(folder_path, "logs.txt")
    remote_path = "/".join([parent_path, flow_run.get_name(), task_run.get_name()]).replace("//", "/")
    # file_path = os.path.join(folder_path, item.name)
    logger.info(f"Uploading {file_path} to remote destination {remote_path} in {upload_items.bucket_name}")
    with open(file_path, "rb") as f:
        upload_item = UploadFile(filename="logs.txt", file=f)
        await storage_client.upload_file(upload_item, upload_items.bucket_name, remote_path)


async def cleanup(rm_folders):
    """This function aims to clean up working/temp directories."""
    for folder in rm_folders:
        delete_directory(folder)


async def format_flow_run_logs(flow_run_obj: FlowRun, flow_logs: List[Log]):
    flow_logs_dict = {}
    for log in flow_logs:
        log_dict = log.dict()
        if log_dict.get("task_run_id", None) is not None:
            task_run_name = await get_task_run_name(log_dict["task_run_id"])
            if task_run_name in flow_logs_dict:
                flow_logs_dict[task_run_name] += format_log_record(log)
            else:
                flow_logs_dict[task_run_name] = f'task_run_id: {log_dict["task_run_id"]}\n'
                flow_logs_dict[task_run_name] += format_log_record(log)
            continue

        if log_dict.get("flow_run_id", None) is not None:
            if flow_run_obj.name in flow_logs_dict:
                flow_logs_dict[flow_run_obj.name] += format_log_record(log)
            else:
                flow_logs_dict[flow_run_obj.name] = f"flow_run_id: {flow_run_obj.id}\n"
                flow_logs_dict[flow_run_obj.name] += format_log_record(log)

    return flow_logs_dict


async def upload_flow_run_logs(flow_run_obj: FlowRun, upload_info: JobUploads):
    flow_logs = await get_flow_logs_by_id(flow_run_obj.id)
    flow_logs_dict = await format_flow_run_logs(flow_run_obj, flow_logs)

    log_io = BytesIO()
    log_io.write(json.dumps(flow_logs_dict, cls=CustomJSONEncoder).encode("utf-8"))
    log_io.seek(0)

    parent_path = upload_info.default_path
    remote_path = "/".join([parent_path, flow_run_obj.name]).replace("//", "/")

    upload_item = UploadFile(filename="workflow_logs.json", file=log_io)
    await get_storage_client().upload_file(upload_item, upload_info.bucket_name, remote_path)


async def upload_flow_run_status(flow_run_obj: FlowRun, upload_info: JobUploads):
    workflow = await get_flow_runs_plus_tasks_by_id(flow_run_obj.id)

    stat_io = BytesIO()
    stat_io.write(flow_run_to_json(workflow))
    stat_io.seek(0)

    parent_path = upload_info.default_path
    remote_path = "/".join([parent_path, flow_run_obj.name]).replace("//", "/")

    upload_item = UploadFile(filename="workflow_local.json", file=stat_io)
    await get_storage_client().upload_file(upload_item, upload_info.bucket_name, remote_path)


async def on_exit_handler(flow, flow_run, state):
    jobs = flow_run.parameters.get("jobs")
    upload_info = JobUploads(**jobs[0].get("uploads"))

    await upload_flow_run_status(flow_run, upload_info)
    await upload_flow_run_logs(flow_run, upload_info)


async def on_cancellation_handler(flow, flow_run, state):
    jobs = flow_run.parameters.get("jobs")
    upload_info = JobUploads(**jobs[0].get("uploads"))

    storage = get_storage_client()
    if upload_info.default_path:
        folder_path = f"{upload_info.default_path}/{flow_run.name}"
        await storage.delete_file(upload_info.bucket_name, folder_path, True)

    if upload_info.custom_path:
        folder_path = f"{upload_info.custom_path}/{flow_run.name}"
        await storage.delete_file(upload_info.bucket_name, folder_path, True)


"""
 #     # ####### ######  #    # ####### #       ####### #     #    ######  ####### ####### ### #     # ### ####### ### ####### #     #
 #  #  # #     # #     # #   #  #       #       #     # #  #  #    #     # #       #        #  ##    #  #     #     #  #     # ##    #
 #  #  # #     # #     # #  #   #       #       #     # #  #  #    #     # #       #        #  # #   #  #     #     #  #     # # #   #
 #  #  # #     # ######  ###    #####   #       #     # #  #  #    #     # #####   #####    #  #  #  #  #     #     #  #     # #  #  #
 #  #  # #     # #   #   #  #   #       #       #     # #  #  #    #     # #       #        #  #   # #  #     #     #  #     # #   # #
 #  #  # #     # #    #  #   #  #       #       #     # #  #  #    #     # #       #        #  #    ##  #     #     #  #     # #    ##
  ## ##  ####### #     # #    # #       ####### #######  ## ##     ######  ####### #       ### #     # ###    #    ### ####### #     #

"""


def generate_task_name():
    # flow_name = flow_run.flow_name
    # task_name = task_run.task_name

    parameters = task_run.parameters
    name = parameters["job_name"]

    return name


@task(
    name="single-run-module",
    description="This task runs a module. It only handles one run.",
    task_run_name=generate_task_name,
    retries=0,
    log_prints=True,
)
async def run_job_task(job: JobTemplate, job_name: str, ignore_clean_up: bool = False):
    logger = get_run_logger()

    logger.info(f"Starting to prepare job {job_name}...")
    if job.template_config.standalone_base_path:
        base_path = job.template_config.standalone_base_path
    else:
        base_path = os.path.join(os.getcwd(), "standalone")
    local_path = os.path.join(base_path, job.module.name)
    tmp_dir = tempfile.mkdtemp()
    repo_ref = job.module.version.module_meta.repo_ref

    if isinstance(repo_ref.run_meta.cmd, str):
        repo_ref.run_meta.cmd = [repo_ref.run_meta.cmd]

    runner = repo_ref.run_meta.runner
    # BUILDING THE FULL PATH TO VENV RUNNER
    if runner is not None:
        runner = os.path.join(local_path, job.module.version.name, runner)

    for i, cmd in enumerate(repo_ref.run_meta.cmd):
        if "<<runner>>" in cmd:
            if runner is None:
                raise ValueError(
                    "<<runner>> placeholder introduced in cmd but no runner value"
                    f"is provided for module: {job.module.name}:{job.module.version.name}"
                )

            repo_ref.run_meta.cmd[i] = cmd.replace("<<runner>>", runner)

    # if repo_ref.run_meta.mode == ModuleRunModes.VENV:
    #     if len(repo_ref.run_meta.cmd) > 1:
    #         raise ValueError("When using virtual envs to run a script, only one command line is acceptable.")

    #     repo_ref.run_meta.cmd[0] = f"{os.path.join(local_path, job.module.version.name)}/{repo_ref.run_meta.cmd[0]}"

    info = LocalTaskParams(
        standalone_base_path=base_path,
        module_path=local_path,
        module_name=job.module.name,
        module_bucket=repo_ref.bucket.bucket_name,
        module_remote_path=repo_ref.bucket.path_prefix,
        module_version=job.module.version.name,
        module_run_mode=repo_ref.run_meta.mode.value,
        module_run_cmd=repo_ref.run_meta.cmd,
        working_dir=tmp_dir,
        input_path=repo_ref.run_meta.input_path,
        output_path=repo_ref.run_meta.output_path,
        use_tmp_dir=repo_ref.use_tmp_dir,
        ignore_copy_dirs=repo_ref.ignore_copy,
    )

    for k, v in info.model_dump().items():
        task_run.parameters[k] = v

    input_params = job.inputs.parameters
    if isinstance(input_params, str):
        # If it is string then it should be a JSON_STR
        input_params = json.loads(input_params)

    if not isinstance(input_params, dict):
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])
        raise ValueError("Input Parameters should be convertable to python dictionary.")

    try:
        logger.info(f"{job_name}: Downloading the module from s3 repository.")
        await download_module(info)
    except Exception as e:
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])
        raise JobExecutionError(f"Download-Module Error: an error occurred during downloading the module. {e}") from e

    try:
        logger.info(f"{job_name}: Creating working directory.")
        await init_working_directory(info)
    except Exception as e:
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])
        raise JobExecutionError(f"Workdir Error: an error occurred during creating the working directory. {e}") from e

    try:
        logger.info(f"{job_name}: Downloading input files.")
        if len(job.inputs.files) > 0:
            await download_files(info.working_dir, info.input_path, job.inputs.files)
    except Exception as e:
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])
        raise JobExecutionError(f"Download-Files Error: an error occurred during downloading the input files: {e}") from e

    try:
        logger.info(f"{job_name}: Starting to run the module.")
        if info.module_run_mode in (ModuleRunModes.SUBPROCESS, ModuleRunModes.VENV):
            await write_params_to_file(info, input_params, FileType.JSON, "param.json")
            await run_standalone(info)
        else:
            # WHEN RUNNING THROUGH A FUNCTION IN SCRIPTS FOLLOWING ASSUMTIONS ARE MADE:
            # 1. SCRIPT NAME: main.py
            # 2. SCRIPT FUNCTION: def main(input_params)
            execute_function_from_script(
                script_name="main", func_name="main", script_path=info.working_dir, input_params=input_params, working_dir=info.working_dir
            )
    except Exception as e:
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])
        raise JobExecutionError(f"Module-Run Error: an error occured during running the module: {e}") from e

    try:
        logger.info(f"{job_name}: Uploading the outputs.")
        await upload_outputs(info, job.uploads)
    except Exception as e:
        raise JobExecutionError(f"Upload Error: an error occurred during uploading: {e}") from e
    finally:
        await cleanup(rm_folders=[] if ignore_clean_up else [info.working_dir])

    return {"task_id": task_run.get_id(), "task_name": task_run.get_name()}


def generate_flow_run_name():
    # flow_name = flow_run.flow_name

    parameters = flow_run.parameters
    name = parameters["flow_name"]

    return f"{name}: {flow_run.get_id()}"


@flow(
    name="Run Jobs",
    task_runner=ConcurrentTaskRunner(),
    # flow_run_name=generate_flow_run_name,
    flow_run_name=lambda: f"{flow_run.parameters['flow_name']}",
    description="This flow runs a batch of jobs locally and concurrently.",
    on_completion=[on_exit_handler],
    on_failure=[on_exit_handler],
    on_crashed=[on_exit_handler],
    on_cancellation=[on_cancellation_handler],
)
def run_prefect_jobs(jobs: List[JobTemplate], flow_name: str, ignore_clean_up: bool = False):
    lst_tasks = []
    for job in jobs:
        lst_tasks.append(run_job_task.submit(job=job, job_name=f"{job.name}", ignore_clean_up=ignore_clean_up))
    # return lst_tasks
