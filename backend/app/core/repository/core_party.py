from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_party import CoreParty


class PartyRepository:

    @staticmethod
    async def create(party: CoreParty) -> CoreParty:
        async with db as session:
            session.add(party)
            await session.commit()
            await session.refresh(party)
            return party

    @staticmethod
    async def get_all() -> list[CoreParty]:
        async with db as session:
            result = await session.execute(select(CoreParty).order_by(CoreParty.name))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(party_id: int) -> Optional[CoreParty]:
        async with db as session:
            result = await session.execute(select(CoreParty).where(CoreParty.id == party_id))
            return result.scalars().first()

    @staticmethod
    async def update(party_id: int, payload: dict) -> Optional[CoreParty]:
        async with db as session:
            result = await session.execute(select(CoreParty).where(CoreParty.id == party_id))
            party = result.scalars().first()
            if party is None:
                return None

            for field, value in payload.items():
                setattr(party, field, value)

            session.add(party)
            await session.commit()
            await session.refresh(party)
            return party

    @staticmethod
    async def delete(party_id: int) -> bool:
        async with db as session:
            result = await session.execute(select(CoreParty).where(CoreParty.id == party_id))
            party = result.scalars().first()
            if party is None:
                return False

            await session.delete(party)
            await session.commit()
            return True
