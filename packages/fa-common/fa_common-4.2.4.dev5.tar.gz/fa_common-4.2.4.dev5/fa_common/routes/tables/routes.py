from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, Query, Response

from fa_common import (
    BadRequestError,
    Message,
)
from fa_common.models import PaginationListResponse
from fa_common.routes.files.service import get_file
from fa_common.routes.user.models import UserDB
from fa_common.routes.user.service import get_current_app_user

from . import service
from .models import CreateTable, TableItem, UpdateTable

router = APIRouter()


@router.get("", response_model=PaginationListResponse[TableItem])
async def list_tables(
    onlyMine: bool = True,
    limit: int = 10,
    offset: int = 0,
    project: Annotated[list[str] | None, Query()] = None,
    startWith: str | None = None,
    exactName: str | None = None,
    data: bool = False,
    sort: Annotated[list[str] | None, Query()] = None,
    current_user: UserDB = Depends(get_current_app_user),
) -> PaginationListResponse[TableItem]:
    tables = await service.get_tables_for_user(
        user=current_user,
        owner_only=onlyMine,
        offset=offset,
        limit=limit,
        project_ids=project,
        start_with=startWith,
        exact_name=exactName,
        include_data=data,
        sort=sort,
    )

    return tables  # type: ignore


@router.get(
    "/{table_id}/data",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "Table not found"},
        403: {"description": "Access Denied"},
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {"schema": {"type": "object"}},
                "text/csv": {"schema": {"type": "string", "format": "binary"}},
            },
        },
    },
)
async def get_table_data(
    table_id: str,
    limit: int = 100,
    offset: int = 0,
    sort: list[str] | None = Query(None, description="+/- and column name e.g. +column1"),
    accept: str = Header(None, alias="Accept"),
    current_user: UserDB = Depends(get_current_app_user),
):
    table = await service.get_table(table_id, current_user, include_data=True)

    paging_frame = await service.get_paging_frame_from_table(table, offset=offset, limit=limit, sort=sort)

    response_format = "json"
    if "application/json" in accept.lower():
        # Handle JSON response
        response_format = "json"
    elif "text/csv" in accept.lower():
        # Handle CSV response
        response_format = "csv"
    # TODO: Is orient by records ideal?
    return (
        PaginationListResponse[dict](values=paging_frame[0].to_dict(orient="records"), total=paging_frame[1], offset=offset, limit=limit)
        if response_format == "json"
        else Response(paging_frame[0].to_csv(index=False), media_type="text/csv")
    )


@router.put(
    "",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
    response_model=TableItem,
)
async def create_table(
    create: CreateTable,
    current_user: UserDB = Depends(get_current_app_user),
):
    file = await get_file(create.file_id, current_user)
    return await service.create_table_from_file(file, create, current_user)


@router.get(
    "/{table_id}",
    response_model=TableItem,
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "Table not found"},
        403: {"description": "Access Denied"},
    },
)
async def get_table(
    table_id: str,
    include_data: bool = False,
    current_user: UserDB = Depends(get_current_app_user),
):
    table = await service.get_table(table_id, current_user, include_data=include_data)
    return table


# Delete file route
@router.delete(
    "/{table_id}",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
    response_model=Message,
)
async def delete_table(table_id: str, current_user: UserDB = Depends(get_current_app_user)):
    table = await service.get_table(table_id, current_user, include_data=False)
    table_name = table.name
    await service.delete_table(table)

    return Message(message=f"Table {table_name} deleted successfully")


@router.patch(
    "/{table_id}",
    responses={
        400: {"description": "Incorrectly formatted ID"},
        404: {"description": "File not found"},
        403: {"description": "Access Denied"},
    },
    response_model=TableItem,
)
async def update_table(
    table_id: str,
    update: Annotated[UpdateTable, Body(embed=True)],
    current_user: UserDB = Depends(get_current_app_user),
):
    """Update table metadata and optionally replace data if fileId is provided.

    This endpoint can be used to:
    1. Update table metadata such as tags, users, project
    2. Replace table data with a new file (if fileId is provided)
    """
    table = await service.get_table(table_id, current_user, include_data=True)
    return await service.update_table(table, update, current_user)


@router.get("/{table_id}/columns", response_model=list[str])
async def get_column_names(
    table_id: str,
    numeric_only: bool = False,
    current_user: UserDB = Depends(get_current_app_user),
):
    """List Names of columns."""
    table = await service.get_table(table_id, current_user, include_data=False)

    if numeric_only:
        return table.numeric_columns
    return table.columns


@router.get("/{table_id}/column/{column_name}", response_model=list[str])
async def get_column_values(
    table_id: str,
    column_name: str,
    unique: bool = False,
    offset: int = 0,
    limit: int | None = None,
    current_user: UserDB = Depends(get_current_app_user),
):
    """Get a specific column from an active data frame."""

    table = await service.get_table(table_id, current_user, include_data=False)
    frame, total = await service.get_paging_frame_from_table(table, offset=offset, limit=limit)
    if column_name not in frame.columns:
        raise BadRequestError(f"Column {column_name} not found in table {table_id}")

    return list(frame[column_name].unique()) if unique else list(frame[column_name])
