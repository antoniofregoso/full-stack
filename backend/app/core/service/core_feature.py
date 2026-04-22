from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import FeatureInput, FeatureType
from app.core.models.core_feature import CoreFeature
from app.core.repository.core_entity import EntityRepository
from app.core.repository.core_feature import FeatureRepository
from app.core.service.core_system import SystemService


class FeatureService:
    @staticmethod
    def _serialize(feature: CoreFeature) -> FeatureType:
        return FeatureType(
            id=feature.id,
            entity_id=feature.entity_id,
            code=feature.code,
            name=feature.name,
            icon=feature.icon,
            description=feature.description,
            active=feature.active,
            sequence=feature.sequence,
        )

    @staticmethod
    def _normalize(payload: FeatureInput) -> dict:
        data = asdict(payload)
        data["code"] = data["code"].strip().lower()
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        data["icon"] = SystemService._normalize_json_object(data.get("icon"), "icon")
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if not data["code"] or data["name"] is None:
            raise HTTPException(status_code=400, detail="entity_id, code and name are required")
        return data

    @staticmethod
    async def create(payload: FeatureInput) -> FeatureType:
        data = FeatureService._normalize(payload)
        entity = await EntityRepository.get_by_id(data["entity_id"])
        if entity is None:
            raise HTTPException(status_code=400, detail="entity does not exist")

        existing = await FeatureRepository.get_by_code(data["entity_id"], data["code"])
        if existing:
            raise HTTPException(status_code=400, detail="feature code already exists for this entity")

        created = await FeatureRepository.create(CoreFeature(**data))
        return FeatureService._serialize(created)

    @staticmethod
    async def get_all() -> list[FeatureType]:
        features = await FeatureRepository.get_all()
        return [FeatureService._serialize(feature) for feature in features]

    @staticmethod
    async def get_by_id(feature_id: int) -> FeatureType | None:
        feature = await FeatureRepository.get_by_id(feature_id)
        return FeatureService._serialize(feature) if feature else None

    @staticmethod
    async def update(feature_id: int, payload: FeatureInput) -> FeatureType:
        data = FeatureService._normalize(payload)
        entity = await EntityRepository.get_by_id(data["entity_id"])
        if entity is None:
            raise HTTPException(status_code=400, detail="entity does not exist")

        existing = await FeatureRepository.get_by_code(data["entity_id"], data["code"])
        if existing and existing.id != feature_id:
            raise HTTPException(status_code=400, detail="feature code already exists for this entity")

        updated = await FeatureRepository.update(feature_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="feature not found")
        return FeatureService._serialize(updated)

    @staticmethod
    async def delete(feature_id: int) -> bool:
        deleted = await FeatureRepository.delete(feature_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="feature not found")
        return True
