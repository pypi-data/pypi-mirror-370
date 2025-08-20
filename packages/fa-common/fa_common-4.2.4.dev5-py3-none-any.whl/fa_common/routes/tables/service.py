import random
import string
import sys
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
from beanie import Link, PydanticObjectId
from beanie.operators import ElemMatch, In, Or, RegEx
from bson import ObjectId
from pandas import DataFrame
from pydantic import BaseModel

# use the xt_workbench.shared versions of these imports for now
from fa_common import File, sizeof_fmt
from fa_common.exceptions import BadRequestError, ForbiddenError, NotFoundError, RuleValidationError
from fa_common.models import PaginationListResponse
from fa_common.routes.files.models import FileDB
from fa_common.routes.files.service import get_file, get_file_bytes
from fa_common.routes.files.utils import get_bytes_from_file_ref, get_data_frame_from_file
from fa_common.routes.project.models import ProjectDB
from fa_common.routes.user.models import UserDB
from fa_common.storage import get_storage_client
from fa_common.storage.base_client import BaseClient
from fa_common.utils import logger as LOG
from fa_common.utils import validate_id

from .models import CreateTable, TableDB, TableDBWithData, TableLoadParams, UpdateTable


def new_unique_name(old_name: str) -> str:
    """Generate a new unique name for a table by appending a random 4 characters to the old name.
    Ensuring the characters are valid for AWS S3 storage"""
    return f"{old_name}_{''.join(random.choices(string.ascii_letters + string.digits, k=4))}"


async def save_table_file_csv(frame: DataFrame, parent: File, table_name: str, overwrite: bool = False) -> File:
    client: BaseClient = get_storage_client()
    bucket = parent.bucket
    path = f"{parent.path}/{parent.name.replace('.', '_')}_tables/{table_name}.csv"
    exists = await client.file_exists(bucket, path)
    if exists and not overwrite:
        LOG.warning(f"Table File {table_name} already exists, adding a suffix")
        return await save_table_file_csv(frame, parent, new_unique_name(table_name), overwrite=overwrite)

    else:
        string_buf = StringIO()
        frame.to_csv(string_buf, index=False)
        string_buf.seek(0)  # Be kind, rewind
        file_ref = await client.upload_string(string_buf.read(), bucket, path, content_type="text/csv")

    return file_ref


async def save_table_file_feather(frame: DataFrame, parent: File, table_name: str, overwrite: bool = False) -> File:
    client: BaseClient = get_storage_client()
    bucket = parent.bucket
    path = f"{parent.path}/{parent.name.replace('.', '_')}_tables/{table_name}.feather"
    exists = await client.file_exists(bucket, path)
    if exists and not overwrite:
        LOG.warning(f"Table File {table_name} already exists, adding a suffix")
        return await save_table_file_feather(frame, parent, new_unique_name(table_name), overwrite=overwrite)
    else:
        bytes_io = BytesIO()
        frame.to_feather(bytes_io, compression="zstd")
        file_ref = await client.upload_string(bytes_io.read(), bucket, path, content_type="application/vnd.apache.arrow.file")

    return file_ref


# async def save_table_file_hdf5(frame: DataFrame, parent: File, table_name: str, overwrite: bool = False) -> File:
#     client: BaseClient = get_storage_client()
#     bucket = parent.bucket
#     path = f"{parent.path}/{parent.name.replace('.', '_')}_tables/{table_name}.h5"
#     s3url = f"s3://{bucket}/{path}"
#     exists = await client.file_exists(bucket, path)
#     if exists and not overwrite:
#         raise AlreadyExistsError(f"Table {table_name} already exists in {parent.id}")
#     else:
#         s3f = fsspec.open(s3url, mode='rb', anon=True, default_fill_cache=False)
#         h5f = h5py.File(s3f., mode='w')
#         with HDFStore("{table_name}.h5", mode="w", complib="blosc", complevel=4, driver="H5FD_CORE",
#  driver_core_backing_store=0) as store:
#             store.put(key="data", value=    frame, format="table")
#             file_ref = await client.upload_string(store._handle, bucket, path, content_type="application/x-hdf5")
#     return file_ref


class TableSort(BaseModel):
    column: str
    ascending: bool = True


async def get_frame_from_table(table: TableDB, sort: list[str] | None = None) -> DataFrame:
    frame = None
    if table.data_format == "file" and table.data_file is not None:
        bytes_io = await get_bytes_from_file_ref(table.data_file)
        if table.data_file.name.endswith(".csv"):
            frame = pd.read_csv(bytes_io)
        elif table.data_file.name.endswith(".feather"):
            frame = pd.read_feather(bytes_io)
        # elif table.data_file.name.endswith(".h5"):
        #     with h5py.File(bytes_io, "r") as f:
        #         frame = pd.read_hdf(pd.HDFStore(f), key="data")
    elif table.data_format == "json" and isinstance(table.data, dict):
        frame = DataFrame.from_dict(table.data)
    elif table.data_format == "json" and isinstance(table.data, str):
        frame = pd.read_json(StringIO(table.data))
    elif table.data_format == "csv" and isinstance(table.data, str):
        frame = pd.read_csv(StringIO(table.data))
    elif table.data_format == "load_from_raw" and table.data_file is not None and table.data_params is not None:
        file_bytes = await get_bytes_from_file_ref(table.data_file)
        frame, _ = await get_data_frame_from_file(
            file_bytes,
            table.data_file.name,
            header_row=None,
            can_be_single_col=True,
            separator=table.data_params.separator,
            sheet=table.data_params.sheet,
            data_start_row=table.data_params.data_start_row,
            data_end_row=table.data_params.data_end_row,
            encoding=table.data_params.encoding,
            transpose=table.data_params.transpose,
        )
    else:
        raise BadRequestError(f"Table data format was unable to be loaded: {table.data_format}")

    if frame is None:
        raise BadRequestError(f"Table data format was unable to be loaded: {table.data_format}")

    if sort is not None and isinstance(frame, pd.DataFrame):
        # apply sorting to pandas where sort is a list of strings +/-column_name
        # if no sign is present assume assending
        assending = []
        columns = []
        for s in sort:
            if s:
                offset = 0
                if s.startswith("-"):
                    assending.append(False)
                    offset = 1
                else:
                    assending.append(True)
                    if s.startswith("+"):
                        offset = 1
                columns.append(s[offset:])
        frame = frame.sort_values(by=columns, ascending=assending)

    return frame  # type: ignore


async def get_paging_frame_from_table(
    table: TableDB, offset: int = 0, limit: int | None = None, sort: list[str] | None = None
) -> tuple[DataFrame, int]:
    frame = await get_frame_from_table(table, sort)
    total_rows = len(frame)

    return frame.iloc[offset : offset + limit] if limit is not None else frame.iloc[offset:], total_rows


async def create_table_from_file(file: FileDB, create: CreateTable, owner: UserDB) -> TableDB:
    # Rename Duplicate columns
    file_bytes = await get_file_bytes(file)

    df, metadata = await get_data_frame_from_file(
        file_bytes,
        file.file_ref.name,
        header_row=create.params.header_start_row,
        can_be_single_col=create.allow_single_column,
        separator=create.params.separator,
        sheet=create.params.sheet,
        data_start_row=create.params.data_start_row,
        data_end_row=create.params.data_end_row,
        encoding=create.params.encoding,
        transpose=create.params.transpose,
        metadata_rows=create.params.metadata_rows,
    )

    data = None
    file_ref = None
    if create.data_format in [None, "auto"]:
        """Find the optimal format to store the table in"""
        size = sys.getsizeof(df)
        if size > (1000 * 1000 * 1):
            create.data_format = "file"
        elif size > (1000 * 1000 * 0.5):
            create.data_format = "csv"
        else:
            create.data_format = "json"

    match create.data_format:
        case "json":
            data = df.to_json(orient="records", index=False)
            size = sys.getsizeof(data)
            if sys.getsizeof(data) > (1000 * 1000 * 5):
                raise RuleValidationError(f"Table is too large to store in JSON format in DB (> 5MB). Size of data = {sizeof_fmt(size)}")
        case "csv":
            data = df.to_csv(index=False)
            size = sys.getsizeof(data)
            if sys.getsizeof(data) > (1000 * 1000 * 5):
                raise RuleValidationError(f"Table is too large to store in CSV format in DB (> 5MB). Size of data = {sizeof_fmt(size)}")
        case "file":
            try:
                file_ref = await save_table_file_feather(df, file.file_ref, create.table_name)
            except Exception as e:
                # LOG.warning(f"Failed to save {create.table_name} as feather file: {str(e)}")
                # file_ref = await save_table_file_hdf5(df, file.file_ref, create.table_name)
                # except Exception as e:
                LOG.warning(f"Failed to save {create.table_name} as feather file: {e!s}")
                file_ref = await save_table_file_csv(df, file.file_ref, create.table_name)

        case "load_from_raw":
            file_ref = file.file_ref
        case _:
            pass
    try:
        project_id = validate_id(create.project_id)
    except Exception:
        project_id = None

    if not project_id:
        try:
            project_id = validate_id(file.project_id)
        except Exception:
            project_id = None

    project = await ProjectDB.get(project_id) if project_id else None

    table = TableDBWithData(
        name=create.table_name,
        owner=owner,  # type: ignore
        project=project,  # type: ignore
        columns=df.columns.astype(str).tolist(),
        numeric_columns=df.select_dtypes(include=[np.number]).columns.astype(str).tolist(),
        data_format=create.data_format,  # type: ignore
        data=data,
        data_file=file_ref,
        data_params=create.params,
        metadata_rows=metadata,
        metadata_extra=create.metadata_extra,
        parent_file_id=str(file.id) if file else None,
        tags=create.tags,
        total_rows=len(df),
        table_users=file.file_users if create.table_users is None else create.table_users,
    )

    await table.save()

    if create.return_data_format is None:
        table.data = None
    elif create.return_data_format == "json" and create.data_format != "json":
        table.data = df.to_json(orient="records", index=False)
    elif create.return_data_format == "csv" and create.data_format != "csv":
        table.data = df.to_csv(index=False)

    return table


async def get_tables_for_user(
    user: UserDB,
    owner_only: bool = False,
    offset: int = 0,
    limit: int = 10,
    sort: list[str] | None = None,
    project_ids: list[str] | None = None,
    start_with: str | None = None,
    exact_name: str | None = None,
    include_data: bool = False,
) -> PaginationListResponse[TableDB] | PaginationListResponse[TableDBWithData]:
    """Get tables for a user."""
    table_type = TableDBWithData if include_data else TableDB
    result = PaginationListResponse[table_type](values=[], total=0, limit=limit, offset=offset)

    # Build all filter conditions first
    filter_conditions = []

    # User access filter
    if owner_only:
        filter_conditions.append(table_type.owner.id == PydanticObjectId(user.id))
    else:
        filter_conditions.append(
            Or(
                table_type.owner.id == PydanticObjectId(user.id),
                ElemMatch(table_type.table_users, {"$regex": f"^{user.email}$", "$options": "i"}),
            )
        )

    # Project filter
    if project_ids and len(project_ids) > 0:
        try:
            _project_ids = [PydanticObjectId(pid) for pid in project_ids]
            filter_conditions.append(In(table_type.project.id, _project_ids))
        except Exception as e:
            raise BadRequestError(f"Invalid project ID: {project_ids}") from e

    # Name filters
    if exact_name:
        filter_conditions.append(RegEx(table_type.name, f"^{exact_name}$", "i"))
    elif start_with:
        filter_conditions.append(RegEx(table_type.name, f"^{start_with}", "i"))

    # Create a single combined query with all conditions
    query = table_type.find(*filter_conditions, fetch_links=True)

    # Get total count before pagination
    result.total = await query.count()

    # Apply sorting
    # Ensure we have a stable sort by adding id as a tie-breaker if not already present
    if sort:
        has_id_sort = any(s.endswith("id") for s in sort)
        if not has_id_sort:
            sort.append("+_id")
    else:
        sort = ["-created", "+_id"]  # Default stable sort

    query = query.sort(*sort)
    if offset > 0:
        query = query.skip(offset)
    if limit > 0:
        query = query.limit(limit)

    # Apply pagination with proper sorting order
    result.values = await query.to_list()

    return result


async def get_table(table_id: str | ObjectId, user: UserDB, include_data: bool = False) -> TableDB:
    valid_file_id = PydanticObjectId(validate_id(table_id))

    if include_data:
        table = await TableDBWithData.get(valid_file_id, fetch_links=True, nesting_depth=1)

    else:
        table = await TableDB.get(valid_file_id, fetch_links=True, nesting_depth=1)

    if table is None:
        raise NotFoundError(f"Table {table_id} not found.")

    if isinstance(table.owner, Link):
        raise ValueError("Table owner does not exist in the database")

    access_from_project = False
    if table.project is not None:
        # linked project has been pre-fetched so safe to ignore
        project: ProjectDB = table.project  # type: ignore
        access_from_project = await project.user_has_access(user)

    access_from_table_users = False
    if user.email is not None:
        access_from_table_users = bool(user.email.lower() not in [user.lower() for user in table.table_users])

    if table.owner.id != user.id and not access_from_project and not access_from_table_users:
        raise ForbiddenError(detail="You do not have access to this table")

    return table


async def delete_table(table: TableDB):
    client = get_storage_client()
    if table.data_format == "file" and table.data_file is not None:
        if table.data_file.bucket is None or table.data_file.id is None:
            raise ValueError("Table data file is missing bucket or Path")
        await client.delete_file(table.data_file.bucket, table.data_file.full_path)

    await table.delete()

    return True


async def delete_project_tables(project_id: str | ObjectId | PydanticObjectId) -> dict:
    """Delete all tables associated with a project.

    Args:
        project_id: The ID of the project whose tables should be deleted

    Returns:
        A dictionary with statistics about the operation
    """
    valid_project_id = validate_id(project_id)

    # Find all tables associated with this project
    tables = await TableDB.find(TableDB.project.id == valid_project_id).to_list()

    total_tables = len(tables)
    deleted_count = 0
    error_count = 0
    errors = []

    # Delete each table
    for table in tables:
        try:
            await delete_table(table)
            deleted_count += 1
        except Exception as e:
            error_count += 1
            errors.append({"table_id": str(table.id), "error": str(e)})
            LOG.error(f"Error deleting table {table.id} for project {project_id}: {e!s}")

    results = {"project_id": str(project_id), "total_tables": total_tables, "deleted_count": deleted_count, "error_count": error_count}

    if errors:
        results["errors"] = errors

    LOG.info(f"Delete Project Tables results: {results}")

    return results


async def update_table(
    table: TableDB,
    update: UpdateTable,
    user: UserDB,
) -> TableDB:
    if table is None or table.id is None:
        raise NotFoundError("Table does not exist")

    # First handle metadata updates
    update_table = table.model_copy(update=update.get_update_dict())

    if update.add_tags is not None:
        update_table.tags.extend(update.add_tags)

    if update.add_table_users is not None:
        update_table.table_users.extend(update.add_table_users)

    # Check if we need to replace the data
    if (update.file_id and table.parent_file_id != update.file_id) or (update.params is not None and update.params != table.data_params):
        newFileId = update.file_id if update.file_id is not None else table.parent_file_id
        if newFileId is None:
            raise ValueError("Table is triggering a table file update but no ID is available.")

        if table.data_file is not None:
            # If the table already has a file, delete it
            storage_client = get_storage_client()
            await storage_client.delete_file(table.data_file.bucket, table.data_file.full_path)

        # Get the file with new data
        file = await get_file(newFileId, user)

        # If params are provided, use them; otherwise, use existing params
        params = update.params or table.data_params or TableLoadParams()

        # Get the file bytes and build dataframe
        file_bytes = await get_file_bytes(file)
        df, metadata = await get_data_frame_from_file(
            file_bytes,
            file.file_ref.name,
            header_row=None,
            can_be_single_col=True,  # Allow single column for replacement
            separator=params.separator,
            sheet=params.sheet,
            data_start_row=params.data_start_row,
            data_end_row=params.data_end_row,
            encoding=params.encoding,
            transpose=params.transpose,
            metadata_rows=params.metadata_rows,
        )

        # Prepare data storage based on existing format
        data = None
        file_ref = None
        data_format = update.data_format if update.data_format else table.data_format

        # Handle data storage based on format (same as in replace_table_data)
        match data_format:
            case "json":
                data = df.to_json(orient="records", index=False)
                size = sys.getsizeof(data)
                if sys.getsizeof(data) > (1000 * 1000 * 5):
                    raise RuleValidationError(
                        f"Table is too large to store in JSON format in DB (> 5MB). Size of data = {sizeof_fmt(size)}"
                    )
            case "csv":
                data = df.to_csv(index=False)
                size = sys.getsizeof(data)
                if sys.getsizeof(data) > (1000 * 1000 * 5):
                    raise RuleValidationError(f"Table is too large to store in CSV format in DB (> 5MB). Size of data = {sizeof_fmt(size)}")
            case "file":
                try:
                    # If there's an existing file, we want to replace it (overwrite=True)
                    file_ref = await save_table_file_feather(df, file.file_ref, update_table.name, overwrite=True)
                except Exception as e:
                    LOG.warning(f"Failed to save {update_table.name} as feather file: {e!s}")
                    file_ref = await save_table_file_csv(df, file.file_ref, update_table.name, overwrite=True)
            case "load_from_raw":
                file_ref = file.file_ref
            case _:
                pass

        # Update the data-related fields
        if isinstance(update_table, TableDBWithData):
            update_table.data = data

        update_table.data_file = file_ref if file_ref else update_table.data_file
        update_table.columns = df.columns.astype(str).tolist()
        update_table.numeric_columns = df.select_dtypes(include=[np.number]).columns.astype(str).tolist()
        update_table.metadata_rows = metadata if metadata else update_table.metadata_rows
        update_table.total_rows = len(df)
        update_table.parent_file_id = str(file.id) if file else None
        update_table.data_params = params

    # Save the updated table
    await update_table.save()

    return update_table


# Keep the replace_table_data method for backward compatibility
async def replace_table_data(table: TableDB, file: FileDB, user: UserDB) -> TableDB:
    """Replace the data of an existing table with new file data while preserving metadata

    Args:
        table: The existing table to update
        file: The file containing new data
        user: The user performing the operation

    Returns:
        The updated table
    """

    # Create an UpdateTable object and use the update_table method
    update = UpdateTable(fileId=str(file.id), params=table.data_params)

    return await update_table(table, update, user)
