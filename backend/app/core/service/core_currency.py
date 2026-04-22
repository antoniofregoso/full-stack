from dataclasses import asdict
from typing import Any

from fastapi import HTTPException

from app.core.graphql.types import CurrencyInput, CurrencyType
from app.core.models.core_currency import CoreCurrency
from app.core.repository.core_currency import CurrencyRepository


class CurrencyService:

    @staticmethod
    def _serialize(currency: CoreCurrency) -> CurrencyType:
        return CurrencyType(
            id=currency.id,
            code=currency.code,
            name=currency.name,
            iso_numeric=currency.iso_numeric,
            symbol=currency.symbol,
            currency_unit_label=currency.currency_unit_label,
            currency_subunit_label=currency.currency_subunit_label,
            rounding=currency.rounding,
            position=currency.position,
            active=currency.active,
        )

    @staticmethod
    def _normalize_json_label(value: Any) -> dict[str, str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            text = value.strip()
            return {"es_MX": text} if text else None
        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail="currency labels must be objects")

        normalized: dict[str, str] = {}
        for key, label in value.items():
            locale = str(key).strip()
            text = str(label).strip() if label is not None else ""
            if locale and text:
                normalized[locale] = text
        return normalized or None

    @staticmethod
    def _normalize(payload: CurrencyInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().upper()
        data["name"] = data["name"].strip()
        data["symbol"] = data["symbol"].strip()
        data["position"] = getattr(data["position"], "value", data["position"]).strip().upper()
        data["currency_unit_label"] = CurrencyService._normalize_json_label(
            data.get("currency_unit_label")
        )
        data["currency_subunit_label"] = CurrencyService._normalize_json_label(
            data.get("currency_subunit_label")
        )
        if not data["code"] or not data["name"]:
            raise HTTPException(status_code=400, detail="code and name are required")
        if data["position"] not in {"BEFORE", "AFTER"}:
            raise HTTPException(status_code=400, detail="position must be BEFORE or AFTER")
        return data

    @staticmethod
    async def create(payload: CurrencyInput) -> CurrencyType:
        data = CurrencyService._normalize(payload)
        existing = await CurrencyRepository.get_by_code(data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="currency code already exists")

        created = await CurrencyRepository.create(CoreCurrency(**data))
        return CurrencyService._serialize(created)

    @staticmethod
    async def get_all() -> list[CurrencyType]:
        currencies = await CurrencyRepository.get_all()
        return [CurrencyService._serialize(currency) for currency in currencies]

    @staticmethod
    async def get_by_code(code: str) -> CurrencyType | None:
        currency = await CurrencyRepository.get_by_code(code.strip().upper())
        return CurrencyService._serialize(currency) if currency else None

    @staticmethod
    async def update(currency_id: int, payload: CurrencyInput) -> CurrencyType:
        data = CurrencyService._normalize(payload)
        existing = await CurrencyRepository.get_by_code(data["code"])
        if existing and existing.id != currency_id:
            raise HTTPException(status_code=400, detail="currency code already exists")

        updated = await CurrencyRepository.update(currency_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="currency not found")

        return CurrencyService._serialize(updated)

    @staticmethod
    async def delete(currency_id: int) -> bool:
        deleted = await CurrencyRepository.delete(currency_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="currency not found")
        return True
