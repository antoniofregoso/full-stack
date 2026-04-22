from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.core.models.core_audit import CoreAudit
from app.core.models.core_country_timezone_rel import CoreCountryTimezoneRel

if TYPE_CHECKING:
    from app.core.models.core_timezone import CoreTimezone

class CoreCountry(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_countries"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    code: str = Field(unique=True, index=True)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    phone_code: Optional[str] = None
    currency_id: Optional[int] = Field(default=None, foreign_key="core_currencies.id")
    states: list["CoreCountryState"] = Relationship()
    timezones: list["CoreTimezone"] = Relationship(
        back_populates="countries",
        link_model=CoreCountryTimezoneRel,
    )
    



class CoreCountryState(SQLModel, table=True):
    __tablename__ = "core_country_states"
    __table_args__ = (
        UniqueConstraint("country_id", "code", name="uq_country_state_country_code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    code: str = Field(index=True)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    country_id: int = Field(foreign_key="core_countries.id")


from app.core.models.core_timezone import CoreTimezone  # noqa: E402
