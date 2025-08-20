from io import BytesIO
from typing import Any, Literal

import pandas as pd
from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import UploadFile
from pydantic import EmailStr

from fa_common.config import get_settings
from fa_common.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    StorageError,
)
from fa_common.routes.project.models import ProjectDB
from fa_common.routes.user.models import UserDB
from fa_common.storage import get_storage_client
from fa_common.utils import get_logger, validate_id

from .models import FileDB, UpdateFile
from .utils import get_data_frame_from_file, get_unique_filename, safe_join_path

LOG = get_logger()


async def delete_files_for_user(user: UserDB):
    files = await get_files_for_user(user, owner_only=True, limit=0)
    for file in files[0]:
        await delete_file(file)
    return True


async def delete_files_for_project(project_id: str | ObjectId | PydanticObjectId):
    """
    Delete all files associated with a specific project.

    Parameters
    ----------
    project_id : str | ObjectId
        The ID of the project whose files should be deleted.

    Returns
    -------
    bool
        True if the operation was successful.
    """
    valid_proj_id = validate_id(project_id)
    files, _ = await get_files_for_project(project_id=valid_proj_id, limit=0)

    for file in files:
        LOG.info(f"Deleting file {file.file_ref.name} from project {project_id}")
        await delete_file(file)

    return True


async def get_file_bytes(file: FileDB) -> BytesIO:
    client = get_storage_client()
    try:
        if file.file_ref.bucket is not None and file.file_ref.id is not None:
            file_bytes = await client.get_file(file.file_ref.bucket, file.file_ref.id)

            if file_bytes is None:
                raise NotFoundError(f"No file content returned from {file.file_ref.id}")
        else:
            raise InternalServerError("File ref is incomplete.")
    except StorageError as err:
        raise NotFoundError(f"Referenced file is missing from {file.file_ref.id}") from err

    return file_bytes


async def get_table_from_file(
    file: FileDB,
    offset: int = 0,
    limit: int = 100,
    sort: list[str] | None = None,
    separator: str | None = None,
    sheet: str | None = None,
    return_format: Literal["csv", "json"] = "json",
    encoding: str | None = "utf-8",
    transpose: bool = False,
    header_start_row: int = 0,
    data_start_row: int = 1,
    data_end_row: int | None = None,
) -> tuple[str | list[dict], int]:
    # Rename Duplicate columns
    file_bytes = await get_file_bytes(file)
    try:
        df, _ = await get_data_frame_from_file(
            file_bytes,
            file.file_ref.name,
            header_row=header_start_row,
            data_start_row=data_start_row,
            data_end_row=data_end_row,
            can_be_single_col=True,
            separator=separator,
            sheet=sheet,
            encoding=encoding,
            transpose=transpose,
        )
    except Exception as e:
        raise BadRequestError(f"Error creating table from file, is this file a valid table format?: {e}") from e

    if sort is not None and isinstance(df, pd.DataFrame):
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
        try:
            df = df.sort_values(by=columns, ascending=assending)
        except KeyError as e:
            LOG.warning(f"Unable to sort by {columns}, one or more columns not found in file: {file.file_ref.name}: {e}")

    total = df.shape[0]
    if return_format == "json":
        return df.iloc[offset : offset + limit].to_dict("records"), total
    else:
        return df.iloc[offset : offset + limit].to_csv(index=False), total


async def upload_file(
    file: UploadFile,
    user: UserDB,
    project_id: str | ObjectId | None = None,
    sub_path: str = "",
    tags: list[str] = [],
    file_users: list[EmailStr] = [],
    allow_duplicates: bool = False,
) -> FileDB:
    settings = get_settings()
    client = get_storage_client()
    if project_id is not None:
        valid_proj_id = validate_id(project_id)
        project = await ProjectDB.find_one(ProjectDB.id == valid_proj_id)
        if project is None:
            raise NotFoundError(f"Project with id {project_id} does not exist.")

        storage = project.get_storage()
    else:
        storage = user.get_storage_location(settings.PROJECT_NAME)

    storage_path = safe_join_path([storage.path_prefix, sub_path])

    file.filename = await get_unique_filename(storage.bucket_name, storage_path, file.filename, allow_duplicates)

    sheets = None
    if file.filename is not None and (file.filename.lower().endswith(".xlsx")):
        try:
            excel_file = BytesIO(file.file.read())
            wb = pd.ExcelFile(excel_file, engine="openpyxl")
            sheets = wb.sheet_names
            file.file.seek(0)  # be kind, rewind
        except Exception as e:
            raise InternalServerError(f"Unable to read excel file: {file.filename}") from e

        file.file.seek(0)

    file_ref = await client.upload_file(
        file,
        storage.bucket_name,
        storage_path,
    )

    file_model = FileDB(
        owner_id=user.sub,  # Using user.sub instead of str(user.id)
        project_id=str(project_id) if project_id is not None else None,
        file_ref=file_ref,
        tags=tags,
        file_users=file_users,
        sheets=sheets,
    )
    await file_model.save()

    return file_model


async def replace_file(
    filedb: FileDB,
    file: UploadFile,
    allow_duplicates: bool = False,
) -> FileDB:
    client = get_storage_client()

    bucket = filedb.file_ref.bucket
    path = filedb.file_ref.path if filedb.file_ref.path is not None else ""

    if filedb.file_ref.bucket is not None and filedb.file_ref.id is not None:
        await client.delete_file(filedb.file_ref.bucket, filedb.file_ref.id)
    else:
        raise InternalServerError(f"Unable to delete file due to incomplete File ref {filedb.file_ref.id} ID: {filedb.id}.")

    file.filename = await get_unique_filename(bucket, path, file.filename, allow_duplicates=allow_duplicates)

    file_ref = await client.upload_file(
        file,
        bucket,
        path,
    )

    filedb.file_ref = file_ref
    await filedb.save()

    return filedb


async def get_files(
    user: UserDB | None = None,
    owner_only=False,
    offset: int = 0,
    limit: int = 10,
    sort: list[str] | None = None,
    project_ids: list[str] | None = None,
    path: str | None = None,
    extensions: list[str] | None = None,
    mime_type: str | None = None,
    start_with: str | None = None,
    exact_name: str | None = None,
) -> tuple[list[FileDB], int]:
    """
    Get files based on various filter criteria.

    Parameters
    ----------
    user : UserDB | None, optional
        The user object to filter files by. If None, user-based filtering is skipped. Default is None.
    owner_only : bool, optional
        If True and user is provided, only return files owned by the user. Default is False.
    offset : int, optional
        The number of files to skip before returning results. Default is 0.
    limit : int, optional
        The maximum number of files to return. Default is 10.
    sort : list[str], optional
        The list of fields to sort the files by using the syntax `['+fieldName', '-secondField']`.
        See https://beanie-odm.dev/tutorial/finding-documents/
        Default is an empty list.
    project_ids : list[str] | None, optional
        A list of project IDs to filter the files by. Default is None.
    path : str | None, optional
        The exact file path to filter the files by. Default is None.
    extensions : list[str] | None, optional
        List of file extensions to filter by. Default is None.
    mime_type : str | None, optional
        The MIME type to filter the files by. Default is None.
    start_with : str | None, optional
        The prefix to filter the files by. Default is None.
    exact_name : str | None, optional
        The exact name to filter the files by. Will take priority over 'start_with' if both are provided. Default is None.

    Returns
    -------
    list[FileDB]
        A list of files matching the criteria.
    """
    # Initialize combined query
    combined_query: dict[str, Any] = {}

    # Add user query if a user is provided
    if user:
        # First $or query for user ownership and file users
        user_query: dict[str, Any] = {
            "$or": [
                {"ownerId": user.sub},  # Check files owned by user.sub
                {"ownerId": str(user.id)},  # Check files owned by user.id
            ]
        }

        if not owner_only:
            # Add file_users check when not in owner_only mode
            user_query["$or"].append({"fileUsers": {"$elemMatch": {"$regex": f"^{user.email}$", "$options": "i"}}})

        # Add user query to combined query
        combined_query["$and"] = [user_query]

    # Second $or query for file extensions
    extension_query = []
    if extensions:
        extension_query = [{"fileRef.name": {"$regex": f".*\\.{ext}$", "$options": "i"}} for ext in extensions]
        if "$and" not in combined_query:
            combined_query["$and"] = []
        combined_query["$and"].append({"$or": extension_query})

    if project_ids:
        combined_query["projectId"] = {"$in": project_ids}

    if path:
        combined_query["fileRef.path"] = {"$regex": f"^{path}$", "$options": "i"}

    if exact_name:
        combined_query["fileRef.name"] = {"$regex": f"^{exact_name}$", "$options": "i"}
    elif start_with:
        combined_query["fileRef.name"] = {"$regex": f"^{start_with}", "$options": "i"}

    if mime_type:
        combined_query["fileRef.contentType"] = mime_type

    query = FileDB.find(combined_query)
    if sort and sort is not None:
        query = query.sort(*sort)

    total = await query.count()
    if offset > 0:
        query = query.skip(offset)
    if limit > 0:
        query = query.limit(limit)
    return await query.to_list(), total


async def get_files_for_user(
    user: UserDB,
    owner_only=False,
    offset: int = 0,
    limit: int = 10,
    sort: list[str] | None = None,
    project_ids: list[str] | None = None,
    path: str | None = None,
    extensions: list[str] | None = None,
    mime_type: str | None = None,
    start_with: str | None = None,
    exact_name: str | None = None,
) -> tuple[list[FileDB], int]:
    """
    Get files for a specific user.
    This is a wrapper around get_files that ensures backward compatibility.

    Parameters are the same as get_files, but user is required.
    """
    return await get_files(
        user=user,
        owner_only=owner_only,
        offset=offset,
        limit=limit,
        sort=sort,
        project_ids=project_ids,
        path=path,
        extensions=extensions,
        mime_type=mime_type,
        start_with=start_with,
        exact_name=exact_name,
    )


async def get_files_for_project(
    project_id: str | ObjectId,
    offset: int = 0,
    limit: int = 10,
    sort: list[str] | None = None,
    path: str | None = None,
    extensions: list[str] | None = None,
    mime_type: str | None = None,
    start_with: str | None = None,
    exact_name: str | None = None,
) -> tuple[list[FileDB], int]:
    """
    Get files for a specific project.

    Parameters
    ----------
    project_id : str | ObjectId
        The ID of the project to get files for.
    offset : int, optional
        The number of files to skip before returning results. Default is 0.
    limit : int, optional
        The maximum number of files to return. Default is 10.
    sort : list[str], optional
        The list of fields to sort the files by.
    path : str | None, optional
        The exact file path to filter the files by. Default is None.
    extensions : list[str] | None, optional
        List of file extensions to filter by. Default is None.
    mime_type : str | None, optional
        The MIME type to filter the files by. Default is None.
    start_with : str | None, optional
        The prefix to filter the files by. Default is None.
    exact_name : str | None, optional
        The exact name to filter the files by. Default is None.

    Returns
    -------
    list[FileDB]
        A list of files belonging to the project.
    """
    valid_proj_id = validate_id(project_id)

    return await get_files(
        user=None,
        offset=offset,
        limit=limit,
        sort=sort,
        project_ids=[str(valid_proj_id)],
        path=path,
        extensions=extensions,
        mime_type=mime_type,
        start_with=start_with,
        exact_name=exact_name,
    )


async def get_file(file_id: str | ObjectId, user: UserDB) -> FileDB:
    valid_file_id = validate_id(file_id)
    file = await FileDB.find_one(FileDB.id == valid_file_id)

    if file is None:
        raise NotFoundError(f"File {file_id} not found.")

    access_from_project = False
    if file.project_id is not None:
        project = await ProjectDB.find_one(ProjectDB.id == validate_id(file.project_id))
        if project is not None and await project.user_has_access(user):
            access_from_project = True

    access_from_file_users = False
    if user.email is not None:
        access_from_file_users = bool(user.email.lower() not in [user.lower() for user in file.file_users])

    if file.owner_id != user.sub and file.owner_id != str(user.id) and not access_from_file_users and not access_from_project:
        raise ForbiddenError(detail="You do not have access to this file")

    return file


async def delete_file(file: FileDB):
    client = get_storage_client()

    if file.file_ref.bucket is not None and file.file_ref.id is not None:
        await client.delete_file(file.file_ref.bucket, file.file_ref.id)
    else:
        raise InternalServerError(f"Unable to delete file due to incomplete File ref {file.file_ref.id} ID: {file.id}.")
    await file.delete()
    return True


async def update_file_metadata(
    file: FileDB,
    update: UpdateFile,
) -> FileDB:
    if file is None or file.id is None:
        raise NotFoundError("File does not exist")

    update_file = file.model_copy(update=update.get_update_dict())
    if update.add_tags is not None:
        update_file.tags.extend(update.add_tags)
    if update.add_file_users is not None:
        update_file.file_users.extend(update.add_file_users)
    await update_file.save()

    return update_file
