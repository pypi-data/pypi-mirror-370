# from typing import List, Union

# from fa_common import NotFoundError
# from fa_common import logger as LOG
# from fa_common.db import Operator, WhereCondition, get_db_client
# from fastapi.encoders import jsonable_encoder
# from pydantic import ValidationError

# from fa_common.routes.shared import Project, ProjectStatus

# from .models import ProjectSZ
# from .service import ProjectService


# def serialise_model(model: Project) -> dict:
#     return jsonable_encoder(model.dict(by_alias=True))


# def get_project_service(project_type: str) -> ProjectService:
#     return ProjectService()


# async def dict_to_project(project_dict: dict, sz: bool = False) -> Project:
#     project_type = project_dict.get("project_type")
#     if project_type is None:
#         project_type = project_dict.get("dataType")
#     assert project_type is not None, "Trying to convert a project dictionary with no 'dataType' value."

#     if project_dict["status"] is not ProjectStatus.ERROR:
#         try:
#             if not sz:
#                 from fa_common.project.models import GenericProject as Generic
#             else:
#                 from fa_common.project.models import GenericProjectSZ as Generic  # type: ignore

#             return Generic(**project_dict)
#         except ValidationError as err:
#             LOG.warning(f"Project {project_dict.get('id')} has serialisation errors.")
#             LOG.error(str(err))
#             project_dict["status"] = ProjectStatus.ERROR
#             await Project.update_one(project_dict.get("id"), project_dict)

#     if not sz:
#         return Project(**project_dict)
#     else:
#         return ProjectSZ(**project_dict)


# async def get_project_dicts_for_user(
#     user_id: str,
#     workspace_name: str = None,
#     project_type: str = None,
#     client_format=False,
# ) -> List[dict]:
#     conditions = [WhereCondition(field="user_id", operator=Operator.EQUALS, value=user_id)]
#     if workspace_name is not None:
#         conditions.append(
#             WhereCondition(field="workspace_name", operator=Operator.EQUALS, value=workspace_name)
#         )
#     if project_type is not None:
#         conditions.append(
#             WhereCondition(field="project_type", operator=Operator.EQUALS, value=project_type.value)
#         )
#     results = await get_db_client().list_dict(Project.get_db_collection(), conditions)
#     if client_format:
#         client_list = [(await dict_to_project(res, sz=True)).dict(by_alias=True) for res in results]

#         return jsonable_encoder(client_list)

#     return results


# async def get_projects_for_user(
#     user_id: str, workspace_name: str = None, project_type: str = None, sz=False
# ) -> List[Project]:
#     projects = await get_project_dicts_for_user(user_id, workspace_name, project_type)

#     return [await dict_to_project(ds, sz=sz) for ds in projects]


# async def get_project_dict_for_user(
#     user_id: str,
#     workspace_name: str,
#     project_name: str,
#     client_format=False,
#     expected: bool = False,
# ) -> dict:
#     db = get_db_client()
#     conditions = [
#         WhereCondition(field="user_id", operator=Operator.EQUALS, value=user_id),
#         WhereCondition(field="workspace_name", operator=Operator.EQUALS, value=workspace_name),
#         WhereCondition(field="name", operator=Operator.EQUALS, value=project_name),
#     ]
#     project = await db.find_one_dict(Project.get_db_collection(), where=conditions)
#     if expected and project is None:
#         raise NotFoundError(f"Project: {project_name} does not exist in workspace: {workspace_name}")
#     if client_format:
#         return jsonable_encoder((await dict_to_project(project, sz=True)).dict(by_alias=True))
#     return project


# async def get_project_for_user(
#     user_id: str,
#     workspace_name: str,
#     project_name: str,
#     sz=False,
#     expected: bool = False,
# ) -> Project:

#     return await dict_to_project(
#         await get_project_dict_for_user(user_id, workspace_name, project_name, expected=expected),
#         sz=sz,
#     )


# async def delete_projects_for_user(
#     user_id: str, workspace_name: str = None, project_type: str = None
# ) -> bool:

#     projects = await get_projects_for_user(user_id, workspace_name, project_type)

#     if len(projects) > 0:
#         for project in projects:
#             service = get_project_service(project.project_type)
#             await service.delete_project(user_id, project.workspace_name, project.name)

#     return True
