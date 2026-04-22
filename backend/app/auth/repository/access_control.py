from sqlmodel import select
from config import db

from app.auth.models.auth_user import (
    AuthPermission,
    AuthRole,
    AuthRolePermission,
    AuthUser,
    AuthUserRole,
)


class AccessControlRepository:

    @staticmethod
    async def assign_role(user_id: int, role_name: str) -> bool:
        async with db as session:
            user_result = await session.execute(
                select(AuthUser.id).where(AuthUser.id == user_id)
            )
            if user_result.scalar_one_or_none() is None:
                return False

            role_result = await session.execute(
                select(AuthRole).where(AuthRole.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            if role is None:
                role = AuthRole(name=role_name)
                session.add(role)
                await session.flush()

            mapping_result = await session.execute(
                select(AuthUserRole.id).where(
                    AuthUserRole.user_id == user_id,
                    AuthUserRole.role_id == role.id,
                )
            )
            if mapping_result.scalar_one_or_none() is not None:
                return True

            session.add(AuthUserRole(user_id=user_id, role_id=role.id))
            await session.commit()
            return True

    @staticmethod
    async def has_permission(user_id: int, permission_code: str) -> bool:
        async with db as session:
            query = (
                select(AuthPermission.id)
                .join(
                    AuthRolePermission,
                    AuthPermission.id == AuthRolePermission.permission_id,
                )
                .join(AuthRole, AuthRole.id == AuthRolePermission.role_id)
                .join(AuthUserRole, AuthUserRole.role_id == AuthRole.id)
                .where(
                    AuthUserRole.user_id == user_id,
                    AuthPermission.code == permission_code,
                    AuthPermission.active == True,
                    AuthRole.active == True,
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def has_any_permission(user_id: int, permission_codes: list[str]) -> bool:
        if not permission_codes:
            return False

        async with db as session:
            query = (
                select(AuthPermission.id)
                .join(
                    AuthRolePermission,
                    AuthPermission.id == AuthRolePermission.permission_id,
                )
                .join(AuthRole, AuthRole.id == AuthRolePermission.role_id)
                .join(AuthUserRole, AuthUserRole.role_id == AuthRole.id)
                .where(
                    AuthUserRole.user_id == user_id,
                    AuthPermission.code.in_(permission_codes),
                    AuthPermission.active == True,
                    AuthRole.active == True,
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def assign_permission_to_role(role_name: str, permission_code: str) -> bool:
        async with db as session:
            role_result = await session.execute(
                select(AuthRole).where(AuthRole.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            if role is None:
                role = AuthRole(name=role_name)
                session.add(role)
                await session.flush()

            permission_result = await session.execute(
                select(AuthPermission).where(AuthPermission.code == permission_code)
            )
            permission = permission_result.scalar_one_or_none()
            if permission is None:
                permission = AuthPermission(code=permission_code)
                session.add(permission)
                await session.flush()

            mapping_result = await session.execute(
                select(AuthRolePermission.id).where(
                    AuthRolePermission.role_id == role.id,
                    AuthRolePermission.permission_id == permission.id,
                )
            )
            if mapping_result.scalar_one_or_none() is not None:
                return True

            session.add(
                AuthRolePermission(role_id=role.id, permission_id=permission.id)
            )
            await session.commit()
            return True
