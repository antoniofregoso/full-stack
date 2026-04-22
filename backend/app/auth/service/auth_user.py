from dataclasses import asdict

from fastapi import HTTPException

from app.auth.graphql.types import AdminUpdateUserInput, UpdateMyProfileInput, UserType
from app.auth.models.auth_user import AuthUser, ThemeMode, UserType as AuthUserType
from app.auth.repository.auth_user import AuthUserRepository
from app.core.service.core_user_assignment import UserAssignmentService


class AuthUserService:

    @staticmethod
    async def _serialize(user: AuthUser) -> UserType:
        return UserType(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            active=user.active,
            theme=user.theme.value if hasattr(user.theme, "value") else str(user.theme),
            user_type=user.user_type.value
            if hasattr(user.user_type, "value")
            else str(user.user_type),
            lang_id=user.lang_id,
            tz_id=user.tz_id,
            tz_offset=user.tz_offset,
            page_size=user.page_size,
            company_id=user.company_id,
            landing_path=await UserAssignmentService.get_my_landing_path(user.id),
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized_name = name.strip()
        if len(normalized_name) < 2:
            raise HTTPException(status_code=400, detail="name must be at least 2 characters")
        return normalized_name

    @staticmethod
    def _normalize_page_size(page_size: int) -> int:
        if page_size < 1:
            raise HTTPException(status_code=400, detail="page_size must be greater than 0")
        return page_size

    @staticmethod
    def _normalize_avatar_url(avatar_url: str | None) -> str | None:
        if avatar_url is None:
            return None
        normalized_avatar_url = avatar_url.strip()
        return normalized_avatar_url or None

    @staticmethod
    def _normalize_self_update(payload: UpdateMyProfileInput) -> dict:
        data = {key: value for key, value in asdict(payload).items() if value is not None}
        if "name" in data:
            data["name"] = AuthUserService._normalize_name(data["name"])
        if "avatar_url" in data:
            data["avatar_url"] = AuthUserService._normalize_avatar_url(data["avatar_url"])
        if "theme" in data:
            data["theme"] = ThemeMode(data["theme"])
        if "page_size" in data:
            data["page_size"] = AuthUserService._normalize_page_size(data["page_size"])
        return data

    @staticmethod
    def _normalize_admin_update(payload: AdminUpdateUserInput) -> dict:
        data = {key: value for key, value in asdict(payload).items() if value is not None}
        if "name" in data:
            data["name"] = AuthUserService._normalize_name(data["name"])
        if "avatar_url" in data:
            data["avatar_url"] = AuthUserService._normalize_avatar_url(data["avatar_url"])
        if "email" in data:
            data["email"] = data["email"].strip().lower()
            if not data["email"]:
                raise HTTPException(status_code=400, detail="email is required")
        if "theme" in data:
            data["theme"] = ThemeMode(data["theme"])
        if "page_size" in data:
            data["page_size"] = AuthUserService._normalize_page_size(data["page_size"])
        return data

    @staticmethod
    async def get_all() -> list[UserType]:
        users = await AuthUserRepository.get_all()
        return [await AuthUserService._serialize(user) for user in users]

    @staticmethod
    async def get_me(user_id: int) -> UserType:
        user = await AuthUserRepository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return await AuthUserService._serialize(user)

    @staticmethod
    async def update_my_profile(user_id: int, payload: UpdateMyProfileInput) -> UserType:
        user = await AuthUserRepository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        if user.user_type == AuthUserType.SYSTEM:
            raise HTTPException(status_code=403, detail="system users cannot update profile here")

        data = AuthUserService._normalize_self_update(payload)
        if not data:
            raise HTTPException(status_code=400, detail="at least one field is required")

        updated = await AuthUserRepository.update(user_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="user not found")
        return await AuthUserService._serialize(updated)

    @staticmethod
    async def update_by_admin(user_id: int, payload: AdminUpdateUserInput) -> UserType:
        user = await AuthUserRepository.get_by_id(user_id, include_system=True)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        if user.user_type == AuthUserType.SYSTEM:
            raise HTTPException(status_code=403, detail="system users cannot be updated from admin UI")

        data = AuthUserService._normalize_admin_update(payload)
        if not data:
            raise HTTPException(status_code=400, detail="at least one field is required")

        if "email" in data:
            existing_user = await AuthUserRepository.get_by_email(data["email"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(status_code=400, detail="email already exists")

        updated = await AuthUserRepository.update(user_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="user not found")
        return await AuthUserService._serialize(updated)
