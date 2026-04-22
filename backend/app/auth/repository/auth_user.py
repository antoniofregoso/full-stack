from app.auth.models.auth_user import AuthUser, UserType
from config import db
from sqlalchemy import select


class AuthUserRepository:


    
    @staticmethod
    async def create(user: AuthUser):
        async with db as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def get_all(include_system: bool = False):
        async with db as session:
            query = select(AuthUser)
            if not include_system:
                query = query.where(AuthUser.user_type != UserType.SYSTEM)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_by_id(id: int, include_system: bool = False):
        async with db as session:
            query = select(AuthUser).where(AuthUser.id == id)
            if not include_system:
                query = query.where(AuthUser.user_type != UserType.SYSTEM)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def update(id: int, user_data):
        async with db as session:
            # We locate the existing note
            query = select(AuthUser).where(AuthUser.id == id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                # We expect note_data to be a dict
                for key, value in user_data.items():
                    setattr(user, key, value)
                
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
            return None

    @staticmethod
    async def delete(id: int):
        async with db as session:
            query = select(AuthUser).where(AuthUser.id == id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_by_email(email: str):
        async with db as session:
            query = select(AuthUser).where(AuthUser.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
