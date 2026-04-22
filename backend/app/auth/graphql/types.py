from enum import Enum
from typing import Optional

import strawberry

from app.auth.models.auth_user import ThemeMode

@strawberry.input
class RegisterInput:
    name: str
    email: str
    password: str
    avatar_url: Optional[str] = None

@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class ChangePasswordInput:
    current_password: str
    new_password: str


@strawberry.type
class LoginType:
    email: str
    token: str


@strawberry.type
class UserType:
    id: int
    email: str
    name: str
    avatar_url: Optional[str]
    active: bool
    theme: str
    user_type: str
    lang_id: Optional[int]
    tz_id: Optional[int]
    tz_offset: Optional[int]
    page_size: Optional[int]
    company_id: Optional[int]
    landing_path: Optional[str]


@strawberry.enum
class ThemeModeEnum(str, Enum):
    light = ThemeMode.light.value
    dark = ThemeMode.dark.value
    system = ThemeMode.system.value


@strawberry.input
class UpdateMyProfileInput:
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    theme: Optional[ThemeModeEnum] = None
    lang_id: Optional[int] = None
    tz_id: Optional[int] = None
    tz_offset: Optional[int] = None
    page_size: Optional[int] = None


@strawberry.input
class AdminUpdateUserInput:
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    active: Optional[bool] = None
    theme: Optional[ThemeModeEnum] = None
    lang_id: Optional[int] = None
    tz_id: Optional[int] = None
    tz_offset: Optional[int] = None
    page_size: Optional[int] = None
    company_id: Optional[int] = None
