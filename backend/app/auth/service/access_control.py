from app.auth.repository.access_control import AccessControlRepository


class AccessControlService:

    @staticmethod
    async def assign_role(user_id: int, role_name: str) -> bool:
        role_name = role_name.strip()
        if not role_name:
            return False
        return await AccessControlRepository.assign_role(user_id, role_name)

    @staticmethod
    async def has_permission(user_id: int, permission_code: str) -> bool:
        permission_code = permission_code.strip()
        if not permission_code:
            return False
        return await AccessControlRepository.has_permission(user_id, permission_code)

    @staticmethod
    async def has_module_permission(user_id: int, module: str, action: str) -> bool:
        module = module.strip().lower()
        action = action.strip().lower()
        if not module or not action:
            return False

        permission_codes = [
            f"{module}.{action}",
            f"{module}.*",
            "*.*",
        ]
        return await AccessControlRepository.has_any_permission(user_id, permission_codes)

    @staticmethod
    async def has_scoped_permission(
        user_id: int, module: str, resource: str, action: str
    ) -> bool:
        module = module.strip().lower()
        resource = resource.strip().lower()
        action = action.strip().lower()
        if not module or not resource or not action:
            return False

        permission_codes = list(
            dict.fromkeys(
                [
                    f"{module}.{resource}.{action}",
                    f"{module}.{resource}.*",
                    f"{module}.*.{action}",
                    f"{module}.*.*",
                    "*.*.*",
                ]
            )
        )
        return await AccessControlRepository.has_any_permission(user_id, permission_codes)

    @staticmethod
    async def assign_permission_to_role(role_name: str, permission_code: str) -> bool:
        role_name = role_name.strip()
        permission_code = permission_code.strip()
        if not role_name or not permission_code:
            return False
        return await AccessControlRepository.assign_permission_to_role(
            role_name, permission_code
        )

    @staticmethod
    async def assign_module_permission_to_role(
        role_name: str, module: str, action: str
    ) -> bool:
        module = module.strip().lower()
        action = action.strip().lower()
        if not module or not action:
            return False
        permission_code = f"{module}.{action}"
        return await AccessControlService.assign_permission_to_role(
            role_name, permission_code
        )

    @staticmethod
    async def assign_scoped_permission_to_role(
        role_name: str, module: str, resource: str, action: str
    ) -> bool:
        module = module.strip().lower()
        resource = resource.strip().lower()
        action = action.strip().lower()
        if not module or not resource or not action:
            return False
        permission_code = f"{module}.{resource}.{action}"
        return await AccessControlService.assign_permission_to_role(
            role_name, permission_code
        )
