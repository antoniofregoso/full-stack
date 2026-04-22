from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import AppSettingsInput, AppSettingsType
from app.core.models.core_app_settings import CoreAppSettings
from app.core.repository.core_app import AppRepository
from app.core.repository.core_app_settings import AppSettingsRepository


class AppSettingsService:
    @staticmethod
    def _to_type(setting: CoreAppSettings) -> AppSettingsType:
        return AppSettingsType(
            id=setting.id,
            app_id=setting.app_id,
            key=setting.key,
            value=setting.value,
            created_at=setting.created_at,
            create_by=setting.create_by,
            updated_at=setting.updated_at,
            updated_by=setting.updated_by,
        )

    @staticmethod
    def _normalize(payload: AppSettingsInput) -> dict:
        data = asdict(payload)
        data["key"] = data["key"].strip()
        if not data["key"]:
            raise HTTPException(status_code=400, detail="key is required")
        return data

    @staticmethod
    async def _ensure_app_exists(app_id: int) -> None:
        app = await AppRepository.get_by_id(app_id)
        if app is None:
            raise HTTPException(status_code=400, detail="app does not exist")

    @staticmethod
    async def create(payload: AppSettingsInput) -> AppSettingsType:
        data = AppSettingsService._normalize(payload)
        await AppSettingsService._ensure_app_exists(data["app_id"])
        existing = await AppSettingsRepository.get_by_app_and_key(data["app_id"], data["key"])
        if existing:
            raise HTTPException(status_code=400, detail="app setting key already exists")

        created = await AppSettingsRepository.create(CoreAppSettings(**data))
        return AppSettingsService._to_type(created)

    @staticmethod
    async def get_all() -> list[AppSettingsType]:
        settings = await AppSettingsRepository.get_all()
        return [AppSettingsService._to_type(setting) for setting in settings]

    @staticmethod
    async def get_by_id(setting_id: int) -> AppSettingsType | None:
        setting = await AppSettingsRepository.get_by_id(setting_id)
        return AppSettingsService._to_type(setting) if setting else None

    @staticmethod
    async def get_by_app(app_id: int) -> list[AppSettingsType]:
        settings = await AppSettingsRepository.get_by_app(app_id)
        return [AppSettingsService._to_type(setting) for setting in settings]

    @staticmethod
    async def get_by_app_and_key(app_id: int, key: str) -> AppSettingsType | None:
        normalized_key = key.strip()
        if not normalized_key:
            raise HTTPException(status_code=400, detail="key is required")

        setting = await AppSettingsRepository.get_by_app_and_key(app_id, normalized_key)
        return AppSettingsService._to_type(setting) if setting else None

    @staticmethod
    async def update(setting_id: int, payload: AppSettingsInput) -> AppSettingsType:
        data = AppSettingsService._normalize(payload)
        await AppSettingsService._ensure_app_exists(data["app_id"])

        existing = await AppSettingsRepository.get_by_app_and_key(data["app_id"], data["key"])
        if existing and existing.id != setting_id:
            raise HTTPException(status_code=400, detail="app setting key already exists")

        updated = await AppSettingsRepository.update(setting_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="app setting not found")

        return AppSettingsService._to_type(updated)

    @staticmethod
    async def delete(setting_id: int) -> bool:
        deleted = await AppSettingsRepository.delete(setting_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="app setting not found")
        return True
