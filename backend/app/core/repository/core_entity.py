from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_action import CoreAction
from app.core.models.core_entity import CoreEntity
from app.core.models.core_feature import CoreFeature


class EntityRepository:
    @staticmethod
    def _query():
        return select(CoreEntity).options(
            selectinload(CoreEntity.features),
            selectinload(CoreEntity.actions),
        )

    @staticmethod
    async def create(entity: CoreEntity) -> CoreEntity:
        async with db as session:
            session.add(entity)
            await session.commit()
            result = await session.execute(
                EntityRepository._query().where(CoreEntity.id == entity.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreEntity]:
        async with db as session:
            result = await session.execute(
                EntityRepository._query().order_by(
                    CoreEntity.sequence,
                    func.coalesce(
                        CoreEntity.name["es_MX"].astext,
                        CoreEntity.name["en_US"].astext,
                        CoreEntity.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(entity_id: int) -> Optional[CoreEntity]:
        async with db as session:
            result = await session.execute(
                EntityRepository._query().where(CoreEntity.id == entity_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(module_id: int, code: str) -> Optional[CoreEntity]:
        async with db as session:
            result = await session.execute(
                EntityRepository._query().where(
                    CoreEntity.module_id == module_id,
                    CoreEntity.code == code,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_module(module_id: int) -> list[CoreEntity]:
        async with db as session:
            result = await session.execute(
                EntityRepository._query()
                .where(CoreEntity.module_id == module_id)
                .order_by(CoreEntity.sequence, CoreEntity.code)
            )
            return result.scalars().all()

    @staticmethod
    async def get_first_by_module(module_id: int) -> Optional[CoreEntity]:
        async with db as session:
            result = await session.execute(
                EntityRepository._query()
                .where(CoreEntity.module_id == module_id, CoreEntity.active == True)
                .order_by(CoreEntity.sequence, CoreEntity.code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(entity_id: int, payload: dict) -> Optional[CoreEntity]:
        async with db as session:
            result = await session.execute(
                select(CoreEntity).where(CoreEntity.id == entity_id)
            )
            entity = result.scalars().first()
            if entity is None:
                return None

            for field, value in payload.items():
                setattr(entity, field, value)

            session.add(entity)
            await session.commit()
            result = await session.execute(
                EntityRepository._query().where(CoreEntity.id == entity.id)
            )
            return result.scalars().first()

    @staticmethod
    async def delete(entity_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreEntity).where(CoreEntity.id == entity_id)
            )
            entity = result.scalars().first()
            if entity is None:
                return False

            await session.delete(entity)
            await session.commit()
            return True

    @staticmethod
    async def get_features(entity_id: int) -> list[CoreFeature]:
        async with db as session:
            result = await session.execute(
                select(CoreFeature)
                .where(CoreFeature.entity_id == entity_id)
                .order_by(CoreFeature.sequence, CoreFeature.code)
            )
            return result.scalars().all()

    @staticmethod
    async def get_actions(entity_id: int) -> list[CoreAction]:
        async with db as session:
            result = await session.execute(
                select(CoreAction)
                .where(CoreAction.entity_id == entity_id)
                .order_by(CoreAction.sequence, CoreAction.code)
            )
            return result.scalars().all()
