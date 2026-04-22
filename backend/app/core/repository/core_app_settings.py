from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_app_settings import CoreAppSettings


class AppSettingsRepository:
    @staticmethod
    async def create(setting: CoreAppSettings) -> CoreAppSettings:
        async with db as session:
            session.add(setting)
            await session.commit()
            await session.refresh(setting)
            return setting

    @staticmethod
    async def get_all() -> list[CoreAppSettings]:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings).order_by(CoreAppSettings.app_id, CoreAppSettings.key)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(setting_id: int) -> Optional[CoreAppSettings]:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings).where(CoreAppSettings.id == setting_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_app(app_id: int) -> list[CoreAppSettings]:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings)
                .where(CoreAppSettings.app_id == app_id)
                .order_by(CoreAppSettings.key)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_app_and_key(app_id: int, key: str) -> Optional[CoreAppSettings]:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings).where(
                    CoreAppSettings.app_id == app_id,
                    CoreAppSettings.key == key,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(setting_id: int, payload: dict) -> Optional[CoreAppSettings]:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings).where(CoreAppSettings.id == setting_id)
            )
            setting = result.scalars().first()
            if setting is None:
                return None

            for field, value in payload.items():
                setattr(setting, field, value)

            session.add(setting)
            await session.commit()
            await session.refresh(setting)
            return setting

    @staticmethod
    async def delete(setting_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreAppSettings).where(CoreAppSettings.id == setting_id)
            )
            setting = result.scalars().first()
            if setting is None:
                return False

            await session.delete(setting)
            await session.commit()
            return True
