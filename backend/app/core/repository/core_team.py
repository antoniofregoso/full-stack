from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_module import CoreModule
from app.core.models.core_team import CoreTeam


class TeamRepository:
    @staticmethod
    def _query():
        return select(CoreTeam).options(selectinload(CoreTeam.modules))

    @staticmethod
    async def create(team: CoreTeam) -> CoreTeam:
        async with db as session:
            session.add(team)
            await session.commit()
            result = await session.execute(
                TeamRepository._query().where(CoreTeam.id == team.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreTeam]:
        async with db as session:
            result = await session.execute(
                TeamRepository._query().order_by(
                    CoreTeam.sequence,
                    func.coalesce(
                        CoreTeam.name["es_MX"].astext,
                        CoreTeam.name["en_US"].astext,
                        CoreTeam.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(team_id: int) -> Optional[CoreTeam]:
        async with db as session:
            result = await session.execute(
                TeamRepository._query().where(CoreTeam.id == team_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(system_id: int, code: str) -> Optional[CoreTeam]:
        async with db as session:
            result = await session.execute(
                TeamRepository._query().where(
                    CoreTeam.system_id == system_id,
                    CoreTeam.code == code,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(team_id: int, payload: dict) -> Optional[CoreTeam]:
        async with db as session:
            result = await session.execute(select(CoreTeam).where(CoreTeam.id == team_id))
            team = result.scalars().first()
            if team is None:
                return None

            for field, value in payload.items():
                setattr(team, field, value)

            session.add(team)
            await session.commit()
            result = await session.execute(
                TeamRepository._query().where(CoreTeam.id == team.id)
            )
            return result.scalars().first()

    @staticmethod
    async def delete(team_id: int) -> bool:
        async with db as session:
            result = await session.execute(select(CoreTeam).where(CoreTeam.id == team_id))
            team = result.scalars().first()
            if team is None:
                return False

            await session.delete(team)
            await session.commit()
            return True

    @staticmethod
    async def get_modules(team_id: int) -> list[CoreModule]:
        async with db as session:
            result = await session.execute(
                select(CoreModule)
                .where(CoreModule.team_id == team_id)
                .order_by(CoreModule.sequence, CoreModule.code)
            )
            return result.scalars().all()

