from typing import Optional

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.models.core_audit import CoreAudit


class CoreUserAssignment(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_user_assignments"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "system_id",
            "team_id",
            "module_id",
            "entity_id",
            name="uq_core_user_assignments_scope",
        ),
        CheckConstraint(
            """
            ((CASE WHEN system_id IS NOT NULL THEN 1 ELSE 0 END) +
             (CASE WHEN team_id IS NOT NULL THEN 1 ELSE 0 END) +
             (CASE WHEN module_id IS NOT NULL THEN 1 ELSE 0 END) +
             (CASE WHEN entity_id IS NOT NULL THEN 1 ELSE 0 END)) = 1
            """,
            name="ck_core_user_assignments_exactly_one_scope",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="auth_users.id")
    system_id: Optional[int] = Field(default=None, foreign_key="core_systems.id")
    team_id: Optional[int] = Field(default=None, foreign_key="core_teams.id")
    module_id: Optional[int] = Field(default=None, foreign_key="core_modules.id")
    entity_id: Optional[int] = Field(default=None, foreign_key="core_entities.id")
    assignment_role: Optional[str] = None
    is_manager: bool = Field(default=False)
    active: bool = Field(default=True) 
