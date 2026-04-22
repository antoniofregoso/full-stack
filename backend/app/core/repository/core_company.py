from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_company import CoreCompany
from app.core.models.core_system import CoreSystem


class CompanyRepository:
    @staticmethod
    def _query():
        return select(CoreCompany).options(selectinload(CoreCompany.systems_ids))

    @staticmethod
    async def create(company: CoreCompany, system_ids: list[int] | None = None) -> CoreCompany:
        async with db as session:
            session.add(company)
            await session.flush()

            if system_ids is not None:
                company.systems_ids = []
                if system_ids:
                    systems_result = await session.execute(
                        select(CoreSystem).where(CoreSystem.id.in_(system_ids))
                    )
                    company.systems_ids = systems_result.scalars().all()

            await session.commit()
            result = await session.execute(
                CompanyRepository._query().where(CoreCompany.id == company.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreCompany]:
        async with db as session:
            result = await session.execute(
                CompanyRepository._query().order_by(CoreCompany.name)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(company_id: int) -> Optional[CoreCompany]:
        async with db as session:
            result = await session.execute(
                CompanyRepository._query().where(CoreCompany.id == company_id)
            )
            return result.scalars().first()

    @staticmethod
    async def update(
        company_id: int,
        payload: dict,
        system_ids: list[int] | None = None,
    ) -> Optional[CoreCompany]:
        async with db as session:
            result = await session.execute(
                select(CoreCompany).where(CoreCompany.id == company_id)
            )
            company = result.scalars().first()
            if company is None:
                return None

            for field, value in payload.items():
                setattr(company, field, value)

            if system_ids is not None:
                company.systems_ids = []
                if system_ids:
                    selected_systems_result = await session.execute(
                        select(CoreSystem).where(CoreSystem.id.in_(system_ids))
                    )
                    company.systems_ids = selected_systems_result.scalars().all()

            session.add(company)
            await session.commit()
            result = await session.execute(
                CompanyRepository._query().where(CoreCompany.id == company.id)
            )
            return result.scalars().first()

    @staticmethod
    async def delete(company_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreCompany).where(CoreCompany.id == company_id)
            )
            company = result.scalars().first()
            if company is None:
                return False

            await session.delete(company)
            await session.commit()
            return True
