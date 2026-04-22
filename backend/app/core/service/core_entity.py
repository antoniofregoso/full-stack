from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import ActionType, EntityInput, EntityType, FeatureType
from app.core.models.core_entity import CoreEntity
from app.core.repository.core_entity import EntityRepository
from app.core.repository.core_module import ModuleRepository
from app.core.service.core_system import SystemService


class EntityService:
    @staticmethod
    def _serialize(entity: CoreEntity) -> EntityType:
        return EntityType(
            id=entity.id,
            module_id=entity.module_id,
            code=entity.code,
            name=entity.name,
            icon=entity.icon,
            description=entity.description,
            active=entity.active,
            sequence=entity.sequence,
            feature_ids=[feature.id for feature in entity.features],
            action_ids=[action.id for action in entity.actions],
        )

    @staticmethod
    def _normalize(payload: EntityInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().lower()
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        data["icon"] = SystemService._normalize_icon(data.get("icon"))
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if not data["code"] or data["name"] is None:
            raise HTTPException(status_code=400, detail="module_id, code and name are required")
        return data

    @staticmethod
    async def create(payload: EntityInput) -> EntityType:
        data = EntityService._normalize(payload)
        module = await ModuleRepository.get_by_id(data["module_id"])
        if module is None:
            raise HTTPException(status_code=400, detail="module does not exist")

        existing = await EntityRepository.get_by_code(data["module_id"], data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="entity code already exists for this module")

        created = await EntityRepository.create(CoreEntity(**data))
        return EntityService._serialize(created)

    @staticmethod
    async def get_all() -> list[EntityType]:
        entities = await EntityRepository.get_all()
        return [EntityService._serialize(entity) for entity in entities]

    @staticmethod
    async def get_by_id(entity_id: int) -> EntityType | None:
        entity = await EntityRepository.get_by_id(entity_id)
        return EntityService._serialize(entity) if entity else None

    @staticmethod
    async def get_by_module(module_id: int) -> list[EntityType]:
        entities = await EntityRepository.get_by_module(module_id)
        return [EntityService._serialize(entity) for entity in entities]

    @staticmethod
    async def get_features(entity_id: int) -> list[FeatureType]:
        from app.core.service.core_feature import FeatureService

        entity = await EntityRepository.get_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="entity not found")
        return [FeatureService._serialize(feature) for feature in entity.features]

    @staticmethod
    async def get_actions(entity_id: int) -> list[ActionType]:
        from app.core.service.core_action import ActionService

        entity = await EntityRepository.get_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="entity not found")
        return [ActionService._serialize(action) for action in entity.actions]

    @staticmethod
    async def update(entity_id: int, payload: EntityInput) -> EntityType:
        data = EntityService._normalize(payload)
        module = await ModuleRepository.get_by_id(data["module_id"])
        if module is None:
            raise HTTPException(status_code=400, detail="module does not exist")

        existing = await EntityRepository.get_by_code(data["module_id"], data["code"])
        if existing and existing.id != entity_id:
            raise HTTPException(status_code=400, detail="entity code already exists for this module")

        updated = await EntityRepository.update(entity_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="entity not found")
        return EntityService._serialize(updated)

    @staticmethod
    async def delete(entity_id: int) -> bool:
        deleted = await EntityRepository.delete(entity_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="entity not found")
        return True
