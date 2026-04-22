from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr, constr
from sqlalchemy import UniqueConstraint
from app.core.models.core_audit import CoreAudit    

class ThemeMode(str, Enum):
    light = "light"
    dark = "dark"
    system = "system"


class UserType(str, Enum):
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"
    AIAGENT = "AIAGENT"


class AuthUser(CoreAudit, SQLModel, table=True):
    __tablename__ = "auth_users"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    name: constr(min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    password: constr(min_length=8)
    active: bool = Field(default=True)
    theme: ThemeMode = Field(default=ThemeMode.system)
    user_type: UserType = Field(default=UserType.HUMAN)
    lang_id: Optional[int] = Field(default=None, foreign_key="core_langs.id")
    tz_id: Optional[int] = Field(default=None, foreign_key="core_timezones.id")
    tz_offset: Optional[int] = None
    page_size: Optional[int] = Field(default=25)
    company_id: Optional[int] = Field(default=None, foreign_key="core_companies.id")


class AuthRole(CoreAudit, SQLModel, table=True):
    __tablename__ = "auth_roles"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    active: bool = Field(default=True)


class AuthPermission(CoreAudit, SQLModel, table=True):
    __tablename__ = "auth_permissions"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    code: str = Field(index=True, unique=True)
    description: Optional[str] = None
    active: bool = Field(default=True)


class AuthUserRole(CoreAudit, SQLModel, table=True):
    __tablename__ = "auth_user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_auth_user_roles_user_role"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="auth_users.id")
    role_id: int = Field(foreign_key="auth_roles.id")


class AuthRolePermission(CoreAudit, SQLModel, table=True):
    __tablename__ = "auth_role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_auth_role_permissions_role_permission"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    role_id: int = Field(foreign_key="auth_roles.id")
    permission_id: int = Field(foreign_key="auth_permissions.id")
