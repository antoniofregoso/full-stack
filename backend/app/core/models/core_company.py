from typing import TYPE_CHECKING, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.core.models.core_audit import CoreAudit

if TYPE_CHECKING:
    from app.core.models.core_system import CoreSystem

class CoreCompanySystemLink(SQLModel, table=True):
    __tablename__ = "core_company_system_link"

    company_id: Optional[int] = Field(default=None, foreign_key="core_companies.id", primary_key=True)
    system_id: Optional[int] = Field(default=None, foreign_key="core_systems.id", primary_key=True)
    description: Optional[dict[str, str]] = Field(default=None, sa_type=JSONB)


class CoreCompany(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_companies"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str
    active: bool = Field(default=False)
    sequence: Optional[int] = Field(default=10)
    currency_id: Optional[int] = Field(default=None, foreign_key="core_currencies.id")
    color: Optional[str] = None
    street: Optional[str] = None
    street2: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[int] = Field(default=None, foreign_key="core_country_states.id")
    country_id: Optional[int] = Field(default=None, foreign_key="core_countries.id")
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    vat: Optional[str] = None
    lang_id: Optional[int] = Field(default=None, foreign_key="core_langs.id")
    user_id: Optional[int] = Field(default=None, foreign_key="auth_users.id")
    users_ids: list["AuthUser"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "AuthUser.company_id"},
    )
    systems_ids: list["CoreSystem"] = Relationship(link_model=CoreCompanySystemLink)


from app.core.models.core_system import CoreSystem  # noqa: E402
