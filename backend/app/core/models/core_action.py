from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.core.models.core_audit import CoreAudit
from app.infrastructure.model_defaults import default_icon

if TYPE_CHECKING:
    from app.core.models.core_entity import CoreEntity


class CoreAction(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_actions"
    __table_args__ = (
        UniqueConstraint("entity_id", "code", name="uq_core_actions_entity_code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    entity_id: int = Field(foreign_key="core_entities.id")
    code: str = Field(index=True)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    icon: dict[str, str] = Field(default_factory=default_icon, sa_type=JSONB)
    description: Optional[dict[str, str]] = Field(default=None, sa_type=JSONB)
    active: bool = Field(default=True)
    sequence: int = Field(default=10)
    entity: "CoreEntity" = Relationship(back_populates="actions")


from app.core.models.core_entity import CoreEntity  # noqa: E402
