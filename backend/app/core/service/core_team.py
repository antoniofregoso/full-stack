from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import ModuleType, TeamInput, TeamType
from app.core.models.core_team import CoreTeam
from app.core.repository.core_system import SystemRepository
from app.core.repository.core_team import TeamRepository
from app.core.service.core_system import SystemService


class TeamService:
    @staticmethod
    def _serialize(team: CoreTeam) -> TeamType:
        return TeamType(
            id=team.id,
            system_id=team.system_id,
            code=team.code,
            name=team.name,
            icon=team.icon,
            description=team.description,
            active=team.active,
            status=team.status,
            sequence=team.sequence,
            module_ids=[module.id for module in team.modules],
        )

    @staticmethod
    def _normalize(payload: TeamInput) -> dict:
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
            raise HTTPException(status_code=400, detail="system_id, code and name are required")
        return data

    @staticmethod
    async def create(payload: TeamInput) -> TeamType:
        data = TeamService._normalize(payload)
        system = await SystemRepository.get_by_id(data["system_id"])
        if system is None:
            raise HTTPException(status_code=400, detail="system does not exist")

        existing = await TeamRepository.get_by_code(data["system_id"], data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="team code already exists for this system")

        created = await TeamRepository.create(CoreTeam(**data))
        return TeamService._serialize(created)

    @staticmethod
    async def get_all() -> list[TeamType]:
        teams = await TeamRepository.get_all()
        return [TeamService._serialize(team) for team in teams]

    @staticmethod
    async def get_by_id(team_id: int) -> TeamType | None:
        team = await TeamRepository.get_by_id(team_id)
        return TeamService._serialize(team) if team else None

    @staticmethod
    async def get_modules(team_id: int) -> list[ModuleType]:
        from app.core.service.core_module import ModuleService

        modules = await TeamRepository.get_modules(team_id)
        return [ModuleService._serialize(module) for module in modules]

    @staticmethod
    async def update(team_id: int, payload: TeamInput) -> TeamType:
        data = TeamService._normalize(payload)
        system = await SystemRepository.get_by_id(data["system_id"])
        if system is None:
            raise HTTPException(status_code=400, detail="system does not exist")

        existing = await TeamRepository.get_by_code(data["system_id"], data["code"])
        if existing and existing.id != team_id:
            raise HTTPException(status_code=400, detail="team code already exists for this system")

        updated = await TeamRepository.update(team_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="team not found")
        return TeamService._serialize(updated)

    @staticmethod
    async def delete(team_id: int) -> bool:
        deleted = await TeamRepository.delete(team_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="team not found")
        return True
