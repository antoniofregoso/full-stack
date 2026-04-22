from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import LangInput, LangType
from app.core.models.core_lang import CoreLang
from app.core.repository.core_lang import LangRepository


class LangService:

    @staticmethod
    def _serialize(lang: CoreLang) -> LangType:
        return LangType(
            id=lang.id,
            name=lang.name,
            code=lang.code,
            iso_code=lang.iso_code,
            url_code=lang.url_code,
            date_format=lang.date_format,
            time_format=lang.time_format,
            week_start=lang.week_start,
            flag=lang.flag,
            active=lang.active,
        )

    @staticmethod
    def _normalize(payload: LangInput) -> dict:
        data = asdict(payload)
        data["name"] = data["name"].strip()
        data["code"] = data["code"].strip()
        data["iso_code"] = data["iso_code"].strip()
        data["url_code"] = data["url_code"].strip()
        if data.get("date_format"):
            data["date_format"] = data["date_format"].strip()
        if data.get("time_format"):
            data["time_format"] = data["time_format"].strip()
        if data.get("flag"):
            data["flag"] = data["flag"].strip()
        if data.get("week_start") is not None:
            data["week_start"] = int(data["week_start"])

        if not data["code"] or not data["name"] or not data["iso_code"] or not data["url_code"]:
            raise HTTPException(
                status_code=400,
                detail="name, code, iso_code and url_code are required",
            )
        if data.get("week_start") is not None and data["week_start"] not in {1, 2, 3, 4, 5, 6, 7}:
            raise HTTPException(status_code=400, detail="week_start must be between 1 and 7")
        return data

    @staticmethod
    async def create(payload: LangInput) -> LangType:
        data = LangService._normalize(payload)
        existing_code = await LangRepository.get_by_code(data["code"])
        if existing_code:
            raise HTTPException(status_code=400, detail="language code already exists")
        existing_iso_code = await LangRepository.get_by_iso_code(data["iso_code"])
        if existing_iso_code:
            raise HTTPException(status_code=400, detail="language iso_code already exists")
        existing_url_code = await LangRepository.get_by_url_code(data["url_code"])
        if existing_url_code:
            raise HTTPException(status_code=400, detail="language url_code already exists")

        created = await LangRepository.create(CoreLang(**data))
        return LangService._serialize(created)

    @staticmethod
    async def get_all() -> list[LangType]:
        langs = await LangRepository.get_all()
        return [LangService._serialize(lang) for lang in langs]

    @staticmethod
    async def get_by_code(code: str) -> LangType | None:
        lang = await LangRepository.get_by_code(code.strip())
        return LangService._serialize(lang) if lang else None

    @staticmethod
    async def update(lang_id: int, payload: LangInput) -> LangType:
        data = LangService._normalize(payload)
        existing_code = await LangRepository.get_by_code(data["code"])
        if existing_code and existing_code.id != lang_id:
            raise HTTPException(status_code=400, detail="language code already exists")
        existing_iso_code = await LangRepository.get_by_iso_code(data["iso_code"])
        if existing_iso_code and existing_iso_code.id != lang_id:
            raise HTTPException(status_code=400, detail="language iso_code already exists")
        existing_url_code = await LangRepository.get_by_url_code(data["url_code"])
        if existing_url_code and existing_url_code.id != lang_id:
            raise HTTPException(status_code=400, detail="language url_code already exists")

        updated = await LangRepository.update(lang_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="language not found")

        return LangService._serialize(updated)

    @staticmethod
    async def delete(lang_id: int) -> bool:
        deleted = await LangRepository.delete(lang_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="language not found")
        return True
