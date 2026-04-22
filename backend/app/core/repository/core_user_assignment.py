from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_user_assignment import CoreUserAssignment


class UserAssignmentRepository:
    @staticmethod
    async def create(assignment: CoreUserAssignment) -> CoreUserAssignment:
        async with db as session:
            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)
            return assignment

    @staticmethod
    async def get_by_id(assignment_id: int) -> Optional[CoreUserAssignment]:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment).where(CoreUserAssignment.id == assignment_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreUserAssignment]:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment).order_by(CoreUserAssignment.user_id, CoreUserAssignment.id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_user(user_id: int) -> list[CoreUserAssignment]:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment)
                .where(CoreUserAssignment.user_id == user_id)
                .order_by(CoreUserAssignment.id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_scope(
        *,
        system_id: int | None = None,
        team_id: int | None = None,
        module_id: int | None = None,
        entity_id: int | None = None,
    ) -> list[CoreUserAssignment]:
        async with db as session:
            query = select(CoreUserAssignment)
            if system_id is not None:
                query = query.where(CoreUserAssignment.system_id == system_id)
            if team_id is not None:
                query = query.where(CoreUserAssignment.team_id == team_id)
            if module_id is not None:
                query = query.where(CoreUserAssignment.module_id == module_id)
            if entity_id is not None:
                query = query.where(CoreUserAssignment.entity_id == entity_id)
            result = await session.execute(query.order_by(CoreUserAssignment.id))
            return result.scalars().all()

    @staticmethod
    async def find_existing(payload: dict) -> Optional[CoreUserAssignment]:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment).where(
                    CoreUserAssignment.user_id == payload["user_id"],
                    CoreUserAssignment.system_id == payload.get("system_id"),
                    CoreUserAssignment.team_id == payload.get("team_id"),
                    CoreUserAssignment.module_id == payload.get("module_id"),
                    CoreUserAssignment.entity_id == payload.get("entity_id"),
                )
            )
            return result.scalars().first()

    @staticmethod
    async def update(assignment_id: int, payload: dict) -> Optional[CoreUserAssignment]:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment).where(CoreUserAssignment.id == assignment_id)
            )
            assignment = result.scalars().first()
            if assignment is None:
                return None

            for field, value in payload.items():
                setattr(assignment, field, value)

            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)
            return assignment

    @staticmethod
    async def delete(assignment_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreUserAssignment).where(CoreUserAssignment.id == assignment_id)
            )
            assignment = result.scalars().first()
            if assignment is None:
                return False

            await session.delete(assignment)
            await session.commit()
            return True
