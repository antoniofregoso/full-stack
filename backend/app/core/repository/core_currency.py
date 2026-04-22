from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_currency import CoreCurrency


class CurrencyRepository:

    @staticmethod
    async def create(currency: CoreCurrency) -> CoreCurrency:
        async with db as session:
            session.add(currency)
            await session.commit()
            await session.refresh(currency)
            return currency

    @staticmethod
    async def get_all() -> list[CoreCurrency]:
        async with db as session:
            result = await session.execute(select(CoreCurrency).order_by(CoreCurrency.name))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(currency_id: int) -> Optional[CoreCurrency]:
        async with db as session:
            result = await session.execute(
                select(CoreCurrency).where(CoreCurrency.id == currency_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(code: str) -> Optional[CoreCurrency]:
        async with db as session:
            result = await session.execute(
                select(CoreCurrency).where(CoreCurrency.code == code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(currency_id: int, payload: dict) -> Optional[CoreCurrency]:
        async with db as session:
            result = await session.execute(
                select(CoreCurrency).where(CoreCurrency.id == currency_id)
            )
            currency = result.scalars().first()
            if currency is None:
                return None

            for field, value in payload.items():
                setattr(currency, field, value)

            session.add(currency)
            await session.commit()
            await session.refresh(currency)
            return currency

    @staticmethod
    async def delete(currency_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreCurrency).where(CoreCurrency.id == currency_id)
            )
            currency = result.scalars().first()
            if currency is None:
                return False

            await session.delete(currency)
            await session.commit()
            return True
