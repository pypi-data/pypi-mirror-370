# from fa_common import HTTPException
# from fa_common import logger as LOG
# from fastapi import APIRouter, Depends, Path, Query
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import ORJSONResponse

# from fa_common.routes.dataset import get_dataset
# from fa_common.routes.shared import Message
# from fa_common.routes.users import User, get_current_user

# from .models import CreateProjectRequest, GenericProjectSZ
# from .service import ProjectService
# from .utils import dict_to_dataset, get_dataset_dict_for_user, get_dataset_dicts_for_user, get_dataset_service

# router = APIRouter()


# async def get_dataset_response(dataset_dict: dict):
#     response_content = (await dict_to_dataset(dataset_dict, sz=True)).dict(by_alias=True)
#     status_code = 200
#     return ORJSONResponse(
#         status_code=status_code,
#         content=jsonable_encoder(response_content),
#     )


# @router.get("/{workspace_name}")
# async def list_datasets(
#     workspace_name: str = Path(..., regex="^[0-9a-zA-Z_]+$"),
#     dataset_type: str = Query(None, title="Project Type", description="Filter by Datatype"),
#     current_user: User = Depends(get_current_user),
# ):
#     """List Users Projects"""
#     return await get_dataset_dicts_for_user(current_user.id, workspace_name, dataset_type, client_format=True)


# @router.get(
#     "/{workspace_name}/{dataset_name}",
#     ## Your model response goes here
#     response_model=GenericProjectSZ.response_model,
#     responses={
#         404: {"description": "Project not found"},
#     },
# )  # type: ignore
# async def get_dataset(
#     workspace_name: str = Path(..., regex="^[0-9a-zA-Z_ ]+$"),
#     dataset_name: str = Path(..., regex="^[0-9a-zA-Z_ ]+$"),
#     current_user: User = Depends(get_current_user),
# ):
#     """Gets a dataset given the dataset_name"""
#     dataset = await get_dataset_dict_for_user(current_user.id, workspace_name, dataset_name, expected=True)
#     return await get_dataset_response(dataset)


# @router.delete(
#     "/{workspace_name}/{dataset_name}",
#     response_model=Message,
#     responses={404: {"description": "Project not found"}},
# )
# async def delete_dataset(
#     workspace_name: str = Path(..., regex="^[0-9a-zA-Z_ ]+$"),
#     dataset_name: str = Path(..., regex="^[0-9a-zA-Z_ ]+$"),
#     current_user: User = Depends(get_current_user),
# ) -> Message:
#     """Deletes a dataset given the dataset_name"""
#     dataset = await ProjectService.get_dataset(current_user.id, workspace_name, dataset_name, True)
#     service = get_dataset_service(dataset.dataset_type)
#     await service.delete_dataset(current_user.id, workspace_name, dataset_name)
#     return Message(message=f"Deleted dataset {dataset_name}.")


# @router.put(
#     "",
#     ## Your model response goes here
#     response_model=GenericProjectSZ.response_model,
#     responses={
#         404: {"description": "Project not found"},
#     },
# )
# async def update_dataset(
#     dataset: GenericProjectSZ,
#     current_user: User = Depends(get_current_user),
# ):
#     service = get_dataset_service(dataset.dataset_type)
#     data_dict = dataset.dict(exclude_unset=True)
#     dataset_name = data_dict["name"]
#     workspace_name = data_dict["workspace_name"]
#     updated_dataset = await service.update_dataset(current_user.id, workspace_name, dataset_name, data_dict)

#     return await get_dataset_response(updated_dataset.dict())


# @router.post(
#     "",
#     ## Your model response goes here
#     response_model=GenericProjectSZ.response_model,
#     responses={
#         409: {"description": "Project already exists in the workspace"},
#     },
# )
# async def create_dataset(
#     create: CreateProjectRequest,
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new dataset that has already had the config and data uploaded to GCP.
#     Note datasetId can be sent via json or the uri"""
#     data_dict = create.dataset.dict()
#     data_dict["user_id"] = current_user.id
#     dataset = await ProjectService.get_dataset(
#         current_user.id, data_dict["workspace_name"], data_dict["name"], False
#     )

#     if dataset is not None:
#         if not create.override:
#             raise HTTPException(
#                 status_code=409,
#                 detail=f"Project {data_dict['name']} already exists in workspace "
#                 + f"{data_dict['workspace_name']}",
#             )
#         service = get_dataset_service(dataset.dataset_type)
#         LOG.info(f"Deleting dataset {data_dict['name']} due to override on create.")
#         await service.delete_dataset(current_user.id, data_dict["workspace_name"], data_dict["name"])

#     service = get_dataset_service(data_dict["dataset_type"])
#     dataset = None
#     if data_dict.get("dataset_ref", None) is not None:
#         dataset = await get_dataset(current_user.id, data_dict["dataset_ref"])
#     created_dataset = await service.create_dataset(data_dict, dataset)

#     return await get_dataset_response(created_dataset.dict())
