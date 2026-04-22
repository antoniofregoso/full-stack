from enum import Enum
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.core.models.core_audit import CoreAudit


class TalentNodeType(str, Enum):
    SYSTEM = "SYSTEM"
    TEAM = "TEAM"
    MODULE = "MODULE"
    ENTITY = "ENTITY"
    FEATURE = "FEATURE"
    ACTION = "ACTION"


class TalentNodeAssignment(CoreAudit, SQLModel, table=True):
    __tablename__ = "talent_node_assignments"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "node_type",
            "node_id",
            name="uq_talent_node_assignments_user_node",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="auth_users.id")
    node_type: TalentNodeType
    node_id: int = Field(index=True)
    job_title: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    description: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    is_ai_agent: bool = Field(default=False)
    is_primary: bool = Field(default=False)
    active: bool = Field(default=True)
