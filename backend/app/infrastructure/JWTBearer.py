import typing

from strawberry.permission import BasePermission
from strawberry.types import Info

from app.auth.repository.auth_user import AuthUserRepository
from app.auth.service.access_control import AccessControlService
from app.infrastructure.JWTManager import JWTManager


def _extract_token(info: Info) -> str | None:
    request = info.context["request"]
    authentication = request.headers.get("Authorization")
    if not authentication or not authentication.startswith("Bearer "):
        return None
    return authentication.removeprefix("Bearer ").strip()


async def get_current_user_id(info: Info) -> int | None:
    token = _extract_token(info)
    if not token:
        return None

    try:
        payload = JWTManager.verify_token(token)
    except Exception:
        return None

    user_id = payload.get("uid")
    if isinstance(user_id, int):
        return user_id

    email = payload.get("sub")
    if not email:
        return None

    user = await AuthUserRepository.get_by_email(email)
    return user.id if user else None


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        return await get_current_user_id(info) is not None


def HasModuleAccess(module: str, action: str) -> type[BasePermission]:
    module = module.strip().lower()
    action = action.strip().lower()

    class _HasModuleAccess(BasePermission):
        message = f"Missing permission {module}.{action}"

        async def has_permission(
            self, source: typing.Any, info: Info, **kwargs
        ) -> bool:
            user_id = await get_current_user_id(info)
            if user_id is None:
                return False
            return await AccessControlService.has_module_permission(
                user_id, module, action
            )

    return _HasModuleAccess


def HasScopedAccess(module: str, resource: str, action: str) -> type[BasePermission]:
    module = module.strip().lower()
    resource = resource.strip().lower()
    action = action.strip().lower()

    class _HasScopedAccess(BasePermission):
        message = f"Missing permission {module}.{resource}.{action}"

        async def has_permission(
            self, source: typing.Any, info: Info, **kwargs
        ) -> bool:
            user_id = await get_current_user_id(info)
            if user_id is None:
                return False
            return await AccessControlService.has_scoped_permission(
                user_id, module, resource, action
            )

    return _HasScopedAccess
