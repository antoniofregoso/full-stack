from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import ActionInput, ActionType
from app.core.models.core_action import CoreAction
from app.core.repository.core_action import ActionRepository
from app.core.repository.core_entity import EntityRepository
from app.core.service.core_system import SystemService


class ActionService:
    @staticmethod
    def _serialize(action: CoreAction) -> ActionType:
        return ActionType(
            id=action.id,
            entity_id=action.entity_id,
            code=action.code,
            name=action.name,
            icon=action.icon,
            description=action.description,
            active=action.active,
            sequence=action.sequence,
        )

    @staticmethod
    def _normalize(payload: ActionInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().lower()
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        data["icon"] = SystemService._normalize_icon(data.get("icon"))
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if not data["code"] or data["name"] is None:
            raise HTTPException(status_code=400, detail="entity_id, code and name are required")
        return data

    @staticmethod
    async def create(payload: ActionInput) -> ActionType:
        data = ActionService._normalize(payload)
        entity = await EntityRepository.get_by_id(data["entity_id"])
        if entity is None:
            raise HTTPException(status_code=400, detail="entity does not exist")

        existing = await ActionRepository.get_by_code(data["entity_id"], data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="action code already exists for this entity")

        created = await ActionRepository.create(CoreAction(**data))
        return ActionService._serialize(created)

    @staticmethod
    async def get_all() -> list[ActionType]:
        actions = await ActionRepository.get_all()
        return [ActionService._serialize(action) for action in actions]

    @staticmethod
    async def get_by_id(action_id: int) -> ActionType | None:
        action = await ActionRepository.get_by_id(action_id)
        return ActionService._serialize(action) if action else None

    @staticmethod
    async def update(action_id: int, payload: ActionInput) -> ActionType:
        data = ActionService._normalize(payload)
        entity = await EntityRepository.get_by_id(data["entity_id"])
        if entity is None:
            raise HTTPException(status_code=400, detail="entity does not exist")

        existing = await ActionRepository.get_by_code(data["entity_id"], data["code"])
        if existing and existing.id != action_id:
            raise HTTPException(status_code=400, detail="action code already exists for this entity")

        updated = await ActionRepository.update(action_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="action not found")
        return ActionService._serialize(updated)

    @staticmethod
    async def delete(action_id: int) -> bool:
        deleted = await ActionRepository.delete(action_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="action not found")
        return True
