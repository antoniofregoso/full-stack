from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import AppInput, AppType
from app.core.models.core_app import CoreApp
from app.core.repository.core_app import AppRepository
from app.core.service.core_system import SystemService


class AppService:
    @staticmethod
    def _to_type(app: CoreApp) -> AppType:
        return AppType(
            id=app.id,
            name=app.name,
            description=app.description,
            keys=app.keys,
            active=app.active,
            public=app.public,
            schema_org=app.schema_org,
            created_at=app.created_at,
            create_by=app.create_by,
            updated_at=app.updated_at,
            updated_by=app.updated_by,
        )

    @staticmethod
    def _normalize(payload: AppInput) -> dict:
        data = asdict(payload)
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if data.get("keys") is not None:
            data["keys"] = SystemService._normalize_json_object(data.get("keys"), "keys")
        if data.get("schema_org") is not None:
            data["schema_org"] = SystemService._normalize_json_object(
                data.get("schema_org"), "schema_org"
            )
        return data

    @staticmethod
    async def create(payload: AppInput) -> AppType:
        data = AppService._normalize(payload)
        created = await AppRepository.create(CoreApp(**data))
        return AppService._to_type(created)

    @staticmethod
    async def get_all() -> list[AppType]:
        apps = await AppRepository.get_all()
        return [AppService._to_type(app) for app in apps]

    @staticmethod
    async def get_by_id(app_id: int) -> AppType | None:
        app = await AppRepository.get_by_id(app_id)
        return AppService._to_type(app) if app else None

    @staticmethod
    async def get_by_keys(keys: dict) -> list[AppType]:
        if not isinstance(keys, dict) or not keys:
            raise HTTPException(status_code=400, detail="keys must be a non-empty JSON object")

        apps = await AppRepository.get_by_keys(keys)
        return [AppService._to_type(app) for app in apps]

    @staticmethod
    async def update(app_id: int, payload: AppInput) -> AppType:
        data = AppService._normalize(payload)
        updated = await AppRepository.update(app_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="app not found")

        return AppService._to_type(updated)

    @staticmethod
    async def delete(app_id: int) -> bool:
        deleted = await AppRepository.delete(app_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="app not found")
        return True
