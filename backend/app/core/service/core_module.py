from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import EntityType, ModuleInput, ModuleType
from app.core.models.core_module import CoreModule
from app.core.repository.core_module import ModuleRepository
from app.core.repository.core_team import TeamRepository
from app.core.service.core_system import SystemService


class ModuleService:
    @staticmethod
    def _serialize(module: CoreModule) -> ModuleType:
        return ModuleType(
            id=module.id,
            team_id=module.team_id,
            code=module.code,
            name=module.name,
            icon=module.icon,
            description=module.description,
            active=module.active,
            status=module.status,
            sequence=module.sequence,
            entity_ids=[entity.id for entity in module.entities],
        )

    @staticmethod
    def _normalize(payload: ModuleInput) -> dict:
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
            raise HTTPException(status_code=400, detail="team_id, code and name are required")
        return data

    @staticmethod
    async def create(payload: ModuleInput) -> ModuleType:
        data = ModuleService._normalize(payload)
        team = await TeamRepository.get_by_id(data["team_id"])
        if team is None:
            raise HTTPException(status_code=400, detail="team does not exist")

        existing = await ModuleRepository.get_by_code(data["team_id"], data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="module code already exists for this team")

        created = await ModuleRepository.create(CoreModule(**data))
        return ModuleService._serialize(created)

    @staticmethod
    async def get_all() -> list[ModuleType]:
        modules = await ModuleRepository.get_all()
        return [ModuleService._serialize(module) for module in modules]

    @staticmethod
    async def get_by_id(module_id: int) -> ModuleType | None:
        module = await ModuleRepository.get_by_id(module_id)
        return ModuleService._serialize(module) if module else None

    @staticmethod
    async def get_entities(module_id: int) -> list[EntityType]:
        from app.core.service.core_entity import EntityService

        module = await ModuleRepository.get_by_id(module_id)
        if module is None:
            raise HTTPException(status_code=404, detail="module not found")
        return [EntityService._serialize(entity) for entity in module.entities]

    @staticmethod
    async def update(module_id: int, payload: ModuleInput) -> ModuleType:
        data = ModuleService._normalize(payload)
        team = await TeamRepository.get_by_id(data["team_id"])
        if team is None:
            raise HTTPException(status_code=400, detail="team does not exist")

        existing = await ModuleRepository.get_by_code(data["team_id"], data["code"])
        if existing and existing.id != module_id:
            raise HTTPException(status_code=400, detail="module code already exists for this team")

        updated = await ModuleRepository.update(module_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="module not found")
        return ModuleService._serialize(updated)

    @staticmethod
    async def delete(module_id: int) -> bool:
        deleted = await ModuleRepository.delete(module_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="module not found")
        return True
