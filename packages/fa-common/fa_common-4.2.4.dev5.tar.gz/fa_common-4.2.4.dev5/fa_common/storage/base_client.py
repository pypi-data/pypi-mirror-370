import abc
from io import BytesIO
from typing import List, Optional, Union

from fastapi import UploadFile

from fa_common import get_settings
from fa_common.config import FACommonSettings
from fa_common.models import File


class BaseClient(abc.ABC):
    @abc.abstractmethod
    async def make_bucket(self, name: str) -> None:
        pass

    @abc.abstractmethod
    async def bucket_exists(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    async def delete_bucket(self, name: str):
        pass

    @abc.abstractmethod
    async def list_files(self, bucket_name: str, parent_path: str = "") -> List[File]:
        pass

    @abc.abstractmethod
    async def list_immediate_folders(self, bucket_name: str, parent_path: str = "") -> List[str]:
        # @REVIEW
        pass

    async def get_immediate_folder_names(self, bucket_name: str, parent_path: str = "") -> List[str]:
        # Call the function to list immediate folders
        full_paths = await self.list_immediate_folders(bucket_name, parent_path)

        # Process each path to extract the immediate folder name
        immediate_folder_names = []
        for path in full_paths:
            # Remove the trailing slash (if present)
            trimmed_path = path.rstrip("/")
            # Extract the immediate folder name
            immediate_folder_name = trimmed_path.split("/")[-1]
            immediate_folder_names.append(immediate_folder_name)

        return immediate_folder_names

    @abc.abstractmethod
    async def upload_file(
        self,
        file: UploadFile,
        bucket_name: str,
        parent_path: str = "",
        timeout: int = 60,
    ) -> File:
        pass

    @abc.abstractmethod
    async def upload_string(
        self,
        string: Union[str, bytes],
        bucket_name: str,
        file_path: str,
        content_type="text/plain",
    ) -> File:
        pass

    @abc.abstractmethod
    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        pass

    @abc.abstractmethod
    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        pass

    @abc.abstractmethod
    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        pass

    @abc.abstractmethod
    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        pass

    @abc.abstractmethod
    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        """
        Deletes a file or folder from the specified bucket.

        Arguments:
            bucket_name {str} -- [description]
            file_path {str} -- [description]

        Keyword Arguments:
            recursive {bool} -- Deletes all child & folders files from a non empty folder (default: {False})
        """

    @abc.abstractmethod
    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        pass

    @abc.abstractmethod
    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        pass

    @abc.abstractmethod
    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        """Enable file to be downloaded without auth via a URL temporarily."""

    @classmethod
    @abc.abstractmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        pass

    @classmethod
    def add_user_base_path(cls, user_id: str, sub_path: str) -> str:
        # @REVIEW: This is just a common function across all
        # clients. So, I've put the logic here.
        st = get_settings()
        # Added below trim as sometime an extra "/" could mess things up.
        trim_path = f"{st.BUCKET_USER_FOLDER}/{user_id}/{sub_path}".replace("//", "/")
        return trim_path

    @classmethod
    def add_project_base_path(cls, project_id: str, sub_path: str) -> str:
        # @REVIEW: This is just a common function across all
        # clients. So, I've put the logic here.
        st = get_settings()
        # Added below trim as sometime an extra "/" could mess things up.
        trim_path = f"{st.BUCKET_PROJECT_FOLDER}/{project_id}/{sub_path}".replace("//", "/")
        return trim_path

    @classmethod
    def get_standard_workflow_upload_path_project(cls, project_id):
        st: FACommonSettings = get_settings()
        return cls.add_project_base_path(project_id, st.WORKFLOW_UPLOAD_PATH)

    @classmethod
    def get_standard_workflow_upload_path_user(cls, user_id):
        st: FACommonSettings = get_settings()
        return cls.add_user_base_path(user_id, st.WORKFLOW_UPLOAD_PATH)

    @classmethod
    def reset_instance(cls):
        """Resets the instance. This is used to reset the client in tests."""
        return
