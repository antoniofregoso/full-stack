import strawberry
from app.auth.graphql.types import UserType
from app.auth.service.auth_user import AuthUserService
from app.infrastructure.JWTBearer import HasModuleAccess, IsAuthenticated, get_current_user_id

AuthReadAccess = HasModuleAccess("auth", "read")

@strawberry.type
class Query:
    @strawberry.field
    def auth_hello(self) -> str:
        return "Auth Hello"

    @strawberry.field(permission_classes=[AuthReadAccess])
    async def get_all_users(self) -> list[UserType]:
        return await AuthUserService.get_all()

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: strawberry.Info) -> UserType:
        user_id = await get_current_user_id(info)
        return await AuthUserService.get_me(user_id)
