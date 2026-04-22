from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_page import CorePage


class PageRepository:

    @staticmethod
    async def create(page: CorePage) -> CorePage:
        async with db as session:
            session.add(page)
            await session.commit()
            await session.refresh(page)
            return page

    @staticmethod
    async def get_all() -> list[CorePage]:
        async with db as session:
            result = await session.execute(select(CorePage).order_by(CorePage.name))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(page_id: int) -> Optional[CorePage]:
        async with db as session:
            result = await session.execute(select(CorePage).where(CorePage.id == page_id))
            return result.scalars().first()

    @staticmethod
    async def get_by_name(name: dict) -> Optional[CorePage]:
        async with db as session:
            result = await session.execute(
                select(CorePage).where(CorePage.name == name)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_keys(keys: dict) -> list[CorePage]:
        async with db as session:
            result = await session.execute(
                select(CorePage)
                .where(CorePage.keys.contains(keys))
                .order_by(CorePage.name)
            )
            return result.scalars().all()

    @staticmethod
    async def update(page_id: int, payload: dict) -> Optional[CorePage]:
        async with db as session:
            result = await session.execute(select(CorePage).where(CorePage.id == page_id))
            page = result.scalars().first()
            if page is None:
                return None

            for field, value in payload.items():
                setattr(page, field, value)

            session.add(page)
            await session.commit()
            await session.refresh(page)
            return page

    @staticmethod
    async def delete(page_id: int) -> bool:
        async with db as session:
            result = await session.execute(select(CorePage).where(CorePage.id == page_id))
            page = result.scalars().first()
            if page is None:
                return False

            await session.delete(page)
            await session.commit()
            return True
