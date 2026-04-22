from sqlmodel import select

from config import db
from app.talent.models.talent_node_assignment import TalentNodeAssignment, TalentNodeType


class TalentNodeAssignmentRepository:
    @staticmethod
    async def create(assignment: TalentNodeAssignment) -> TalentNodeAssignment:
        async with db as session:
            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)
            return assignment

    @staticmethod
    async def get_all() -> list[TalentNodeAssignment]:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment).order_by(
                    TalentNodeAssignment.node_type,
                    TalentNodeAssignment.node_id,
                    TalentNodeAssignment.user_id,
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(assignment_id: int) -> TalentNodeAssignment | None:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment).where(TalentNodeAssignment.id == assignment_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_user(user_id: int) -> list[TalentNodeAssignment]:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment)
                .where(TalentNodeAssignment.user_id == user_id)
                .order_by(
                    TalentNodeAssignment.node_type,
                    TalentNodeAssignment.node_id,
                    TalentNodeAssignment.id,
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_node(node_type: TalentNodeType, node_id: int) -> list[TalentNodeAssignment]:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment)
                .where(
                    TalentNodeAssignment.node_type == node_type,
                    TalentNodeAssignment.node_id == node_id,
                )
                .order_by(
                    TalentNodeAssignment.is_primary.desc(),
                    TalentNodeAssignment.user_id,
                    TalentNodeAssignment.id,
                )
            )
            return result.scalars().all()

    @staticmethod
    async def find_existing(
        *, user_id: int, node_type: TalentNodeType, node_id: int
    ) -> TalentNodeAssignment | None:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment).where(
                    TalentNodeAssignment.user_id == user_id,
                    TalentNodeAssignment.node_type == node_type,
                    TalentNodeAssignment.node_id == node_id,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def clear_primary_for_node(
        *, node_type: TalentNodeType, node_id: int, exclude_id: int | None = None
    ) -> None:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment).where(
                    TalentNodeAssignment.node_type == node_type,
                    TalentNodeAssignment.node_id == node_id,
                    TalentNodeAssignment.is_primary == True,
                )
            )
            assignments = result.scalars().all()
            changed = False
            for assignment in assignments:
                if exclude_id is not None and assignment.id == exclude_id:
                    continue
                assignment.is_primary = False
                session.add(assignment)
                changed = True
            if changed:
                await session.commit()

    @staticmethod
    async def update(assignment_id: int, payload: dict) -> TalentNodeAssignment | None:
        async with db as session:
            result = await session.execute(
                select(TalentNodeAssignment).where(TalentNodeAssignment.id == assignment_id)
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
                select(TalentNodeAssignment).where(TalentNodeAssignment.id == assignment_id)
            )
            assignment = result.scalars().first()
            if assignment is None:
                return False
            await session.delete(assignment)
            await session.commit()
            return True
