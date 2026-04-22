from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_lang import CoreLang


class LangRepository:

    @staticmethod
    async def create(lang: CoreLang) -> CoreLang:
        async with db as session:
            session.add(lang)
            await session.commit()
            await session.refresh(lang)
            return lang

    @staticmethod
    async def get_all() -> list[CoreLang]:
        async with db as session:
            result = await session.execute(select(CoreLang).order_by(CoreLang.name))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(lang_id: int) -> Optional[CoreLang]:
        async with db as session:
            result = await session.execute(select(CoreLang).where(CoreLang.id == lang_id))
            return result.scalars().first()

    @staticmethod
    async def get_by_code(code: str) -> Optional[CoreLang]:
        async with db as session:
            result = await session.execute(select(CoreLang).where(CoreLang.code == code))
            return result.scalars().first()

    @staticmethod
    async def get_by_iso_code(iso_code: str) -> Optional[CoreLang]:
        async with db as session:
            result = await session.execute(
                select(CoreLang).where(CoreLang.iso_code == iso_code)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_url_code(url_code: str) -> Optional[CoreLang]:
        async with db as session:
            result = await session.execute(
                select(CoreLang).where(CoreLang.url_code == url_code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(lang_id: int, payload: dict) -> Optional[CoreLang]:
        async with db as session:
            result = await session.execute(select(CoreLang).where(CoreLang.id == lang_id))
            lang = result.scalars().first()
            if lang is None:
                return None

            for field, value in payload.items():
                setattr(lang, field, value)

            session.add(lang)
            await session.commit()
            await session.refresh(lang)
            return lang

    @staticmethod
    async def delete(lang_id: int) -> bool:
        async with db as session:
            result = await session.execute(select(CoreLang).where(CoreLang.id == lang_id))
            lang = result.scalars().first()
            if lang is None:
                return False

            await session.delete(lang)
            await session.commit()
            return True
