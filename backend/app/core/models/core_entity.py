from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.core.models.core_audit import CoreAudit
from app.infrastructure.model_defaults import default_icon

if TYPE_CHECKING:
    from app.core.models.core_action import CoreAction
    from app.core.models.core_feature import CoreFeature
    from app.core.models.core_module import CoreModule


class CoreEntity(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_entities"
    __table_args__ = (
        UniqueConstraint("module_id", "code", name="uq_core_entities_module_code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    module_id: int = Field(foreign_key="core_modules.id")
    code: str = Field(index=True)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    icon: dict[str, str] = Field(default_factory=default_icon, sa_type=JSONB)
    description: Optional[dict[str, str]] = Field(default=None, sa_type=JSONB)
    active: bool = Field(default=True)
    sequence: int = Field(default=10)
    color: Optional[str] = None
    module: "CoreModule" = Relationship(back_populates="entities")
    features: list["CoreFeature"] = Relationship(back_populates="entity")
    actions: list["CoreAction"] = Relationship(back_populates="entity")


from app.core.models.core_action import CoreAction  # noqa: E402
from app.core.models.core_feature import CoreFeature  # noqa: E402
from app.core.models.core_module import CoreModule  # noqa: E402
