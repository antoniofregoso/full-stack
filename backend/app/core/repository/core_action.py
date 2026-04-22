from typing import Optional

from sqlalchemy import func
from sqlmodel import select

from config import db
from app.core.models.core_action import CoreAction


class ActionRepository:
    @staticmethod
    async def create(action: CoreAction) -> CoreAction:
        async with db as session:
            session.add(action)
            await session.commit()
            await session.refresh(action)
            return action

    @staticmethod
    async def get_all() -> list[CoreAction]:
        async with db as session:
            result = await session.execute(
                select(CoreAction).order_by(
                    CoreAction.sequence,
                    func.coalesce(
                        CoreAction.name["es_MX"].astext,
                        CoreAction.name["en_US"].astext,
                        CoreAction.code,
                    ),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(action_id: int) -> Optional[CoreAction]:
        async with db as session:
            result = await session.execute(
                select(CoreAction).where(CoreAction.id == action_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(entity_id: int, code: str) -> Optional[CoreAction]:
        async with db as session:
            result = await session.execute(
                select(CoreAction).where(
                    CoreAction.entity_id == entity_id,
                    CoreAction.code == code,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(action_id: int, payload: dict) -> Optional[CoreAction]:
        async with db as session:
            result = await session.execute(
                select(CoreAction).where(CoreAction.id == action_id)
            )
            action = result.scalars().first()
            if action is None:
                return None

            for field, value in payload.items():
                setattr(action, field, value)

            session.add(action)
            await session.commit()
            await session.refresh(action)
            return action

    @staticmethod
    async def delete(action_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreAction).where(CoreAction.id == action_id)
            )
            action = result.scalars().first()
            if action is None:
                return False

            await session.delete(action)
            await session.commit()
            return True
