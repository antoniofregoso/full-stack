from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_module import CoreModule


class ModuleRepository:
    @staticmethod
    def _query():
        return select(CoreModule).options(selectinload(CoreModule.entities))

    @staticmethod
    async def create(module: CoreModule) -> CoreModule:
        async with db as session:
            session.add(module)
            await session.commit()
            result = await session.execute(
                ModuleRepository._query().where(CoreModule.id == module.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreModule]:
        async with db as session:
            result = await session.execute(
                ModuleRepository._query().order_by(
                    CoreModule.sequence,
                    func.coalesce(
                        CoreModule.name["es_MX"].astext,
                        CoreModule.name["en_US"].astext,
                        CoreModule.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(module_id: int) -> Optional[CoreModule]:
        async with db as session:
            result = await session.execute(
                ModuleRepository._query().where(CoreModule.id == module_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(team_id: int, code: str) -> Optional[CoreModule]:
        async with db as session:
            result = await session.execute(
                ModuleRepository._query().where(
                    CoreModule.team_id == team_id,
                    CoreModule.code == code,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(module_id: int, payload: dict) -> Optional[CoreModule]:
        async with db as session:
            result = await session.execute(
                select(CoreModule).where(CoreModule.id == module_id)
            )
            module = result.scalars().first()
            if module is None:
                return None

            for field, value in payload.items():
                setattr(module, field, value)

            session.add(module)
            await session.commit()
            result = await session.execute(
                ModuleRepository._query().where(CoreModule.id == module.id)
            )
            return result.scalars().first()

    @staticmethod
    async def delete(module_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreModule).where(CoreModule.id == module_id)
            )
            module = result.scalars().first()
            if module is None:
                return False

            await session.delete(module)
            await session.commit()
            return True
