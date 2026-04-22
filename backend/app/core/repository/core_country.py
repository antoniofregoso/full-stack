from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config import db
from app.core.models.core_country import CoreCountry, CoreCountryState
from app.core.models.core_timezone import CoreTimezone


class CountryRepository:

    @staticmethod
    def _query():
        return select(CoreCountry).options(
            selectinload(CoreCountry.states),
            selectinload(CoreCountry.timezones),
        )

    @staticmethod
    async def create(country: CoreCountry) -> CoreCountry:
        async with db as session:
            timezone_ids = [timezone.id for timezone in country.timezones if timezone.id is not None]
            states = [
                {"code": state.code, "name": state.name}
                for state in country.states
            ]

            persisted_country = CoreCountry(
                code=country.code,
                name=country.name,
                phone_code=country.phone_code,
                currency_id=country.currency_id,
            )
            session.add(persisted_country)
            await session.flush()

            persisted_country.states = [
                CoreCountryState(country_id=persisted_country.id, **state_payload)
                for state_payload in states
            ]

            if timezone_ids:
                timezone_result = await session.execute(
                    select(CoreTimezone).where(CoreTimezone.id.in_(timezone_ids))
                )
                persisted_country.timezones = timezone_result.scalars().all()

            await session.commit()
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.id == persisted_country.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_all() -> list[CoreCountry]:
        async with db as session:
            result = await session.execute(
                CountryRepository._query().order_by(
                    func.coalesce(
                        CoreCountry.name["es_MX"].astext,
                        CoreCountry.name["en_US"].astext,
                        CoreCountry.code,
                    )
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(country_id: int) -> Optional[CoreCountry]:
        async with db as session:
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.id == country_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_code(code: str) -> Optional[CoreCountry]:
        async with db as session:
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.code == code)
            )
            return result.scalars().first()

    @staticmethod
    async def update(country_id: int, payload: dict) -> Optional[CoreCountry]:
        async with db as session:
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.id == country_id)
            )
            country = result.scalars().first()
            if country is None:
                return None

            states = payload.pop("states", None)
            timezone_ids = payload.pop("timezone_ids", None)

            for field, value in payload.items():
                setattr(country, field, value)

            if states is not None:
                for state in list(country.states):
                    await session.delete(state)
                await session.flush()
                country.states = [
                    CoreCountryState(country_id=country.id, **state_payload)
                    for state_payload in states
                ]

            if timezone_ids is not None:
                if timezone_ids:
                    timezone_result = await session.execute(
                        select(CoreTimezone).where(CoreTimezone.id.in_(timezone_ids))
                    )
                    timezones = timezone_result.scalars().all()
                else:
                    timezones = []
                country.timezones = timezones

            session.add(country)
            await session.commit()
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.id == country.id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_by_ids(country_ids: list[int]) -> list[CoreCountry]:
        if not country_ids:
            return []

        async with db as session:
            result = await session.execute(
                CountryRepository._query().where(CoreCountry.id.in_(country_ids))
            )
            return result.scalars().all()

    @staticmethod
    async def delete(country_id: int) -> bool:
        async with db as session:
            result = await session.execute(
                select(CoreCountry).where(CoreCountry.id == country_id)
            )
            country = result.scalars().first()
            if country is None:
                return False

            await session.delete(country)
            await session.commit()
            return True
