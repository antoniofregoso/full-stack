from fastapi import HTTPException, logger
from passlib.context import CryptContext

from app.auth.models.auth_user import AuthUser, UserType
from app.auth.repository.auth_user import AuthUserRepository
from app.auth.graphql.types import ChangePasswordInput, RegisterInput, LoginInput, LoginType
from app.infrastructure.JWTManager import JWTManager

import logging
logger = logging.getLogger(__name__)

class AuthenticationService:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return AuthenticationService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return AuthenticationService.pwd_context.hash(password)

    @staticmethod
    async def login(login: LoginInput):
        logger.debug(f"Attempting login for email: {login.email}")
        existing_user = await AuthUserRepository.get_by_email(login.email)

        if not existing_user:
            logger.warning(f"Login failed: Email {login.email} not found")
            raise HTTPException(status_code=401, detail="Email not found!")

        if existing_user.user_type == UserType.SYSTEM:
            logger.warning(f"Login failed: System user {login.email} cannot authenticate with password")
            raise HTTPException(status_code=403, detail="System users cannot login with password")

        if not AuthenticationService.verify_password(login.password, existing_user.password):
            logger.warning(f"Login failed: Incorrect password for email {login.email}")
            raise HTTPException(status_code=401, detail="Incorrect password!")

        token = JWTManager.generate_token(
            {"sub": existing_user.email, "uid": existing_user.id}
        )
        logger.info(f"Login successful for email: {login.email}")
        return LoginType(email=existing_user.email, token=token)

    @staticmethod
    async def register(user: RegisterInput):
        existing_user = await AuthUserRepository.get_by_email(user.email)

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = AuthenticationService.hash_password(user.password)
        avatar_url = user.avatar_url.strip() if user.avatar_url else None
        if avatar_url == "":
            avatar_url = None
        new_user = AuthUser(
            name=user.name,
            email=user.email,
            avatar_url=avatar_url,
            password=hashed_password,
            user_type=UserType.HUMAN,
        )
        await AuthUserRepository.create(new_user)

        return "User registered successfully"

    @staticmethod
    async def change_my_password(user_id: int, payload: ChangePasswordInput) -> str:
        user = await AuthUserRepository.get_by_id(user_id, include_system=True)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.user_type == UserType.SYSTEM:
            raise HTTPException(status_code=403, detail="System users cannot change password")

        if not AuthenticationService.verify_password(payload.current_password, user.password):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        new_password = payload.new_password.strip()
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

        if AuthenticationService.verify_password(new_password, user.password):
            raise HTTPException(status_code=400, detail="New password must be different from current password")

        await AuthUserRepository.update(
            user_id,
            {"password": AuthenticationService.hash_password(new_password)},
        )

        return "Password updated successfully"

        
