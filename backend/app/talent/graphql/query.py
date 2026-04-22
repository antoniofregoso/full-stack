import strawberry

from app.infrastructure.JWTBearer import HasModuleAccess
from app.talent.graphql.types import (
    TalentHierarchyNodeType,
    TalentNodeAssignmentType,
    TalentNodeTypeEnum,
)
from app.talent.models.talent_node_assignment import TalentNodeType
from app.talent.service.talent_node_assignment import TalentNodeAssignmentService

TalentReadAccess = HasModuleAccess("talent", "read")


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[TalentReadAccess])
    async def get_all_talent_node_assignments(self) -> list[TalentNodeAssignmentType]:
        return await TalentNodeAssignmentService.get_all()

    @strawberry.field(permission_classes=[TalentReadAccess])
    async def get_talent_node_assignments_by_user(self, user_id: int) -> list[TalentNodeAssignmentType]:
        return await TalentNodeAssignmentService.get_by_user(user_id)

    @strawberry.field(permission_classes=[TalentReadAccess])
    async def get_talent_node_assignments_by_node(
        self, node_type: TalentNodeTypeEnum, node_id: int
    ) -> list[TalentNodeAssignmentType]:
        return await TalentNodeAssignmentService.get_by_node(TalentNodeType(node_type.value), node_id)

    @strawberry.field(permission_classes=[TalentReadAccess])
    async def get_talent_hierarchy(self, include_inactive: bool = False) -> list[TalentHierarchyNodeType]:
        return await TalentNodeAssignmentService.get_hierarchy(include_inactive=include_inactive)
