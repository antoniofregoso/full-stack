from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_app import CoreApp


class AppRepository:
    @staticmethod
    async def create(app: CoreApp) -> CoreApp:
        async with db as session:
            session.add(app)
            await session.commit()
            await session.refresh(app)
            return app

    @staticmethod
    async def get_all() -> list[CoreApp]:
        async with db as session:
            result = await session.execute(select(CoreApp).order_by(CoreApp.name))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(app_id: int) -> Optional[CoreApp]:
        async with db as session:
            result = await session.execute(select(CoreApp).where(CoreApp.id == app_id))
            return result.scalars().first()

    @staticmethod
    async def get_by_keys(keys: dict) -> list[CoreApp]:
        async with db as session:
            result = await session.execute(
                select(CoreApp)
                .where(CoreApp.keys.contains(keys))
                .order_by(CoreApp.name)
            )
            return result.scalars().all()

    @staticmethod
    async def update(app_id: int, payload: dict) -> Optional[CoreApp]:
        async with db as session:
            result = await session.execute(select(CoreApp).where(CoreApp.id == app_id))
            app = result.scalars().first()
            if app is None:
                return None

            for field, value in payload.items():
                setattr(app, field, value)

            session.add(app)
            await session.commit()
            await session.refresh(app)
            return app

    @staticmethod
    async def delete(app_id: int) -> bool:
        async with db as session:
            result = await session.execute(select(CoreApp).where(CoreApp.id == app_id))
            app = result.scalars().first()
            if app is None:
                return False

            await session.delete(app)
            await session.commit()
            return True
