from dataclasses import asdict
from typing import Any

from fastapi import HTTPException

from app.core.graphql.types import SystemInput, SystemType, TeamType
from app.core.models.core_system import CoreSystem
from app.core.repository.core_system import SystemRepository
from app.infrastructure.model_defaults import default_icon
from app.infrastructure.selections import OperationalStatus


class SystemService:
    VALID_STATUSES = {item.value for item in OperationalStatus}

    @staticmethod
    def _serialize(system: CoreSystem) -> SystemType:
        return SystemType(
            id=system.id,
            code=system.code,
            name=system.name,
            icon=system.icon,
            description=system.description,
            active=system.active,
            status=system.status,
            sequence=system.sequence,
            team_ids=[team.id for team in system.teams],
        )

    @staticmethod
    def _normalize_json_name(value: Any, field_name: str) -> dict[str, str] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be an object like {{'es_MX': 'Nombre'}}",
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
                detail=f"{field_name} must include at least one locale with text",
            )
        return normalized

    @staticmethod
    def _normalize_json_object(value: Any, field_name: str) -> dict:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be a JSON object",
        )
        return value

    @staticmethod
    def _normalize_icon(value: Any) -> dict[str, str]:
        icon = SystemService._normalize_json_object(value, "icon")
        return icon or default_icon()

    @staticmethod
    def _normalize_id_list(value: Any, field_name: str) -> list[int]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise HTTPException(status_code=400, detail=f"{field_name} must be a list of integers")

        normalized: list[int] = []
        seen: set[int] = set()
        for item in value:
            if not isinstance(item, int) or item <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field_name} must contain positive integers",
                )
            if item not in seen:
                seen.add(item)
                normalized.append(item)
        return normalized

    @staticmethod
    def _normalize_status(value: Any, field_name: str = "status") -> OperationalStatus:
        normalized = getattr(value, "value", value)
        if not isinstance(normalized, str):
            raise HTTPException(status_code=400, detail=f"{field_name} must be a valid status")

        normalized = normalized.strip().upper()
        if normalized not in SystemService.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be one of: AHEAD, ON_TRACK, AT_RISK, CRITICAL",
            )
        return OperationalStatus(normalized)

    @staticmethod
    def _normalize(payload: SystemInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().lower()
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        data["icon"] = SystemService._normalize_icon(data.get("icon"))
        data["status"] = SystemService._normalize_status(data.get("status"))
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if not data["code"] or data["name"] is None:
            raise HTTPException(status_code=400, detail="code and name are required")
        return data

    @staticmethod
    async def create(payload: SystemInput) -> SystemType:
        data = SystemService._normalize(payload)
        existing = await SystemRepository.get_by_code(data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="system code already exists")
        created = await SystemRepository.create(CoreSystem(**data))
        return SystemService._serialize(created)

    @staticmethod
    async def get_all() -> list[SystemType]:
        systems = await SystemRepository.get_all()
        return [SystemService._serialize(system) for system in systems]

    @staticmethod
    async def get_by_code(code: str) -> SystemType | None:
        system = await SystemRepository.get_by_code(code.strip().lower())
        return SystemService._serialize(system) if system else None

    @staticmethod
    async def get_teams(system_id: int) -> list[TeamType]:
        from app.core.service.core_team import TeamService

        teams = await SystemRepository.get_teams(system_id)
        return [TeamService._serialize(team) for team in teams]

    @staticmethod
    async def update(system_id: int, payload: SystemInput) -> SystemType:
        data = SystemService._normalize(payload)
        existing = await SystemRepository.get_by_code(data["code"])
        if existing and existing.id != system_id:
            raise HTTPException(status_code=400, detail="system code already exists")

        updated = await SystemRepository.update(system_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="system not found")
        return SystemService._serialize(updated)

    @staticmethod
    async def delete(system_id: int) -> bool:
        deleted = await SystemRepository.delete(system_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="system not found")
        return True
