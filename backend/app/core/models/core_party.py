from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import DateTime
from app.core.models.core_audit import CoreAudit

class CoreRole(CoreAudit,SQLModel, table=True):
    __tablename__ = "core_roles"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str

class CorePartyRole(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_party_roles"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    role_id: int = Field(foreign_key="core_roles.id")
    party_id: int = Field(foreign_key="core_parties.id")
    start_date: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        nullable=True,
    )
    end_date: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        nullable=True,
    )
    
class CoreParty(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_parties"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str
    active: bool = Field(default=True)
    sequence: Optional[int] = Field(default=10)
    color: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="core_parties.id")
    child_parties: list["CoreParty"] = Relationship()
    lang_id: Optional[int] = Field(default=None, foreign_key="core_langs.id")
    street: Optional[str] = None
    street2: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[int] = Field(default=None, foreign_key="core_country_states.id")
    country_id: Optional[int] = Field(default=None, foreign_key="core_countries.id")
    tz_id: Optional[int] = Field(default=None, foreign_key="core_timezones.id")
    tz_offset: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    function: Optional[str] = None
    website: Optional[str] = None
    vat: Optional[str] = None
    avatar_url: Optional[str] = None
    is_company: bool = Field(default=False)
    company_id: Optional[int] = Field(default=None, foreign_key="core_companies.id")
