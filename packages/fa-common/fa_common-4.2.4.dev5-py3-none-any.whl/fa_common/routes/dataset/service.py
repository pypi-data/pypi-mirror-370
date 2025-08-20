# from typing import List, Literal, Optional, Tuple, overload

# from fa_common import NotFoundError
# from fa_common.exceptions import UnImplementedError
# from fa_common import logger as LOG
# from fa_common.db import Operator, WhereCondition

# from fa_common.routes.dataset import Dataset
# from fa_common.routes.shared import GenericProject, Project
# from fa_common.routes.users import User
# from fa_common.routes.workspace import get_workspace


# class ProjectService:
#     @classmethod
#     def get_project_class(cls):
#         return GenericProject

#     @overload
#     @classmethod
#     async def get_project(
#         cls,
#         user_id: str,
#         workspace_name: str,
#         project_name: str,
#         expected: Literal[True],
#     ) -> Project:
#         ...

#     @overload
#     @classmethod
#     async def get_project(
#         cls, user_id: str, workspace_name: str, project_name: str, expected: bool
#     ) -> Optional[Project]:
#         ...

#     @classmethod
#     async def get_project(
#         cls, user_id: str, workspace_name: str, project_name: str, expected: bool
#     ) -> Optional[Project]:
#         conditions = [
#             WhereCondition(field="user_id", operator=Operator.EQUALS, value=user_id),
#             WhereCondition(field="name", operator=Operator.EQUALS, value=project_name),
#             WhereCondition(field="workspace_name", operator=Operator.EQUALS, value=workspace_name),
#         ]
#         project = await cls.get_project_class().find_one(where=conditions)
#         if expected and project is None:
#             LOG.warning(
#                 f"Project for user: {user_id} with name: {project_name} does not exist but was expected"
#             )
#             raise NotFoundError(f"Project: {project_name} does not exist")
#         return project

#     @classmethod
#     async def update_project(
#         cls, user_id: str, workspace_name: str, project_name: str, project: dict
#     ) -> Project:
#         existing_project = await cls.get_project(
#             user_id,
#             workspace_name,
#             project_name,
#             expected=True,
#         )

#         if existing_project is not None:
#             update_project = existing_project.copy(update=project)

#             await cls.get_project_class().update_one(existing_project.id, update_project.dict())

#         return update_project

#     @classmethod
#     async def delete_project(cls, user_id: str, workspace_name: str, project_name: str):
#         project = await cls.get_project(user_id, workspace_name, project_name, True)
#         await Project.delete(project.id)

#     @classmethod
#     async def create_project(cls, project: dict, datasource: Dataset = None) -> Project:
#         _project = GenericProject(**project)

#         workspace = await get_workspace(_project.user_id, _project.workspace_name, expected=True)
#         assert workspace is not None
#         await _project.save()
#         workspace.link_project(_project.id)
#         await workspace.update_one(workspace.id, workspace.dict())

#         return _project

#     @classmethod
#     async def list_projects(
#         cls, user_id: str, workspace_name: str = None, project_type: str = None
#     ) -> List[Project]:
#         conditions = [WhereCondition(field="user_id", operator=Operator.EQUALS, value=user_id)]
#         if workspace_name is not None:
#             conditions.append(
#                 WhereCondition(
#                     field="workspace_name",
#                     operator=Operator.EQUALS,
#                     value=workspace_name,
#                 )
#             )
#         if project_type is not None:
#             conditions.append(
#                 WhereCondition(
#                     field="project_type",
#                     operator=Operator.EQUALS,
#                     value=project_type.value,
#                 )
#             )

#         projects = await cls.get_project_class().list(where=conditions)

#         return projects

#     @classmethod
#     async def get_test_data(cls, user: User, test_data_name: str) -> Tuple[Project, Optional[Dataset]]:
#         raise UnImplementedError("Raw Project does not have test data")
