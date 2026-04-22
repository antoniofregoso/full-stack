import strawberry

from app.auth.service.authentication import AuthenticationService
from app.auth.graphql.types import (
    AdminUpdateUserInput,
    ChangePasswordInput,
    LoginInput,
    LoginType,
    RegisterInput,
    UpdateMyProfileInput,
    UserType,
)
from app.auth.service.auth_user import AuthUserService
from app.auth.service.access_control import AccessControlService
from app.infrastructure.JWTBearer import HasModuleAccess, IsAuthenticated, get_current_user_id

AuthAdminAccess = HasModuleAccess("auth", "admin")

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, login: LoginInput) -> LoginType:
        return await AuthenticationService.login(login)

    @strawberry.mutation
    async def register(self, register: RegisterInput) -> str:
        return await AuthenticationService.register(register)

    @strawberry.mutation(permission_classes=[AuthAdminAccess])
    async def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        return await AccessControlService.assign_role(user_id, role_name)

    @strawberry.mutation(permission_classes=[AuthAdminAccess])
    async def assign_permission_to_role(self, role_name: str, permission_code: str) -> bool:
        return await AccessControlService.assign_permission_to_role(
            role_name, permission_code
        )

    @strawberry.mutation(permission_classes=[AuthAdminAccess])
    async def assign_module_permission_to_role(
        self, role_name: str, module: str, action: str
    ) -> bool:
        return await AccessControlService.assign_module_permission_to_role(
            role_name, module, action
        )

    @strawberry.mutation(permission_classes=[AuthAdminAccess])
    async def assign_scoped_permission_to_role(
        self, role_name: str, module: str, resource: str, action: str
    ) -> bool:
        return await AccessControlService.assign_scoped_permission_to_role(
            role_name, module, resource, action
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_my_profile(
        self, info: strawberry.Info, payload: UpdateMyProfileInput
    ) -> UserType:
        user_id = await get_current_user_id(info)
        return await AuthUserService.update_my_profile(user_id, payload)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def change_my_password(
        self, info: strawberry.Info, payload: ChangePasswordInput
    ) -> str:
        user_id = await get_current_user_id(info)
        return await AuthenticationService.change_my_password(user_id, payload)

    @strawberry.mutation(permission_classes=[AuthAdminAccess])
    async def update_user_by_admin(
        self, user_id: int, payload: AdminUpdateUserInput
    ) -> UserType:
        return await AuthUserService.update_by_admin(user_id, payload)
