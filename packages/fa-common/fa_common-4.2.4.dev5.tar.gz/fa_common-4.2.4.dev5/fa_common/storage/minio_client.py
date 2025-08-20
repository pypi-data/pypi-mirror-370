from datetime import timedelta
from io import BytesIO
from typing import List, Optional, Union

import aiohttp
from fastapi import UploadFile
from miniopy_async import Minio
from miniopy_async.commonconfig import CopySource
from miniopy_async.datatypes import Object
from miniopy_async.deleteobjects import DeleteObject
from miniopy_async.error import MinioException

from fa_common import StorageError, get_current_app, get_settings, sizeof_fmt
from fa_common import logger as LOG
from fa_common.models import File

from .base_client import BaseClient

settings = get_settings()


class MinioClient(BaseClient):
    """
    Singleton client for interacting with Minio. Note we are wrapping all the call in threads to
    enable async support to a sync library.
    Please don't use it directly, use `core.storage.utils.get_storage_client`.
    """

    __instance = None
    minio: Minio

    def __new__(cls) -> "MinioClient":
        """
        Get called before the constructor __init__ and allows us to return a singleton instance.

        Returns:
            [MinioClient] -- [Singleton Instance of client]
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.minio = app.minio  # type: ignore
        return cls.__instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance. Useful for testing or reinitialization."""
        cls.__instance.minio = None  # type: ignore
        cls.__instance = None

    async def make_bucket(self, name: str) -> None:
        try:
            if settings.STORAGE_REGION is None:
                raise ValueError("STORAGE_REGION is not set in settings")

            await self.minio.make_bucket(name, location=settings.STORAGE_REGION)
        except MinioException as err:
            if getattr(err, "code", "") == "BucketAlreadyOwnedByYou":
                LOG.warning(f"Bucket {name} already owned by app")
                return
            if getattr(err, "code", "") == "BucketAlreadyExists":
                LOG.warning(f"Bucket {name} already exists")
                return

            LOG.error(f"Unable to create bucket {name}")
            LOG.error(err)
            raise err

    async def bucket_exists(self, name: str) -> bool:
        return await self.minio.bucket_exists(name)

    @classmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        # @REVIEW: above was not providing the full uri.
        # below will probably not cover all minio cases.
        # possible solutions: adding addtional optional
        # entry (e.g. prefix) or have an ENV var for it?
        settings = get_settings()
        if settings.STORAGE_ENDPOINT == "s3.amazonaws.com":
            full_path = f"{bucket_name}/{path}".replace("//", "/")
            return f"s3://{full_path}"

        if settings.STORAGE_SSL:
            return f"https://{bucket_name}.{settings.STORAGE_ENDPOINT}/{path}"
        else:
            return f"http://{bucket_name}.{settings.STORAGE_ENDPOINT}/{path}"

    @classmethod
    def object_to_file(cls, obj: Object, bucket_name: str, file_name: str | None = None) -> Optional[File]:
        is_dir = obj.is_dir
        path = obj.object_name
        path_segments = path.split("/") if path is not None else []

        if is_dir:
            if len(path_segments) == 1:
                return None
            path_segments = path_segments[:-1]

        name = path_segments[-1]
        path = "/".join(path_segments[:-1])

        LOG.debug("Converting Minio Object: {}", obj)

        return File(
            id=obj.object_name,
            bucket=bucket_name,
            url="s3://" + f"{obj.bucket_name}/{obj.object_name}".replace("//", "/"),
            size=sizeof_fmt(obj.size),
            size_bytes=obj.size,
            dir=is_dir,
            path=path,
            name=name,
            content_type=obj.content_type,
        )

    async def list_files(self, bucket_name: str, parent_path: str = "") -> list[File]:
        objects = await self.minio.list_objects(bucket_name, prefix=parent_path)
        files: List[File] = []
        if objects is None:
            return files
        for obj in objects:
            file = self.object_to_file(obj, bucket_name)
            if file is not None:
                files.append(file)
        return files

    async def list_immediate_folders(self, bucket_name: str, parent_path: str = "") -> list[str]:
        # @REVIEW: Ben. M.: Added this method.
        # Ensure parent_path ends with '/' if it's not empty
        if parent_path and not parent_path.endswith("/"):
            parent_path += "/"

        # Initialize the folders list
        folders: list[str] = []

        # Use the list_objects method with the delimiter parameter set to '/'
        objects = await self.minio.list_objects(
            bucket_name,
            prefix=parent_path,
            recursive=False,
            include_user_meta=False,
            include_version=False,
            use_api_v1=False,
        )
        if objects is not None:
            for obj in objects:
                # Assuming obj is an instance of Object or a similar class that indicates directories differently
                # Typically, directories (or prefixes) might end with '/' in their names
                if obj.object_name is not None and (obj.is_dir or obj.object_name.endswith("/")):
                    folders.append(obj.object_name)

        return folders

    async def upload_string(
        self,
        string: Union[str, bytes],
        bucket_name: str,
        file_path: str,
        content_type="text/plain",
    ) -> File:
        try:
            string_io: BytesIO = BytesIO(string.encode("utf-8")) if isinstance(string, str) else BytesIO(string)
            await self.minio.put_object(
                bucket_name,
                file_path,
                string_io,
                len(string),
                content_type=content_type,
            )

        except MinioException as err:
            LOG.error(str(err))
            raise StorageError(f"Something went wrong uploading file {file_path}") from err
        obj = await self.minio.stat_object(bucket_name, file_path)
        scidra_file = self.object_to_file(obj, bucket_name, file_path)
        if scidra_file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return scidra_file

    async def upload_file(
        self,
        file: UploadFile,
        bucket_name: str,
        parent_path: str = "",
        timeout: int = 60,
    ) -> File:
        # We can't directly set timeout for put_object, but we'll log it for reference
        LOG.info(
            "Note: Timeout parameter ({} seconds) is received but Minio put_object doesn't directly support it",
            timeout,
        )

        if parent_path != "":
            parent_path += "/"
        try:
            # Configure the Minio client with timeout settings if possible
            # Note: miniopy_async doesn't expose direct timeout controls for put_object
            await self.minio.put_object(
                bucket_name,
                f"{parent_path}{file.filename}",
                file.file,
                -1,
                part_size=10 * 1024 * 1024,
            )
        except MinioException as err:
            LOG.error(str(err))
            raise StorageError(f"Something went wrong uploading file {parent_path}{file.filename}") from err
        obj = await self.minio.stat_object(bucket_name, f"{parent_path}{file.filename}")
        scidra_file = self.object_to_file(obj, bucket_name, f"{parent_path}{file.filename}")
        if scidra_file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return scidra_file

    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        obj_ref = await self.minio.stat_object(bucket_name, file_path)
        return self.object_to_file(obj_ref, bucket_name)

    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        try:
            async with aiohttp.ClientSession() as session:
                response = await self.minio.get_object(bucket_name, file_path, session=session)
                if response.status >= 400:
                    raise MinioException(f"get_object returned response code {response.status}")

                return BytesIO(await response.read())
        except MinioException as err:
            if getattr(err, "code", "") == "NoSuchKey":
                return None
            # Likely the file doesn't exist
            LOG.error(str(err))
            raise StorageError(f"Error getting file {file_path}") from err

    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        try:
            stats = await self.minio.stat_object(bucket_name, file_path)
            return stats is not None
        except MinioException as err:
            if getattr(err, "code", "") == "NoSuchKey":
                return False
            LOG.error(str(err))
            raise StorageError(f"Error checking if {file_path} exists") from err

    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        objects = await self.minio.list_objects(bucket_name, prefix=path, recursive=False)
        if objects is None:
            return False
        return any(obj is not None for obj in objects)

    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        try:
            if recursive:
                object_list = await self.minio.list_objects(bucket_name, file_path, recursive=True)
                if object_list is not None:
                    delete_object_list = (DeleteObject(x.object_name) for x in object_list if x.object_name is not None)
                    errors = await self.minio.remove_objects(bucket_name, delete_object_list)
                    for error in errors:
                        LOG.error(f"Error occurred when deleting file(s) {error}")
            else:
                await self.minio.remove_object(bucket_name, file_path)
        except MinioException as err:
            LOG.error(err)
            raise StorageError(f"Something went wrong deleting file(s) {bucket_name}/{file_path}") from err

    async def delete_bucket(self, name: str):
        try:
            await self.delete_file(name, "", True)
            return await self.minio.remove_bucket(name)
        except MinioException as err:
            LOG.error(f"Unable to delete bucket {name}")
            LOG.error(err)
            raise err

    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        try:
            await self.minio.copy_object(bucket_name, new_file_path, CopySource(bucket_name, file_path))
        except MinioException as err:
            LOG.error(f"Error renaming {file_path} to {new_file_path} in bucket {bucket_name}: {err!s}")
            raise StorageError(f"Something went wrong renaming {file_path} to {new_file_path}") from err
        await self.delete_file(bucket_name, file_path)
        obj = await self.minio.stat_object(bucket_name, new_file_path)
        file = self.object_to_file(obj, bucket_name, new_file_path)
        if file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return file

    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        try:
            await self.minio.copy_object(to_bucket, to_path, CopySource(from_bucket, from_path))
        except MinioException as err:
            LOG.error(f"Error copying {from_bucket} {from_path} to {to_bucket} {to_path} : {err!s}")
            raise StorageError(f"Something went wrong copying {from_path} to {to_path}") from err

    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        try:
            file_ref = await self.get_file_ref(bucket, path)
            if file_ref is None:
                raise StorageError(f"File {bucket}/{path} does not exist")
            url = await self.minio.presigned_get_object(bucket, path, timedelta(hours=expire_time_hours))
            file_ref.public_url = url
            return file_ref
        except MinioException as err:
            LOG.error(f"Error creating a presignedurl for {bucket}/{path}")
            raise StorageError(f"Error creating a presigned url for {bucket}/{path}") from err
