from dataclasses import asdict
from typing import Any

from fastapi import HTTPException

from app.core.graphql.types import CountryInput, CountryStateType, CountryType
from app.core.models.core_country import CoreCountry, CoreCountryState
from app.core.repository.core_country import CountryRepository
from app.core.repository.core_timezone import TimezoneRepository


class CountryService:

    @staticmethod
    def _serialize(country: CoreCountry) -> CountryType:
        return CountryType(
            id=country.id,
            code=country.code,
            name=country.name,
            phone_code=country.phone_code,
            currency_id=country.currency_id,
            states=[
                CountryStateType(
                    id=state.id,
                    code=state.code,
                    name=state.name,
                    country_id=state.country_id,
                )
                for state in country.states
            ],
            timezone_ids=[timezone.id for timezone in country.timezones],
        )

    @staticmethod
    def _normalize_name(value: Any) -> dict[str, str]:
        if value is None:
            raise HTTPException(
                status_code=400,
                detail="name must be an object like {'es_MX': 'Mexico'}",
            )
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail="name must be an object like {'es_MX': 'Mexico'}",
            )

        normalized: dict[str, str] = {}
        for key, translation in value.items():
            locale = str(key).strip()
            text = str(translation).strip() if translation is not None else ""
            if locale and text:
                normalized[locale] = text
        if not normalized:
            raise HTTPException(
                status_code=400,
                detail="name must include at least one locale with text",
            )
        return normalized

    @staticmethod
    def _normalize(payload: CountryInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().upper()
        data["name"] = CountryService._normalize_name(data.get("name"))
        if data.get("phone_code"):
            data["phone_code"] = data["phone_code"].strip()
        data["states"] = [
            {
                "code": str(state.get("code") or "").strip().upper(),
                "name": CountryService._normalize_name(state.get("name")),
            }
            for state in data.get("states", [])
        ]
        data["timezone_ids"] = list(dict.fromkeys(data.get("timezone_ids", [])))
        if not data["code"]:
            raise HTTPException(
                status_code=400,
                detail="code and name are required",
            )
        for state in data["states"]:
            if not state["code"]:
                raise HTTPException(status_code=400, detail="state code is required")
        return data

    @staticmethod
    async def _validate_timezones(timezone_ids: list[int]) -> list:
        timezones = await TimezoneRepository.get_by_ids(timezone_ids)
        if len(timezones) != len(timezone_ids):
            raise HTTPException(status_code=400, detail="one or more timezones do not exist")
        return timezones

    @staticmethod
    async def create(payload: CountryInput) -> CountryType:
        data = CountryService._normalize(payload)
        timezone_ids = data.pop("timezone_ids")
        states = data.pop("states")
        existing = await CountryRepository.get_by_code(data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="country code already exists")

        country = CoreCountry(**data)
        country.states = [CoreCountryState(**state) for state in states]
        country.timezones = await CountryService._validate_timezones(timezone_ids)
        created = await CountryRepository.create(country)
        return CountryService._serialize(created)

    @staticmethod
    async def get_all() -> list[CountryType]:
        countries = await CountryRepository.get_all()
        return [CountryService._serialize(country) for country in countries]

    @staticmethod
    async def get_by_code(code: str) -> CountryType | None:
        country = await CountryRepository.get_by_code(code.strip().upper())
        return CountryService._serialize(country) if country else None

    @staticmethod
    async def update(country_id: int, payload: CountryInput) -> CountryType:
        data = CountryService._normalize(payload)
        await CountryService._validate_timezones(data["timezone_ids"])
        existing = await CountryRepository.get_by_code(data["code"])
        if existing and existing.id != country_id:
            raise HTTPException(status_code=400, detail="country code already exists")

        updated = await CountryRepository.update(country_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="country not found")

        return CountryService._serialize(updated)

    @staticmethod
    async def delete(country_id: int) -> bool:
        deleted = await CountryRepository.delete(country_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="country not found")
        return True
