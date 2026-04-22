from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_system import CoreSystem
from app.core.models.core_team import CoreTeam


class SystemRepository:
    @staticmethod
    def _query():
        return select(CoreSystem).options(selectinload(CoreSystem.teams))

    @staticmethod
    async def create(system: CoreSystem) -> CoreSystem:
        async with db as session:
            session.add(system)
            await session.commit()
            result = await session.execute(
                SystemRepository._query().where(CoreSystem.id == system.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreSystem]:
        async with db as session:
            result = await session.execute(
                SystemRepository._query().order_by(
                    CoreSystem.sequence,
                    func.coalesce(
                        CoreSystem.name["es_MX"].astext,
                        CoreSystem.name["en_US"].astext,
                        CoreSystem.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(system_id: int) -> Optional[CoreSystem]:
        async with db as session:
            result = await session.execute(
                SystemRepository._query().where(CoreSystem.id == system_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_ids(system_ids: list[int]) -> list[CoreSystem]:
        if not system_ids:
            return []

        async with db as session:
            result = await session.execute(
                SystemRepository._query().where(CoreSystem.id.in_(system_ids))
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_code(code: str) -> Optional[CoreSystem]:
        async with db as session:
            result = await session.execute(
                SystemRepository._query().where(CoreSystem.code == code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(system_id: int, payload: dict) -> Optional[CoreSystem]:
        async with db as session:
            result = await session.execute(
                select(CoreSystem).where(CoreSystem.id == system_id)
            )
            system = result.scalars().first()
            if system is None:
                return None

            for field, value in payload.items():
                setattr(system, field, value)

            session.add(system)
            await session.commit()
            result = await session.execute(
                SystemRepository._query().where(CoreSystem.id == system.id)
            )
            return result.scalars().first()

    @staticmethod
    async def delete(system_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreSystem).where(CoreSystem.id == system_id)
            )
            system = result.scalars().first()
            if system is None:
                return False

            await session.delete(system)
            await session.commit()
            return True

    @staticmethod
    async def get_teams(system_id: int) -> list[CoreTeam]:
        async with db as session:
            result = await session.execute(
                select(CoreTeam)
                .where(CoreTeam.system_id == system_id)
                .order_by(CoreTeam.sequence, CoreTeam.code)
            )
            return result.scalars().all()
