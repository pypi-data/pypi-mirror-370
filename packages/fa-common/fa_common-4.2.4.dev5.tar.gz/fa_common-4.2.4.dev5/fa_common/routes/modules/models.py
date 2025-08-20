from typing import List, Optional

from beanie import Document
from pymongo import DESCENDING, IndexModel

from fa_common import get_settings
from fa_common.exceptions import BadRequestError, NotFoundError
from fa_common.models import Message, TimeStampedModel
from fa_common.routes.modules.types import Module, ModuleListResponse, ModuleResponse, ModuleVersion


class ModuleDocument(Module, Document, TimeStampedModel):
    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}modules"
        indexes = [
            IndexModel([("name", DESCENDING)], name="module_name", unique=True),
        ]

    @classmethod
    async def get(cls, name: str) -> Module:
        return await cls.find_one(ModuleDocument.name == name)

    @classmethod
    async def get_all(cls) -> List[str]:
        lst_modules = await cls.find_all().to_list()
        return [
            ModuleListResponse(
                name=module.name,
                description=module.description,
                created=str(module.created),
                tags=module.tags,
                versions=[ver.name for ver in module.versions],
                has_base_version=module.base_version is not None,
            )
            for module in lst_modules
        ]

    @classmethod
    async def get_version(cls, name: str, version: str, fuse: bool = True) -> ModuleResponse:
        module = await cls.find_one(ModuleDocument.name == name)
        if module:
            if fuse:
                ver = module.get_fused_version_meta(version)
            else:
                if not module.versions or len(module.versions) == 0:
                    raise NotFoundError("There are no versions for this module!")
                ver = next((v for v in module.versions if v.name == version), None)
            if ver:
                return ModuleResponse(name=module.name, version=ver)
            raise NotFoundError(f"Version {version} not found for Module {name}!")
        raise NotFoundError(f"Module {name} not found!")

    @classmethod
    async def get_versions(cls, name: str) -> List[str]:
        module = await cls.find_one(ModuleDocument.name == name)
        return [ver.name for ver in module.versions]

    @classmethod
    async def insert_new(cls, new_module: Module):
        module_doc = ModuleDocument(**new_module.model_dump())
        await module_doc.insert()
        return module_doc

    @classmethod
    async def delete_module(cls, name: str) -> Message:
        module = await cls.find_one(ModuleDocument.name == name)
        if module:
            await module.delete()
            verify = await cls.find_one(cls.name == name)

            if verify:
                return Message(message="Unsuccessful!", warnings=["Something went wronge with deletion of {name}. The module yet exists."])
            return Message(message=f"Successfully deleted module {name}.")
        else:
            return Message(message="Unsuccessful!", warnings=[f"Module {name} does not exist!"])
        # await cls.find_one(ModuleDocument.name == name).delete()

    @classmethod
    async def overwrite(cls, curr_name: str, module: Module):
        """A complete overwrite of module."""
        module_db = await cls.find_one(ModuleDocument.name == curr_name)
        updated_module = module_db.model_copy(update=module.model_dump())
        res = await updated_module.save()
        return res

    @classmethod
    async def update_meta(cls, curr_name: str, new_name: Optional[str] = None, description: Optional[str] = None):
        """Update name and description."""
        if new_name is None and description is None:
            raise BadRequestError("Either new name or description should be provided!")

        module_db = await cls.find_one(ModuleDocument.name == curr_name)
        if new_name:
            module_db.name = new_name
        if description:
            module_db.description = description

        res = await module_db.save()
        return res

    @classmethod
    async def update_version(cls, name: str, version_name: str, version: ModuleVersion):
        """Update a specific version of a module."""
        module_db = await cls.find_one(ModuleDocument.name == name)
        for i, ver in enumerate(module_db.versions):
            if ver.name == version_name:
                module_db.versions[i] = version

        res = await module_db.save()
        return res

    @classmethod
    async def update_base_version(cls, name: str, version: ModuleVersion):
        """Remove an existing version."""
        module_db = await cls.find_one(ModuleDocument.name == name)
        module_db.base_version = version
        res = await module_db.save()
        return res

    @classmethod
    async def add_new_version(cls, name: str, version: ModuleVersion):
        """Update a specific version of a module."""
        module_db = await cls.find_one(ModuleDocument.name == name)
        module_db.versions.append(version)
        res = await module_db.save()
        return res

    @classmethod
    async def delete_version(cls, name: str, version_name: str):
        """Remove an existing version."""
        module_db = await cls.find_one(ModuleDocument.name == name)
        flt_vers = [v for v in module_db.versions if v.name != version_name]
        module_db.versions = flt_vers
        res = await module_db.save()
        return res
