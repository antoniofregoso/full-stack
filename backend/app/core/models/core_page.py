from typing import Optional

from sqlalchemy import Index
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from app.core.models.core_audit import CoreAudit 

class CorePage(CoreAudit, SQLModel, table=True):
    __tablename__ = "core_pages"
    __table_args__ = (
        Index("ix_core_pages_keys_gin", "keys", postgresql_using="gin"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    description: dict[str, str] = Field(default_factory=dict, sa_type=JSONB)
    keys: Optional[dict] = Field(default=None, sa_type=JSONB)
    view: Optional[dict] = Field(default=None, sa_type=JSONB)
    active: bool = Field(default=True)
    sequence: int = Field(default=10)
    color: Optional[str] = None
    public: bool = Field(default=False)
