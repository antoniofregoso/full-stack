from enum import Enum
from typing import Optional

import strawberry
from strawberry.scalars import JSON

from app.talent.models.talent_node_assignment import TalentNodeType


@strawberry.enum
class TalentNodeTypeEnum(str, Enum):
    SYSTEM = TalentNodeType.SYSTEM.value
    TEAM = TalentNodeType.TEAM.value
    MODULE = TalentNodeType.MODULE.value
    ENTITY = TalentNodeType.ENTITY.value
    FEATURE = TalentNodeType.FEATURE.value
    ACTION = TalentNodeType.ACTION.value


@strawberry.type
class TalentNodeAssignmentType:
    id: int
    user_id: int
    node_type: TalentNodeTypeEnum
    node_id: int
    job_title: JSON
    description: JSON
    is_ai_agent: bool
    is_primary: bool
    active: bool


@strawberry.input
class TalentNodeAssignmentInput:
    user_id: int
    node_type: TalentNodeTypeEnum
    node_id: int
    job_title: JSON = strawberry.field(default_factory=dict)
    description: JSON = strawberry.field(default_factory=dict)
    is_ai_agent: bool = False
    is_primary: bool = False
    active: bool = True


@strawberry.type
class TalentHierarchyNodeType:
    node_type: TalentNodeTypeEnum
    node_id: int
    code: str
    name: JSON
    description: Optional[JSON]
    active: bool
    assignments: list[TalentNodeAssignmentType]
    children: list["TalentHierarchyNodeType"]
