from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_timezone import CoreTimezone
from app.core.models.core_country import CoreCountry
from app.core.models.core_country_timezone_rel import CoreCountryTimezoneRel


class TimezoneRepository:

    @staticmethod
    def _query():
        return select(CoreTimezone).options(selectinload(CoreTimezone.countries))

    @staticmethod
    async def create(timezone: CoreTimezone) -> CoreTimezone:
        async with db as session:
            country_ids = [country.id for country in timezone.countries if country.id is not None]
            persisted_timezone = CoreTimezone(
                name=timezone.name,
                code=timezone.code,
                offset=timezone.offset,
            )
            session.add(persisted_timezone)
            await session.flush()

            if country_ids:
                country_result = await session.execute(
                    select(CoreCountry).where(CoreCountry.id.in_(country_ids))
                )
                persisted_timezone.countries = country_result.scalars().all()

            await session.commit()
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.id == persisted_timezone.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreTimezone]:
        async with db as session:
            result = await session.execute(
                TimezoneRepository._query().order_by(CoreTimezone.name)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(timezone_id: int) -> Optional[CoreTimezone]:
        async with db as session:
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.id == timezone_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_country(country_id: int) -> list[CoreTimezone]:
        async with db as session:
            result = await session.execute(
                TimezoneRepository._query()
                .outerjoin(
                    CoreCountryTimezoneRel,
                    CoreCountryTimezoneRel.timezone_id == CoreTimezone.id,
                )
                .where(
                    CoreCountryTimezoneRel.country_id == country_id
                )
                .order_by(CoreTimezone.name)
                .distinct()
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_code(code: str) -> Optional[CoreTimezone]:
        async with db as session:
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.code == code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(timezone_id: int, payload: dict) -> Optional[CoreTimezone]:
        async with db as session:
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.id == timezone_id)
            )
            timezone = result.scalars().first()
            if timezone is None:
                return None

            country_ids = payload.pop("country_ids", None)
            for field, value in payload.items():
                setattr(timezone, field, value)

            if country_ids is not None:
                if country_ids:
                    country_result = await session.execute(
                        select(CoreCountry).where(CoreCountry.id.in_(country_ids))
                    )
                    countries = country_result.scalars().all()
                else:
                    countries = []
                timezone.countries = countries

            session.add(timezone)
            await session.commit()
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.id == timezone.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_ids(timezone_ids: list[int]) -> list[CoreTimezone]:
        if not timezone_ids:
            return []

        async with db as session:
            result = await session.execute(
                TimezoneRepository._query().where(CoreTimezone.id.in_(timezone_ids))
            )
            return result.scalars().all()

    @staticmethod
    async def delete(timezone_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreTimezone).where(CoreTimezone.id == timezone_id)
            )
            timezone = result.scalars().first()
            if timezone is None:
                return False

            await session.delete(timezone)
            await session.commit()
            return True
