from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import TimezoneInput, TimezoneType
from app.core.models.core_timezone import CoreTimezone
from app.core.repository.core_country import CountryRepository
from app.core.repository.core_timezone import TimezoneRepository


class TimezoneService:

    @staticmethod
    def _serialize(timezone: CoreTimezone) -> TimezoneType:
        return TimezoneType(
            id=timezone.id,
            name=timezone.name,
            code=timezone.code,
            offset=timezone.offset,
            country_ids=[country.id for country in timezone.countries],
        )

    @staticmethod
    def _normalize(payload: TimezoneInput) -> dict:
        data = asdict(payload)
        data["name"] = data["name"].strip()
        data["code"] = data["code"].strip().upper()
        data["country_ids"] = list(dict.fromkeys(data.get("country_ids", [])))
        if not data["name"] or not data["code"]:
            raise HTTPException(status_code=400, detail="name and code are required")

        offset = data.get("offset")
        if offset is not None and (offset < -14 or offset > 14):
            raise HTTPException(
                status_code=400,
                detail="offset must be between -14 and 14",
            )
        return data

    @staticmethod
    async def _validate_countries(country_ids: list[int]):
        if not country_ids:
            return
        countries = await CountryRepository.get_by_ids(country_ids)
        if len(countries) != len(country_ids):
            raise HTTPException(status_code=400, detail="one or more countries do not exist")

    @staticmethod
    async def create(payload: TimezoneInput) -> TimezoneType:
        data = TimezoneService._normalize(payload)
        await TimezoneService._validate_countries(data.get("country_ids", []))

        existing = await TimezoneRepository.get_by_code(data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="timezone code already exists")

        country_ids = data.pop("country_ids")
        timezone = CoreTimezone(**data)
        timezone.countries = await CountryRepository.get_by_ids(country_ids)
        created = await TimezoneRepository.create(timezone)
        return TimezoneService._serialize(created)

    @staticmethod
    async def get_all() -> list[TimezoneType]:
        timezones = await TimezoneRepository.get_all()
        return [TimezoneService._serialize(timezone) for timezone in timezones]

    @staticmethod
    async def get_by_country(country_id: int) -> list[TimezoneType]:
        timezones = await TimezoneRepository.get_by_country(country_id)
        return [TimezoneService._serialize(timezone) for timezone in timezones]

    @staticmethod
    async def get_by_code(code: str) -> TimezoneType | None:
        timezone = await TimezoneRepository.get_by_code(code.strip().upper())
        return TimezoneService._serialize(timezone) if timezone else None

    @staticmethod
    async def update(timezone_id: int, payload: TimezoneInput) -> TimezoneType:
        data = TimezoneService._normalize(payload)
        await TimezoneService._validate_countries(data.get("country_ids", []))

        existing = await TimezoneRepository.get_by_code(data["code"])
        if existing and existing.id != timezone_id:
            raise HTTPException(status_code=400, detail="timezone code already exists")

        updated = await TimezoneRepository.update(timezone_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="timezone not found")

        return TimezoneService._serialize(updated)

    @staticmethod
    async def delete(timezone_id: int) -> bool:
        deleted = await TimezoneRepository.delete(timezone_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="timezone not found")
        return True
