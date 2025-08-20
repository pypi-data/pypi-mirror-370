from typing import List, Optional, Tuple

from beanie.operators import ElemMatch, In, Or, RegEx
from bson import ObjectId

from fa_common import AlreadyExistsError, NotFoundError, UnauthorizedError
from fa_common import logger as LOG
from fa_common.auth.utils import get_admin_scope
from fa_common.routes.files.service import delete_files_for_project
from fa_common.routes.tables.service import delete_project_tables
from fa_common.routes.user.models import UserDB
from fa_common.storage import get_storage_client
from fa_common.utils import validate_id

from .models import CreateAdminProject, ProjectDB, UpdateProject


async def get_project_by_name(user: UserDB, project_name: str, expected: bool = True) -> Optional[ProjectDB]:
    """[summary].
    Arguments:
        user_id {str} -- [description]
        project_name {str} -- [description]
    Keyword Arguments:
        expected {bool} -- [description] (default: {True})
    Raises:
        NotFoundError: When project is expected but does not exist
    """
    # Allow matching on either user.sub or user.id
    user_identifiers = [user.sub, str(user.id)]
    query = ProjectDB.find(In(ProjectDB.user_id, user_identifiers))

    project = await query.find(ProjectDB.name == project_name).first_or_none()
    if expected and project is None:
        LOG.warning(f"Project for user: {user.name} with name: {project_name} does not exist but was expected")
        raise NotFoundError(f"Project: {project_name} does not exist")
    if project is not None and not isinstance(project, ProjectDB):
        raise ValueError(f"Project: {project_name} was found but its type is invalid.")
    return project


async def create_project(user: UserDB, project: dict) -> ProjectDB:
    project_name = project.get("name")
    if project_name is None:
        raise ValueError("No project name was given")
    project_obj = await get_project_by_name(user, project_name, expected=False)
    if project_obj is None:
        # wp = await create_workflow_project(user.sub, project_name, storage=storage)
        project_obj = ProjectDB(
            user_id=user.sub,
            **project,
        )
        await project_obj.initialise_project()
        client = get_storage_client()
        if (
            project_obj.storage is not None
            and project_obj.storage.bucket_name is not None
            and not await client.bucket_exists(project_obj.storage.bucket_name)
        ):
            await client.make_bucket(project_obj.storage.bucket_name)
            LOG.info(f"Created bucket {project_obj.storage.bucket_name}")
        LOG.info(f"ProjectDB {project_obj.id}")
    else:
        raise AlreadyExistsError(
            f"You are already the owner of a project named {project_obj.name}, duplicate project names are not allowed."
        )
    return project_obj


async def create_admin_project(user: UserDB, project: CreateAdminProject) -> ProjectDB:
    admin_project = await create_project(user, project.model_dump(exclude={"permissions"}))
    admin_project.apply_permissions(project.permissions)
    await admin_project.save()
    return admin_project


async def update_project(
    project: ProjectDB,
    update: UpdateProject,
) -> ProjectDB:
    if project is None or project.id is None:
        raise NotFoundError("Project does not exist")
    update_project = project.model_copy(update=update.get_update_dict())
    if update.add_tags is not None:
        update_project.tags.extend(update.add_tags)
    if update.add_project_users is not None:
        update_project.project_users.extend(update.add_project_users)

    await update_project.save()
    return update_project


async def delete(project_id: ObjectId, user_sub: str | None = None) -> bool:
    """Deletes all stored data for a given project.
    Arguments:
        user_token {[str]} -- [user]
        project_name {[str]} -- [project]
    Returns:
        [bool] -- [True if a project was deleted false if it didn't exist]
    """
    project = await ProjectDB.find_one(ProjectDB.id == project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} does not exist")
    elif user_sub is not None and project.user_id != user_sub:
        raise UnauthorizedError(f"Project {project_id} does not belong to user {user_sub}")

    await delete_project_tables(project.id)
    await delete_files_for_project(project.id)

    storage_client = get_storage_client()
    if project.storage is not None and await storage_client.bucket_exists(project.storage.bucket_name):
        try:
            await storage_client.delete_file(project.storage.bucket_name, project.storage.path_prefix, True)
            LOG.info(f"Deleted project folder {project.storage.storage_full_path}")
        except Exception as err:
            if await storage_client.file_exists(project.storage.bucket_name, project.storage.path_prefix):
                raise err
    if project is not None:
        await project.delete()
        return True
    return False


async def get_projects_for_user(
    user: UserDB,
    owner_only=False,
    offset: int = 0,
    limit: int = 10,
    sort: list[str] = [],
    search: Optional[str] = None,
    tag: Optional[str] = None,
    include_public: bool = False,
) -> Tuple[List[ProjectDB], int]:
    """Get projects for a user.

    Parameters
    ----------
    user : UserDB
        The user's database object.
    owner_only : bool, optional
        If True, only return projects owned by the user. Default is False.
    offset : int, optional
        The number of projects to skip before returning results. Default is 0.
    limit : int, optional
        The maximum number of projects to return. Default is 10.
    sort : list[str], optional
        The list of fields to sort the projects by using the syntax `['+fieldName', '-secondField']`.
        See https://beanie-odm.dev/tutorial/finding-documents/
        Default is an empty list.
    search : Optional[str], optional
        Search string to filter projects by name or tags. Default is None.
    tag : Optional[str], optional
        Filter by exact tag match. This is case insensitive and matches against both tags and system_tags. Default is None.

    Returns
    -------
    Tuple[List[ProjectDB], int]
        A tuple containing the list of projects and the total count of projects matching the criteria.
    """
    # Allow matching on either user.sub or user.id
    user_identifiers = [user.sub, str(user.id)]

    if owner_only:
        query = ProjectDB.find(In(ProjectDB.user_id, user_identifiers))
    else:
        if get_admin_scope() in user.roles:
            expressions = [{}]
        else:
            expressions = [
                In(ProjectDB.user_id, user_identifiers),
                {"projectUsers": {"$elemMatch": {"$regex": f"^{user.email}$", "$options": "i"}}},
            ]
        if include_public:
            expressions.append({"isPublic": True})
        query = ProjectDB.find(Or(*expressions))

    # Apply search filter if provided
    if search:
        # Create a regex search for name or tags
        search_regex = RegEx(ProjectDB.name, search, "i")  # Case-insensitive search anywhere in name
        query = query.find(Or(search_regex, ElemMatch(ProjectDB.tags, {"$regex": f"{search}", "$options": "i"})))

    # Apply tag filter if provided
    if tag:
        # Case insensitive exact match on tag in either tags or system_tags
        tag_query = {"$or": [{"tags": {"$regex": f"^{tag}$", "$options": "i"}}, {"systemTags": {"$regex": f"^{tag}$", "$options": "i"}}]}
        query = query.find(tag_query)

    # Get total count before applying pagination
    total_count = await query.count()

    # Apply sorting
    if sort:
        query = query.sort(*sort)

    # Apply pagination
    results = await query.skip(offset).limit(limit).to_list()

    return results, total_count


async def get_project_for_user(
    user: UserDB,
    project_id: str | ObjectId,
    check_owner: bool = False,
) -> ProjectDB:
    """[summary].
    Arguments:
        user_token {str} -- [description]
    Returns:
        [type] -- [description]
    """
    valid_id = validate_id(project_id)
    project = await ProjectDB.get(valid_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} could not be found")
    if not await project.user_has_access(user) and get_admin_scope() not in user.scopes:
        raise UnauthorizedError(f"User {user.name} does not have access to project {project.name}")
    if check_owner and (str(project.user_id) != str(user.id) and str(project.user_id) != user.sub):
        raise UnauthorizedError(f"User {user.name} is not the owner of project {project.name}")
    return project


async def delete_projects_for_user(user: UserDB) -> bool:
    """[summary].
    Arguments:
        user_token {str} -- [description]
    Returns:
        [type] -- [description]
    """
    projects, _ = await get_projects_for_user(user, owner_only=True, limit=100)
    if len(projects) > 0:
        for project in projects:
            if project.id:
                await delete(project.id, user.sub)
    return True
