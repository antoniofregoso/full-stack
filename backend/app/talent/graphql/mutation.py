import strawberry

from app.infrastructure.JWTBearer import HasModuleAccess
from app.talent.graphql.types import TalentNodeAssignmentInput, TalentNodeAssignmentType
from app.talent.service.talent_node_assignment import TalentNodeAssignmentService

TalentCreateAccess = HasModuleAccess("talent", "create")
TalentUpdateAccess = HasModuleAccess("talent", "update")
TalentDeleteAccess = HasModuleAccess("talent", "delete")


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[TalentCreateAccess])
    async def create_talent_node_assignment(
        self, payload: TalentNodeAssignmentInput
    ) -> TalentNodeAssignmentType:
        return await TalentNodeAssignmentService.create(payload)

    @strawberry.mutation(permission_classes=[TalentUpdateAccess])
    async def update_talent_node_assignment(
        self, assignment_id: int, payload: TalentNodeAssignmentInput
    ) -> TalentNodeAssignmentType:
        return await TalentNodeAssignmentService.update(assignment_id, payload)

    @strawberry.mutation(permission_classes=[TalentDeleteAccess])
    async def delete_talent_node_assignment(self, assignment_id: int) -> bool:
        return await TalentNodeAssignmentService.delete(assignment_id)
