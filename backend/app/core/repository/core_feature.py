from typing import Optional

from sqlalchemy import func
from sqlmodel import select

from config import db
from app.core.models.core_feature import CoreFeature


class FeatureRepository:
    @staticmethod
    async def create(feature: CoreFeature) -> CoreFeature:
        async with db as session:
            session.add(feature)
            await session.commit()
            await session.refresh(feature)
            return feature

    @staticmethod
    async def get_all() -> list[CoreFeature]:
        async with db as session:
            result = await session.execute(
                select(CoreFeature).order_by(
                    CoreFeature.sequence,
                    func.coalesce(
                        CoreFeature.name["es_MX"].astext,
                        CoreFeature.name["en_US"].astext,
                        CoreFeature.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(feature_id: int) -> Optional[CoreFeature]:
        async with db as session:
            result = await session.execute(
                select(CoreFeature).where(CoreFeature.id == feature_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(entity_id: int, code: str) -> Optional[CoreFeature]:
        async with db as session:
            result = await session.execute(
                select(CoreFeature).where(
                    CoreFeature.entity_id == entity_id,
                    CoreFeature.code == code,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(feature_id: int, payload: dict) -> Optional[CoreFeature]:
        async with db as session:
            result = await session.execute(
                select(CoreFeature).where(CoreFeature.id == feature_id)
            )
            feature = result.scalars().first()
            if feature is None:
                return None

            for field, value in payload.items():
                setattr(feature, field, value)

            session.add(feature)
            await session.commit()
            await session.refresh(feature)
            return feature

    @staticmethod
    async def delete(feature_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreFeature).where(CoreFeature.id == feature_id)
            )
            feature = result.scalars().first()
            if feature is None:
                return False

            await session.delete(feature)
            await session.commit()
            return True
