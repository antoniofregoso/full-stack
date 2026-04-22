from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.core.models.core_audit import CoreAudit
from app.infrastructure.model_defaults import default_icon
from app.infrastructure.selections import OperationalStatus

if TYPE_CHECKING:
    from app.core.models.core_entity import CoreEntity
    from app.core.models.core_team import CoreTeam


class CoreModule(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_modules"
    __table_args__ = (
        UniqueConstraint("team_id", "code", name="uq_core_modules_team_code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    team_id: int = Field(foreign_key="core_teams.id")
    code: str = Field(index=True)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    icon: dict[str, str] = Field(default_factory=default_icon, sa_type=JSONB)
    description: Optional[dict[str, str]] = Field(default=None, sa_type=JSONB)
    active: bool = Field(default=True)
    status: OperationalStatus = Field(
        default=OperationalStatus.ON_TRACK,
        sa_type=SAEnum(
            OperationalStatus,
            name="operational_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
    )
    sequence: int = Field(default=10)
    color: Optional[str] = None
    team: "CoreTeam" = Relationship(back_populates="modules")
    entities: list["CoreEntity"] = Relationship(back_populates="module")


from app.core.models.core_entity import CoreEntity  # noqa: E402
from app.core.models.core_team import CoreTeam  # noqa: E402
