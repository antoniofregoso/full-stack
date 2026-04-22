from dataclasses import asdict
from enum import Enum
from collections import defaultdict
from typing import Any

from fastapi import HTTPException

from app.auth.repository.auth_user import AuthUserRepository
from app.core.models.core_entity import CoreEntity
from app.core.models.core_module import CoreModule
from app.core.models.core_team import CoreTeam
from app.core.repository.core_action import ActionRepository
from app.core.repository.core_entity import EntityRepository
from app.core.repository.core_feature import FeatureRepository
from app.core.repository.core_module import ModuleRepository
from app.core.repository.core_system import SystemRepository
from app.core.repository.core_team import TeamRepository
from app.talent.graphql.types import (
    TalentHierarchyNodeType,
    TalentNodeAssignmentInput,
    TalentNodeAssignmentType,
    TalentNodeTypeEnum,
)
from app.talent.models.talent_node_assignment import TalentNodeAssignment, TalentNodeType
from app.talent.repository.talent_node_assignment import TalentNodeAssignmentRepository


class TalentNodeAssignmentService:
    @staticmethod
    def _normalize_json_title(value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail="job_title must be an object like {'es_MX': 'Gerente'}",
            )

        normalized: dict[str, str] = {}
        for key, translation in value.items():
            locale = str(key).strip()
            text = str(translation).strip() if translation is not None else ""
            if locale and text:
                normalized[locale] = text
        return normalized

    @staticmethod
    def _normalize_json_description(value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail="description must be an object like {'es_MX': 'Responsable de resultados'}",
            )

        normalized: dict[str, str] = {}
        for key, translation in value.items():
            locale = str(key).strip()
            text = str(translation).strip() if translation is not None else ""
            if locale and text:
                normalized[locale] = text
        return normalized

    @staticmethod
    def _serialize(assignment: TalentNodeAssignment) -> TalentNodeAssignmentType:
        return TalentNodeAssignmentType(
            id=assignment.id,
            user_id=assignment.user_id,
            node_type=TalentNodeTypeEnum(assignment.node_type.value),
            node_id=assignment.node_id,
            job_title=assignment.job_title,
            description=assignment.description,
            is_ai_agent=assignment.is_ai_agent,
            is_primary=assignment.is_primary,
            active=assignment.active,
        )

    @staticmethod
    def _normalize(payload: TalentNodeAssignmentInput) -> dict:
        data = asdict(payload)
        raw_node_type = data["node_type"]
        if isinstance(raw_node_type, Enum):
            raw_node_type = raw_node_type.value
        data["node_type"] = TalentNodeType(str(raw_node_type))
        if data["user_id"] <= 0 or data["node_id"] <= 0:
            raise HTTPException(status_code=400, detail="user_id and node_id must be positive integers")
        data["job_title"] = TalentNodeAssignmentService._normalize_json_title(
            data.get("job_title")
        )
        data["description"] = TalentNodeAssignmentService._normalize_json_description(
            data.get("description")
        )
        data["is_ai_agent"] = bool(data.get("is_ai_agent"))
        return data

    @staticmethod
    async def _validate_references(data: dict) -> None:
        user = await AuthUserRepository.get_by_id(data["user_id"], include_system=True)
        if user is None:
            raise HTTPException(status_code=400, detail="user does not exist")

        node_type = data["node_type"]
        node_id = data["node_id"]

        if node_type == TalentNodeType.SYSTEM:
            node = await SystemRepository.get_by_id(node_id)
        elif node_type == TalentNodeType.TEAM:
            node = await TeamRepository.get_by_id(node_id)
        elif node_type == TalentNodeType.MODULE:
            node = await ModuleRepository.get_by_id(node_id)
        elif node_type == TalentNodeType.ENTITY:
            node = await EntityRepository.get_by_id(node_id)
        elif node_type == TalentNodeType.FEATURE:
            node = await FeatureRepository.get_by_id(node_id)
        else:
            node = await ActionRepository.get_by_id(node_id)

        if node is None:
            raise HTTPException(status_code=400, detail=f"{node_type.value.lower()} node does not exist")

    @staticmethod
    async def create(payload: TalentNodeAssignmentInput) -> TalentNodeAssignmentType:
        data = TalentNodeAssignmentService._normalize(payload)
        await TalentNodeAssignmentService._validate_references(data)

        existing = await TalentNodeAssignmentRepository.find_existing(
            user_id=data["user_id"],
            node_type=data["node_type"],
            node_id=data["node_id"],
        )
        if existing is not None:
            raise HTTPException(status_code=400, detail="talent assignment already exists")

        created = await TalentNodeAssignmentRepository.create(TalentNodeAssignment(**data))
        if created.is_primary:
            await TalentNodeAssignmentRepository.clear_primary_for_node(
                node_type=created.node_type,
                node_id=created.node_id,
                exclude_id=created.id,
            )
        return TalentNodeAssignmentService._serialize(created)

    @staticmethod
    async def get_all() -> list[TalentNodeAssignmentType]:
        assignments = await TalentNodeAssignmentRepository.get_all()
        return [TalentNodeAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def get_by_user(user_id: int) -> list[TalentNodeAssignmentType]:
        assignments = await TalentNodeAssignmentRepository.get_by_user(user_id)
        return [TalentNodeAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def get_by_node(node_type: TalentNodeType, node_id: int) -> list[TalentNodeAssignmentType]:
        assignments = await TalentNodeAssignmentRepository.get_by_node(node_type, node_id)
        return [TalentNodeAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def update(
        assignment_id: int, payload: TalentNodeAssignmentInput
    ) -> TalentNodeAssignmentType:
        data = TalentNodeAssignmentService._normalize(payload)
        await TalentNodeAssignmentService._validate_references(data)

        existing = await TalentNodeAssignmentRepository.find_existing(
            user_id=data["user_id"],
            node_type=data["node_type"],
            node_id=data["node_id"],
        )
        if existing is not None and existing.id != assignment_id:
            raise HTTPException(status_code=400, detail="talent assignment already exists")

        updated = await TalentNodeAssignmentRepository.update(assignment_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="talent assignment not found")
        if updated.is_primary:
            await TalentNodeAssignmentRepository.clear_primary_for_node(
                node_type=updated.node_type,
                node_id=updated.node_id,
                exclude_id=updated.id,
            )
        return TalentNodeAssignmentService._serialize(updated)

    @staticmethod
    async def delete(assignment_id: int) -> bool:
        deleted = await TalentNodeAssignmentRepository.delete(assignment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="talent assignment not found")
        return True

    @staticmethod
    def _build_hierarchy_node(
        *,
        node_type: TalentNodeType,
        node_id: int,
        code: str,
        name: dict[str, str],
        description: dict[str, str] | None,
        active: bool,
        assignments_by_node: dict[tuple[TalentNodeType, int], list[TalentNodeAssignment]],
        children: list[TalentHierarchyNodeType],
    ) -> TalentHierarchyNodeType:
        assignments = assignments_by_node.get((node_type, node_id), [])
        return TalentHierarchyNodeType(
            node_type=TalentNodeTypeEnum(node_type.value),
            node_id=node_id,
            code=code,
            name=name or {},
            description=description,
            active=active,
            assignments=[TalentNodeAssignmentService._serialize(item) for item in assignments],
            children=children,
        )

    @staticmethod
    async def get_hierarchy(include_inactive: bool = False) -> list[TalentHierarchyNodeType]:
        systems = await SystemRepository.get_all()
        teams = await TeamRepository.get_all()
        modules = await ModuleRepository.get_all()
        entities = await EntityRepository.get_all()
        assignments = await TalentNodeAssignmentRepository.get_all()

        if not include_inactive:
            systems = [item for item in systems if item.active]
            teams = [item for item in teams if item.active]
            modules = [item for item in modules if item.active]
            entities = [item for item in entities if item.active]
            assignments = [item for item in assignments if item.active]

        assignments_by_node: dict[tuple[TalentNodeType, int], list[TalentNodeAssignment]] = defaultdict(list)
        for assignment in assignments:
            assignments_by_node[(assignment.node_type, assignment.node_id)].append(assignment)

        teams_by_system: dict[int, list[CoreTeam]] = defaultdict(list)
        for team in teams:
            teams_by_system[team.system_id].append(team)

        modules_by_team: dict[int, list[CoreModule]] = defaultdict(list)
        for module in modules:
            modules_by_team[module.team_id].append(module)

        entities_by_module: dict[int, list[CoreEntity]] = defaultdict(list)
        for entity in entities:
            entities_by_module[entity.module_id].append(entity)

        hierarchy: list[TalentHierarchyNodeType] = []
        for system in systems:
            team_nodes: list[TalentHierarchyNodeType] = []
            for team in teams_by_system.get(system.id, []):
                module_nodes: list[TalentHierarchyNodeType] = []
                for module in modules_by_team.get(team.id, []):
                    entity_nodes = [
                        TalentNodeAssignmentService._build_hierarchy_node(
                            node_type=TalentNodeType.ENTITY,
                            node_id=entity.id,
                            code=entity.code,
                            name=entity.name,
                            description=entity.description,
                            active=entity.active,
                            assignments_by_node=assignments_by_node,
                            children=[],
                        )
                        for entity in entities_by_module.get(module.id, [])
                    ]
                    module_nodes.append(
                        TalentNodeAssignmentService._build_hierarchy_node(
                            node_type=TalentNodeType.MODULE,
                            node_id=module.id,
                            code=module.code,
                            name=module.name,
                            description=module.description,
                            active=module.active,
                            assignments_by_node=assignments_by_node,
                            children=entity_nodes,
                        )
                    )

                team_nodes.append(
                    TalentNodeAssignmentService._build_hierarchy_node(
                        node_type=TalentNodeType.TEAM,
                        node_id=team.id,
                        code=team.code,
                        name=team.name,
                        description=team.description,
                        active=team.active,
                        assignments_by_node=assignments_by_node,
                        children=module_nodes,
                    )
                )

            hierarchy.append(
                TalentNodeAssignmentService._build_hierarchy_node(
                    node_type=TalentNodeType.SYSTEM,
                    node_id=system.id,
                    code=system.code,
                    name=system.name,
                    description=system.description,
                    active=system.active,
                    assignments_by_node=assignments_by_node,
                    children=team_nodes,
                )
            )

        return hierarchy
