import os
from io import BytesIO
from typing import Annotated, Literal

import numpy as np
from fastapi import APIRouter, Depends, File, Form, Header, Path, Query, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import EmailStr
from starlette import status

from fa_common import (
    BadRequestError,
    HTTPException,
    Message,
    get_settings,
    sizeof_fmt,
)
from fa_common import File as FileRef
from fa_common import logger as LOG
from fa_common.models import PaginationListResponse
from fa_common.routes.files.utils import extension_to_mimetype, get_data_frame_from_file, is_image
from fa_common.routes.shared.models import TableInfo
from fa_common.routes.user.models import UserDB
from fa_common.routes.user.service import get_current_app_user
from fa_common.storage import get_storage_client

from . import service
from .models import FileDB, UpdateFile

router = APIRouter()


async def valid_content_length(content_length: int = Header(...)):
    settings = get_settings()
    if content_length > settings.MAX_CONTENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_name="File Upload Error",
            detail=f"This File was too large ({sizeof_fmt(content_length)}).\n"
            + f"The maximum file size is {sizeof_fmt(settings.MAX_CONTENT_LENGTH)}",
        )
    return content_length


@router.post(
    "",
    response_model=FileDB,
    responses={409: {"description": "File already exists"}, 413: {"description": "File too large"}},
)
async def upload_file(
    file: UploadFile = File(...),
    project_id: str | None = Form(None),
    sub_path: str = Form(None),
    tags: list[str] = Form([]),
    file_users: list[EmailStr] = Form([]),
    allow_duplicates: bool = Form(False),
    current_user: UserDB = Depends(get_current_app_user),
    file_size: int = Depends(valid_content_length),
):
    """Upload file to a project or user storage."""
    # permissions = lic_user[1]
    # if not permissions.allow_new_uploads:
    #     raise ForbiddenError(
    #         "Your current licence does not allow for uploading new datasets. "
    #         + "This is mostly likely caused by an expired Licence or Trial."
    #     )

    # if not allowed_file(file.filename):
    #     raise BadRequestError(
    #         detail="The file extension is not supported or there is something wrong with the filename.\n"
    #         + f"File Name: {file.filename} \n Supported extensions include: {ALLOWED_EXTENSIONS}"
    #     )
    settings = get_settings()
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    LOG.debug(f"File {file.filename} uploaded, size {file_size}")
    # max_file_size = permissions.upload_size_limit_bytes()
    max_file_size = settings.MAX_CONTENT_LENGTH
    if file_size > max_file_size:
        LOG.warning(f"File {file.filename} was too large at size {file_size} and was rejected")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File {file.filename} was too large ({sizeof_fmt(file_size)}).\n"
            + f"The maximum file size is {sizeof_fmt(max_file_size)}",
        )
    file.file.seek(0)

    return await service.upload_file(
        file, current_user, project_id, sub_path, tags, file_users=file_users, allow_duplicates=allow_duplicates
    )


@router.get("", response_model=PaginationListResponse[FileDB])
async def get_files(
    onlyMine: bool = True,
    limit: int = 10,
    offset: int = 0,
    project: Annotated[list[str] | None, Query()] = None,
    path: str = "",
    startWith: str | None = None,
    exactName: str | None = None,
    mimeType: str | None = None,
    extension: Annotated[list[str] | None, Query()] = None,
    sort: Annotated[list[str] | None, Query(description="+/- followed by field name e.g. '+created' or '-fileRef.name'")] = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    results, total = await service.get_files_for_user(
        user=current_user,
        owner_only=onlyMine,
        offset=offset,
        limit=limit,
        sort=sort,
        project_ids=project,
        path=path,
        mime_type=mimeType,
        extensions=extension,
        start_with=startWith,
        exact_name=exactName,
    )
    return PaginationListResponse[FileDB](total=total, values=results, limit=limit, offset=offset)


@router.get(
    "/{file_id}",
    response_model=FileDB,
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
)
async def get_file_information(file_id: str, current_user: UserDB = Depends(get_current_app_user)):
    return await service.get_file(file_id, current_user)


@router.get(
    "/{file_id}/download",
    responses={
        200: {
            "description": "Successful response, file is streamed to the client",
        },
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
)
async def download_file(file_id: str, current_user: UserDB = Depends(get_current_app_user)):
    file = await service.get_file(file_id, current_user)
    file_bytes = await service.get_file_bytes(file)

    async def file_streamer(file_bytes: BytesIO):
        while True:
            chunk = file_bytes.read(4096)  # Read in chunks of 4KB
            if not chunk:
                break
            yield chunk

    return StreamingResponse(
        file_streamer(file_bytes),
        media_type=file.file_ref.content_type,
        headers={"Content-Disposition": f"attachment;filename={file.file_ref.name}"},
    )


@router.get(
    "/{file_id}/image",
    responses={
        200: {
            "description": "Successful response, image data is returned",
        },
        400: {"description": "Not a valid image"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
)
async def get_image(file_id: str, current_user: UserDB = Depends(get_current_app_user)):
    file = await service.get_file(file_id, current_user)
    if not is_image(file.file_ref):
        raise BadRequestError(f"File {file.id} is not an image")

    file_bytes = await service.get_file_bytes(file)

    content_type = file.file_ref.content_type if file.file_ref.content_type is not None else extension_to_mimetype(file.file_ref.extension)
    return Response(file_bytes.read(), media_type=content_type)


@router.get(
    "/{file_id}/table",
    responses={
        400: {"description": "Incorrectly formatted ID or Invalid parameters and/or File type for table"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {"schema": {"type": "object"}},
                "text/csv": {"schema": {"type": "string", "format": "binary"}},
            },
        },
    },
    response_model=PaginationListResponse[dict] | str,
)
async def get_raw_table(
    file_id: str,
    offset: int = 0,
    limit: int = 100,
    sort: list[str] | None = Query(None, description="+/- and column name e.g. +column1"),
    separator: str | None = None,
    sheet: str | None = None,
    encoding: str | None = "utf-8",
    transpose: bool = False,
    header_start_row: int = 0,
    data_start_row: int = 1,
    data_end_row: int | None = None,
    accept: str = Header("application/json", alias="Accept"),
    current_user: UserDB = Depends(get_current_app_user),
):
    response_format: Literal["json", "csv"] = "json"
    if "application/json" in accept:
        # Handle JSON response
        response_format = "json"
    elif "text/csv" in accept:
        # Handle CSV response
        response_format = "csv"

    file = await service.get_file(file_id, current_user)
    response, total = await service.get_table_from_file(
        file=file,
        offset=offset,
        limit=limit,
        sort=sort,
        separator=separator,
        sheet=sheet,
        return_format=response_format,
        encoding=encoding,
        transpose=transpose,
        header_start_row=header_start_row,
        data_start_row=data_start_row,
        data_end_row=data_end_row,
    )

    if response_format == "json" and isinstance(response, list):
        return PaginationListResponse[dict](values=response, total=total, limit=limit, offset=offset)
    else:
        return Response(response, media_type="text/csv")


@router.get(
    "/{file_id}/table/info",
    responses={
        400: {"description": "Incorrectly formatted ID or Invalid parameters and/or File type for table"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {"schema": {"type": "object"}},
                "text/csv": {"schema": {"type": "string", "format": "binary"}},
            },
        },
    },
    response_model=TableInfo,
)
async def get_raw_table_info(
    file_id: str,
    separator: str | None = None,
    sheet: str | None = None,
    encoding: str | None = "utf-8",
    transpose: bool = False,
    header_start_row: int = 0,
    data_start_row: int = 1,
    data_end_row: int | None = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    """
    Returns information about the file when parsed as a table, such as column names,
    total rows, numeric columns and a preview of the first 10 rows as a CSV string.
    """
    file = await service.get_file(file_id, current_user)
    file_bytes = await service.get_file_bytes(file)

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

    info = TableInfo(
        columns=df.columns.tolist(),
        total_rows=len(df),
        numeric_columns=df.select_dtypes(include=[np.number]).columns.astype(str).tolist(),
        data=df.head(10).to_csv(),
    )

    return info


@router.patch(
    "/{file_id}/file",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
        409: {"description": "File already exists"},
        413: {"description": "File too large"},
    },
    response_model=FileDB,
)
async def update_file(
    file_id: Annotated[str, Path(title="File Database ID")],
    file: UploadFile = File(...),
    allow_duplicates: bool = Form(False),
    current_user: UserDB = Depends(get_current_app_user),
    file_size: int = Depends(valid_content_length),
) -> FileDB:
    file_db = await service.get_file(file_id, current_user)

    settings = get_settings()
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    LOG.debug(f"File {file.filename} uploaded, size {file_size}")
    # max_file_size = permissions.upload_size_limit_bytes()
    max_file_size = settings.MAX_CONTENT_LENGTH
    if file_size > max_file_size:
        LOG.warning(f"File {file.filename} was too large at size {file_size} and was rejected")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File {file.filename} was too large ({sizeof_fmt(file_size)}).\n"
            + f"The maximum file size is {sizeof_fmt(max_file_size)}",
        )
    file.file.seek(0)

    return await service.replace_file(file_db, file, allow_duplicates)


@router.get(
    "/{file_id}/presigned-url",
    response_model=FileRef,
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
)
async def get_file_link(file_id: str, expire_time_hours: int = 3, current_user=Depends(get_current_app_user)) -> FileRef:
    file = await service.get_file(file_id, current_user)

    client = get_storage_client()
    if file.file_ref.bucket is None or file.file_ref.id is None:
        raise BadRequestError("File reference is incomplete")
    return await client.create_temp_file_url(file.file_ref.bucket, file.file_ref.id, expire_time_hours)


# Delete file route
@router.delete(
    "/{file_id}",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
    response_model=Message,
)
async def delete_file(file_id: str, current_user: UserDB = Depends(get_current_app_user)):
    file = await service.get_file(file_id, current_user)
    file_name = file.file_ref.name
    await service.delete_file(file)

    return Message(message=f"File {file_name} deleted successfully")


@router.patch(
    "/{file_id}",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
    response_model=FileDB,
)
async def update_file_information(
    file_id: Annotated[str, Path(title="File Database ID")],
    update: UpdateFile,
    current_user: UserDB = Depends(get_current_app_user),
) -> FileDB:
    file = await service.get_file(file_id, current_user)
    # TODO: If changing project id the file should get moved to the new project
    return await service.update_file_metadata(file, update)
