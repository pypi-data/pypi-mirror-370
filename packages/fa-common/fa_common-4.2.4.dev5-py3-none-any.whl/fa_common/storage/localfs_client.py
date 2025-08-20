from io import BytesIO
from pathlib import Path
from typing import List, Optional, Union

import aiofiles
import aiofiles.os
from aioshutil import copy, rmtree
from fastapi import UploadFile

from fa_common import StorageError, get_current_app, sizeof_fmt
from fa_common import logger as LOG
from fa_common.config import get_settings
from fa_common.exceptions import UnImplementedError
from fa_common.models import File

from .base_client import BaseClient


class LocalFSClient(BaseClient):
    """
    Singleton client for interacting with the local filesystem.
    Please don't use it directly, use `core.storage.utils.get_storage_client`.
    """

    __instance = None
    root_path: Path = Path(get_settings().LOCALFS_STORAGE_PATH)  # type: ignore

    def __new__(cls) -> "LocalFSClient":
        """
        Get called before the constructor __init__ and allows us to return a singleton instance.

        Returns:
            [LocalFSClient] -- [Singleton Instance of client]
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.root_path = app.storage_root_path  # type: ignore
        return cls.__instance

    async def make_bucket(self, name: str) -> None:
        try:
            bucket_path: Path = self.root_path / name
            await aiofiles.os.mkdir(bucket_path)
        except FileExistsError:
            LOG.warning(f"Bucket {name} already exists")

    async def bucket_exists(self, name: str) -> bool:
        bucket_path: Path = self.root_path / name
        return await aiofiles.os.path.exists(bucket_path)

    async def delete_bucket(self, name: str):
        try:
            bucket_path: Path = self.root_path / name
            await rmtree(str(bucket_path))
        except OSError as err:
            LOG.warning(f"Unable to delete Bucket: {name}")
            raise StorageError(f"Unable to delete Bucket:: {name}") from err

    async def _get_bucket(self, name: str) -> Path:
        """Internal method to level bucket."""
        bucket_path: Path = self.root_path / name
        if await self.bucket_exists(name) is False:
            LOG.error("Trying to get bucket {} that doesn't exist", bucket_path)
            raise StorageError(f"Trying to get bucket {bucket_path} that doesn't exist")
        else:
            return bucket_path

    # async def _get_blob(self, bucket_name, path):
    #     """
    #     Internal method to get GCP blob reference
    #     """
    #     # bucket = self.gcp_storage.bucket(bucket_name)
    #     bucket = await self._get_bucket(bucket_name)
    #     return bucket.blob(self.convert_path_in(path, bucket_name))

    # async def _list_blobs(self, bucket_name, prefix) -> Iterator[Blob]:
    #     bucket = await self._get_bucket(bucket_name)
    #     return await force_async(bucket.list_blobs)(prefix=self.convert_path_in(prefix, bucket_name))

    @classmethod
    def convert_path_in(cls, path: str, bucket_name) -> str:
        return path

    @classmethod
    def convert_path_out(cls, path: str, bucket_name) -> str:
        return path

    @classmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        return str(cls.root_path / bucket_name / path)

    @classmethod
    async def fs_file_to_file(cls, file_path: Path) -> File:
        is_dir = await aiofiles.os.path.isdir(file_path)
        path = str(file_path)
        path_segments = path.split("/")
        bucket = path_segments[0] if len(path_segments) > 1 else "/"
        if is_dir and len(path_segments) > 1:
            path_segments = path_segments[0:-1]

        name = path_segments[-1]
        path = "/".join(path_segments[1:-1])

        stat = await aiofiles.os.stat(file_path)

        return File(
            id=file_path.name,
            url=str(file_path),
            bucket=bucket,
            size=sizeof_fmt(stat.st_size),
            size_bytes=stat.st_size,
            dir=is_dir,
            path=path,
            name=name,
            content_type="".join(file_path.suffixes),
        )

    async def list_files(self, bucket_name: str, parent_path: str = "") -> List[File]:
        files: List[File] = []

        bucket_path = await self._get_bucket(bucket_name)
        glob_string = parent_path + "/**/*" if parent_path else "**/*"
        fs_files = bucket_path.glob(glob_string)

        for fs_file in fs_files:
            file = await self.fs_file_to_file(fs_file)
            if file is not None:
                files.append(file)

        return files

    async def upload_string(
        self,
        string: Union[str, bytes],
        bucket_name: str,
        file_path: str,
        content_type="text/plain",
    ) -> File:
        bucket_path = await self._get_bucket(bucket_name)
        insert_path = bucket_path / file_path

        # We just overwrite anything already there
        try:
            async with aiofiles.open(insert_path, mode="wb") as f:
                if isinstance(string, (bytes, bytearray)):
                    await f.write(string)
                else:
                    await f.write(string.encode("utf-8"))  # type: ignore
        except OSError as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploading string {}", file_path) from err

        scidra_file = await self.fs_file_to_file(insert_path)
        if scidra_file is None:
            raise StorageError("A file could not be created from the filesystem")
        return scidra_file

    async def upload_file(
        self,
        file: UploadFile,
        bucket_name: str,
        parent_path: str = "",
        timeout: int = 60,
    ) -> File:
        bucket_path = await self._get_bucket(bucket_name)
        path = self.convert_path_in(parent_path, bucket_name)
        parent_path = str(bucket_path / path)
        if not file.filename:
            raise StorageError("File name is empty")
        file_path = bucket_path / path / file.filename
        try:
            file.file.seek(0)
            await aiofiles.os.makedirs(parent_path, exist_ok=True)
            async with aiofiles.open(file_path, mode="wb") as f:
                await f.write(file.file.read())
        except OSError as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploading file {}", file_path) from err
        scidra_file = await self.fs_file_to_file(file_path)
        if scidra_file is None:
            raise StorageError("A file could not be created from the filesystem")
        return scidra_file

    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        bucket_path = await self._get_bucket(bucket_name)
        fs_path = bucket_path / file_path
        return await self.fs_file_to_file(fs_path)

    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        bucket_path = await self._get_bucket(bucket_name)
        fs_path = bucket_path / file_path
        if not fs_path.exists():
            return None

        byte_stream = BytesIO()
        async with aiofiles.open(fs_path, mode="rb") as f:
            byte_stream = BytesIO(await f.read())
        byte_stream.seek(0)
        return byte_stream

    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        fs_path = self.root_path / bucket_name / file_path

        return fs_path.exists()

    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        fs_path = self.root_path / bucket_name / path

        exists = await aiofiles.os.path.exists(fs_path)
        is_dir = exists and await aiofiles.os.path.isdir(fs_path)
        file_list = []
        if exists and is_dir:
            file_list = await aiofiles.os.listdir(fs_path)

        return exists and is_dir and len(file_list) > 0

    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        try:
            if recursive:
                bucket_path = await self._get_bucket(bucket_name)
                fs_path = bucket_path / file_path
                is_dir = await aiofiles.os.path.isdir(fs_path)

                try:
                    if is_dir:
                        await rmtree(str(fs_path))
                    else:
                        await aiofiles.os.remove(fs_path)
                except OSError as err:
                    LOG.error(str(err))
                    raise StorageError(
                        "Something went wrong deleting file {}/{}",
                        bucket_name,
                        file_path,
                    ) from err
            else:
                bucket_path = await self._get_bucket(bucket_name)
                fs_path = bucket_path / file_path
                is_dir = await aiofiles.os.path.isdir(fs_path)
                try:
                    if not is_dir:
                        await aiofiles.os.remove(fs_path)
                    else:
                        raise StorageError(
                            "Trying to recursively delete a single file {}/{}",
                            bucket_name,
                            file_path,
                        )
                except OSError as err:
                    LOG.error(str(err))
                    raise StorageError(
                        "Something went wrong deleting file {}/{}",
                        bucket_name,
                        file_path,
                    ) from err
        except KeyError as err:
            raise StorageError(f"Trying to delete a file {bucket_name}/{file_path} that doesn't exist.") from err

    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        bucket_path = await self._get_bucket(bucket_name)
        fs_path = bucket_path / self.convert_path_in(file_path, bucket_name)
        new_fs_path = bucket_path / self.convert_path_in(new_file_path, bucket_name)

        if await aiofiles.os.path.exists(fs_path):
            try:
                await aiofiles.os.rename(fs_path, new_fs_path)
            except FileExistsError as err:
                raise StorageError(
                    f"Trying to rename a file {bucket_name}/{file_path} to "
                    + f"something that already exists ({bucket_name}/{new_file_path})."
                ) from err
        else:
            raise StorageError(f"Trying to rename a file {bucket_name}/{file_path} that doesn't exist.")

        LOG.debug(f"{file_path} renamed to {new_file_path}")
        file = await self.fs_file_to_file(new_fs_path)
        if file is None:
            raise StorageError("A file could not be created from the filesystem")
        return file

    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        old_bucket_path = await self._get_bucket(from_bucket)
        new_bucket_path = await self._get_bucket(to_bucket)
        old_fs_path = old_bucket_path / self.convert_path_in(from_path, from_bucket)
        new_fs_path = new_bucket_path / self.convert_path_in(to_path, to_bucket)
        if await aiofiles.os.path.exists(old_fs_path):
            await copy(old_fs_path, new_fs_path)
        else:
            raise StorageError(f"Trying to copy a file {from_bucket}/{from_path} that doesn't exist.")
        LOG.debug(f"{from_path} copied to {to_path}")

    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        # bucket_path = await self._get_bucket(bucket)
        # temp_path = bucket_path / path

        # Need to be able to create a temporary file -
        # async with aiofiles.tempfile.NamedTemporaryFile('wb+') as f:
        # but then automatically clean it up after some time.
        # FIXME make this work
        raise UnImplementedError("File system support for temp downloads currently not working.")

    async def list_immediate_folders(self, bucket_name: str, parent_path: str = "") -> List[str]:
        """
        List immediate folders within a specified bucket and parent path.

        Args:
            bucket_name (str): Name of the local bucket.
            parent_path (str): Parent directory path under which to list folders.

        Returns:
            List[str]: A list of folder names.
        """
        bucket_path = await self._get_bucket(bucket_name)
        parent_folder = bucket_path / parent_path

        folders = []
        # Iterate through entries in the parent folder
        for entry in parent_folder.iterdir():
            if entry.is_dir():
                # Extract the name of the folder and add it to the list
                folders.append(entry.name)

        return folders
