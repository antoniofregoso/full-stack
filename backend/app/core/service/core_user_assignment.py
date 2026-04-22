from dataclasses import asdict

from fastapi import HTTPException

from app.auth.repository.auth_user import AuthUserRepository
from app.core.graphql.types import UserAssignmentInput, UserAssignmentType
from app.core.models.core_user_assignment import CoreUserAssignment
from app.core.repository.core_entity import EntityRepository
from app.core.repository.core_module import ModuleRepository
from app.core.repository.core_system import SystemRepository
from app.core.repository.core_team import TeamRepository
from app.core.repository.core_user_assignment import UserAssignmentRepository


class UserAssignmentService:
    @staticmethod
    async def get_my_landing_path(user_id: int) -> str | None:
        assignments = await UserAssignmentRepository.get_by_user(user_id)
        prioritized = sorted(
            assignments,
            key=lambda item: (
                0 if item.entity_id is not None else
                1 if item.module_id is not None else
                2 if item.team_id is not None else
                3
            ),
        )
        if not prioritized:
            return None
        return await UserAssignmentService._resolve_landing_path(prioritized[0])

    @staticmethod
    async def _resolve_landing_path(assignment: CoreUserAssignment) -> str | None:
        if assignment.entity_id is not None:
            entity = await EntityRepository.get_by_id(assignment.entity_id)
            if entity is None:
                return None
            module = await ModuleRepository.get_by_id(entity.module_id)
            if module is None:
                return None
            team = await TeamRepository.get_by_id(module.team_id)
            if team is None:
                return None
            system = await SystemRepository.get_by_id(team.system_id)
            if system is None:
                return None
            return f"/system/{system.code}/team/{team.code}/module/{module.code}/entity/{entity.code}"

        if assignment.module_id is not None:
            module = await ModuleRepository.get_by_id(assignment.module_id)
            if module is None:
                return None
            entity = await EntityRepository.get_first_by_module(module.id)
            if entity is None:
                return None
            team = await TeamRepository.get_by_id(module.team_id)
            if team is None:
                return None
            system = await SystemRepository.get_by_id(team.system_id)
            if system is None:
                return None
            return f"/system/{system.code}/team/{team.code}/module/{module.code}/entity/{entity.code}"

        if assignment.team_id is not None:
            team = await TeamRepository.get_by_id(assignment.team_id)
            if team is None or not team.modules:
                return None
            module = sorted(team.modules, key=lambda item: (item.sequence, item.code))[0]
            entity = await EntityRepository.get_first_by_module(module.id)
            if entity is None:
                return None
            system = await SystemRepository.get_by_id(team.system_id)
            if system is None:
                return None
            return f"/system/{system.code}/team/{team.code}/module/{module.code}/entity/{entity.code}"

        if assignment.system_id is not None:
            system = await SystemRepository.get_by_id(assignment.system_id)
            if system is None or not system.teams:
                return None
            team = sorted(system.teams, key=lambda item: (item.sequence, item.code))[0]
            modules = await TeamRepository.get_modules(team.id)
            if not modules:
                return None
            module = modules[0]
            entity = await EntityRepository.get_first_by_module(module.id)
            if entity is None:
                return None
            return f"/system/{system.code}/team/{team.code}/module/{module.code}/entity/{entity.code}"

        return None

    @staticmethod
    async def _serialize(assignment: CoreUserAssignment) -> UserAssignmentType:
        return UserAssignmentType(
            id=assignment.id,
            user_id=assignment.user_id,
            system_id=assignment.system_id,
            team_id=assignment.team_id,
            module_id=assignment.module_id,
            entity_id=assignment.entity_id,
            assignment_role=assignment.assignment_role,
            is_manager=assignment.is_manager,
            active=assignment.active,
            landing_path=await UserAssignmentService._resolve_landing_path(assignment),
        )

    @staticmethod
    def _normalize(payload: UserAssignmentInput) -> dict:
        data = asdict(payload)
        if data.get("assignment_role") is not None:
            data["assignment_role"] = data["assignment_role"].strip() or None

        scope_fields = ["system_id", "team_id", "module_id", "entity_id"]
        selected_scope = [field for field in scope_fields if data.get(field) is not None]
        if len(selected_scope) != 1:
            raise HTTPException(
                status_code=400,
                detail="exactly one scope is required: system_id, team_id, module_id or entity_id",
            )
        return data

    @staticmethod
    async def _validate_references(data: dict) -> None:
        user = await AuthUserRepository.get_by_id(data["user_id"], include_system=True)
        if user is None:
            raise HTTPException(status_code=400, detail="user does not exist")

        if data.get("system_id") is not None:
            system = await SystemRepository.get_by_id(data["system_id"])
            if system is None:
                raise HTTPException(status_code=400, detail="system does not exist")

        if data.get("team_id") is not None:
            team = await TeamRepository.get_by_id(data["team_id"])
            if team is None:
                raise HTTPException(status_code=400, detail="team does not exist")

        if data.get("module_id") is not None:
            module = await ModuleRepository.get_by_id(data["module_id"])
            if module is None:
                raise HTTPException(status_code=400, detail="module does not exist")

        if data.get("entity_id") is not None:
            entity = await EntityRepository.get_by_id(data["entity_id"])
            if entity is None:
                raise HTTPException(status_code=400, detail="entity does not exist")

    @staticmethod
    async def create(payload: UserAssignmentInput) -> UserAssignmentType:
        data = UserAssignmentService._normalize(payload)
        await UserAssignmentService._validate_references(data)

        existing = await UserAssignmentRepository.find_existing(data)
        if existing:
            raise HTTPException(status_code=400, detail="user assignment already exists")

        created = await UserAssignmentRepository.create(CoreUserAssignment(**data))
        return await UserAssignmentService._serialize(created)

    @staticmethod
    async def get_all() -> list[UserAssignmentType]:
        assignments = await UserAssignmentRepository.get_all()
        return [await UserAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def get_by_user(user_id: int) -> list[UserAssignmentType]:
        assignments = await UserAssignmentRepository.get_by_user(user_id)
        return [await UserAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def get_by_scope(
        *,
        system_id: int | None = None,
        team_id: int | None = None,
        module_id: int | None = None,
        entity_id: int | None = None,
    ) -> list[UserAssignmentType]:
        assignments = await UserAssignmentRepository.get_by_scope(
            system_id=system_id,
            team_id=team_id,
            module_id=module_id,
            entity_id=entity_id,
        )
        return [await UserAssignmentService._serialize(assignment) for assignment in assignments]

    @staticmethod
    async def update(assignment_id: int, payload: UserAssignmentInput) -> UserAssignmentType:
        data = UserAssignmentService._normalize(payload)
        await UserAssignmentService._validate_references(data)

        existing = await UserAssignmentRepository.find_existing(data)
        if existing and existing.id != assignment_id:
            raise HTTPException(status_code=400, detail="user assignment already exists")

        updated = await UserAssignmentRepository.update(assignment_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="user assignment not found")
        return await UserAssignmentService._serialize(updated)

    @staticmethod
    async def delete(assignment_id: int) -> bool:
        deleted = await UserAssignmentRepository.delete(assignment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="user assignment not found")
        return True
