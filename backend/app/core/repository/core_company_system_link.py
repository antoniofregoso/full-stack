from typing import Optional

from sqlmodel import select

from config import db
from app.core.models.core_company import CoreCompanySystemLink


class CompanySystemLinkRepository:
    @staticmethod
    async def create(link: CoreCompanySystemLink) -> CoreCompanySystemLink:
        async with db as session:
            session.add(link)
            await session.commit()
            await session.refresh(link)
            return link

    @staticmethod
    async def get_all() -> list[CoreCompanySystemLink]:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink).order_by(
                    CoreCompanySystemLink.company_id,
                    CoreCompanySystemLink.system_id,
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_ids(company_id: int, system_id: int) -> Optional[CoreCompanySystemLink]:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink).where(
                    CoreCompanySystemLink.company_id == company_id,
                    CoreCompanySystemLink.system_id == system_id,
                )
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_company(company_id: int) -> list[CoreCompanySystemLink]:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink)
                .where(CoreCompanySystemLink.company_id == company_id)
                .order_by(CoreCompanySystemLink.system_id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_system(system_id: int) -> list[CoreCompanySystemLink]:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink)
                .where(CoreCompanySystemLink.system_id == system_id)
                .order_by(CoreCompanySystemLink.company_id)
            )
            return result.scalars().all()

    @staticmethod
    async def update(
        current_company_id: int,
        current_system_id: int,
        payload: dict,
    ) -> Optional[CoreCompanySystemLink]:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink).where(
                    CoreCompanySystemLink.company_id == current_company_id,
                    CoreCompanySystemLink.system_id == current_system_id,
                )
            )
            link = result.scalars().first()
            if link is None:
                return None

            for field, value in payload.items():
                setattr(link, field, value)

            session.add(link)
            await session.commit()
            await session.refresh(link)
            return link

    @staticmethod
    async def delete(company_id: int, system_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreCompanySystemLink).where(
                    CoreCompanySystemLink.company_id == company_id,
                    CoreCompanySystemLink.system_id == system_id,
                )
            )
            link = result.scalars().first()
            if link is None:
                return False

            await session.delete(link)
            await session.commit()
            return True
