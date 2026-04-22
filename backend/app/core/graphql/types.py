import datetime
from enum import Enum
from typing import Optional

import strawberry
from strawberry.scalars import JSON

from app.infrastructure.model_defaults import default_icon
from app.infrastructure.selections import OperationalStatus


@strawberry.enum
class CurrencyPositionEnum(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


@strawberry.enum
class OperationalStatusEnum(str, Enum):
    AHEAD = OperationalStatus.AHEAD.value
    ON_TRACK = OperationalStatus.ON_TRACK.value
    AT_RISK = OperationalStatus.AT_RISK.value
    CRITICAL = OperationalStatus.CRITICAL.value


@strawberry.type
class SystemType:
    id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    status: OperationalStatusEnum
    sequence: int
    team_ids: list[int]


@strawberry.input
class SystemInput:
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=default_icon)
    description: Optional[JSON] = None
    active: bool = True
    status: OperationalStatusEnum = OperationalStatusEnum.ON_TRACK
    sequence: int = 10


@strawberry.type
class TeamType:
    id: int
    system_id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    status: OperationalStatusEnum
    sequence: int
    module_ids: list[int]


@strawberry.input
class TeamInput:
    system_id: int
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=default_icon)
    description: Optional[JSON] = None
    active: bool = True
    status: OperationalStatusEnum = OperationalStatusEnum.ON_TRACK
    sequence: int = 10


@strawberry.type
class ModuleType:
    id: int
    team_id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    status: OperationalStatusEnum
    sequence: int
    entity_ids: list[int]


@strawberry.input
class ModuleInput:
    team_id: int
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=default_icon)
    description: Optional[JSON] = None
    active: bool = True
    status: OperationalStatusEnum = OperationalStatusEnum.ON_TRACK
    sequence: int = 10


@strawberry.type
class EntityType:
    id: int
    module_id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    sequence: int
    feature_ids: list[int]
    action_ids: list[int]


@strawberry.input
class EntityInput:
    module_id: int
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=default_icon)
    description: Optional[JSON] = None
    active: bool = True
    sequence: int = 10


@strawberry.type
class FeatureType:
    id: int
    entity_id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    sequence: int


@strawberry.input
class FeatureInput:
    entity_id: int
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=dict)
    description: Optional[JSON] = None
    active: bool = True
    sequence: int = 10


@strawberry.type
class ActionType:
    id: int
    entity_id: int
    code: str
    name: JSON
    icon: JSON
    description: Optional[JSON]
    active: bool
    sequence: int


@strawberry.input
class ActionInput:
    entity_id: int
    code: str
    name: JSON
    icon: JSON = strawberry.field(default_factory=default_icon)
    description: Optional[JSON] = None
    active: bool = True
    sequence: int = 10


@strawberry.type
class UserAssignmentType:
    id: int
    user_id: int
    system_id: Optional[int]
    team_id: Optional[int]
    module_id: Optional[int]
    entity_id: Optional[int]
    assignment_role: Optional[str]
    is_manager: bool
    active: bool
    landing_path: Optional[str]


@strawberry.input
class UserAssignmentInput:
    user_id: int
    system_id: Optional[int] = None
    team_id: Optional[int] = None
    module_id: Optional[int] = None
    entity_id: Optional[int] = None
    assignment_role: Optional[str] = None
    is_manager: bool = False
    active: bool = True


@strawberry.type
class CountryStateType:
    id: int
    code: str
    name: JSON
    country_id: int


@strawberry.input
class CountryStateInput:
    code: str
    name: JSON


@strawberry.type
class CountryType:
    id: int
    code: str
    name: JSON
    phone_code: Optional[str]
    currency_id: Optional[int]
    states: list[CountryStateType]
    timezone_ids: list[int]


@strawberry.input
class CountryInput:
    code: str
    name: JSON
    phone_code: Optional[str] = None
    currency_id: Optional[int] = None
    states: list[CountryStateInput] = strawberry.field(default_factory=list)
    timezone_ids: list[int] = strawberry.field(default_factory=list)


@strawberry.type
class TimezoneType:
    id: int
    name: str
    code: str
    offset: Optional[int]
    country_ids: list[int]


@strawberry.input
class TimezoneInput:
    name: str
    code: str
    offset: Optional[int] = 0
    country_ids: list[int] = strawberry.field(default_factory=list)


@strawberry.type
class CurrencyType:
    id: int
    code: str
    name: str
    iso_numeric: int
    symbol: str
    currency_unit_label: Optional[JSON]
    currency_subunit_label: Optional[JSON]
    rounding: float
    position: CurrencyPositionEnum
    active: bool


@strawberry.input
class CurrencyInput:
    code: str
    name: str
    iso_numeric: int = 0
    symbol: str = ""
    currency_unit_label: Optional[JSON] = None
    currency_subunit_label: Optional[JSON] = None
    rounding: float = 0.01
    position: CurrencyPositionEnum = CurrencyPositionEnum.BEFORE
    active: bool = False


@strawberry.type
class LangType:
    id: int
    name: str
    code: str
    iso_code: str
    url_code: str
    date_format: Optional[str]
    time_format: Optional[str]
    week_start: Optional[int]
    flag: Optional[str]
    active: bool


@strawberry.input
class LangInput:
    name: str
    code: str
    iso_code: str
    url_code: str
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    week_start: Optional[int] = None
    flag: Optional[str] = None
    active: bool = False


@strawberry.type
class CompanyType:
    id: int
    name: str
    active: bool
    sequence: Optional[int]
    currency_id: Optional[int]
    color: Optional[str]
    street: Optional[str]
    street2: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    vat: Optional[str]
    lang_id: Optional[int]
    systems_ids: list[int]


@strawberry.input
class CompanyInput:
    name: str
    active: bool = False
    sequence: Optional[int] = 10
    currency_id: Optional[int] = None
    color: Optional[str] = None
    street: Optional[str] = None
    street2: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[int] = None
    country_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    vat: Optional[str] = None
    lang_id: Optional[int] = None
    systems_ids: list[int] = strawberry.field(default_factory=list)


@strawberry.type
class CompanySystemLinkType:
    company_id: int
    system_id: int
    description: Optional[JSON]


@strawberry.input
class CompanySystemLinkInput:
    company_id: int
    system_id: int
    description: Optional[JSON] = None


@strawberry.type
class PartyType:
    id: int
    name: str
    active: bool
    sequence: Optional[int]
    color: Optional[str]
    parent_id: Optional[int]
    lang_id: Optional[int]
    street: Optional[str]
    street2: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]
    tz_id: Optional[int]
    tz_offset: Optional[int]
    phone: Optional[str]
    email: Optional[str]
    function: Optional[str]
    website: Optional[str]
    vat: Optional[str]
    avatar_url: Optional[str]
    is_company: bool
    company_id: Optional[int]
    created_at: datetime.datetime
    create_by: Optional[int]
    updated_at: Optional[datetime.datetime]
    updated_by: Optional[int]


@strawberry.input
class PartyInput:
    name: str
    active: bool = True
    sequence: Optional[int] = 10
    color: Optional[str] = None
    parent_id: Optional[int] = None
    lang_id: Optional[int] = None
    street: Optional[str] = None
    street2: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[int] = None
    country_id: Optional[int] = None
    tz_id: Optional[int] = None
    tz_offset: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    function: Optional[str] = None
    website: Optional[str] = None
    vat: Optional[str] = None
    avatar_url: Optional[str] = None
    is_company: bool = False
    company_id: Optional[int] = None


@strawberry.type
class AppType:
    id: int
    name: JSON
    description: Optional[JSON]
    keys: Optional[JSON]
    active: bool
    public: bool
    schema_org: Optional[JSON]
    created_at: datetime.datetime
    create_by: Optional[int]
    updated_at: Optional[datetime.datetime]
    updated_by: Optional[int]


@strawberry.input
class AppInput:
    name: JSON
    description: Optional[JSON] = None
    keys: Optional[JSON] = None
    active: bool = True
    public: bool = True
    schema_org: Optional[JSON] = None


@strawberry.type
class AppSettingsType:
    id: int
    app_id: int
    key: str
    value: Optional[JSON]
    created_at: datetime.datetime
    create_by: Optional[int]
    updated_at: Optional[datetime.datetime]
    updated_by: Optional[int]


@strawberry.input
class AppSettingsInput:
    app_id: int
    key: str
    value: Optional[JSON] = None


@strawberry.type
class PageType:
    id: int
    name: JSON
    description: Optional[JSON]
    keys: Optional[JSON]
    view: Optional[JSON]
    active: bool
    sequence: int
    color: Optional[str]
    public: bool
    created_at: datetime.datetime
    create_by: Optional[int]
    updated_at: Optional[datetime.datetime]
    updated_by: Optional[int]


@strawberry.input
class PageInput:
    name: JSON
    description: Optional[JSON] = None
    keys: Optional[JSON] = None
    view: Optional[JSON] = None
    active: bool = True
    sequence: int = 10
    color: Optional[str] = None
    public: bool = False
