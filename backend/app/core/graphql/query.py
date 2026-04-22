import strawberry
from strawberry.scalars import JSON

from app.core.graphql.types import (
    ActionType,
    AppSettingsType,
    AppType,
    CompanyType,
    CompanySystemLinkType,
    CountryType,
    CurrencyType,
    EntityType,
    FeatureType,
    LangType,
    ModuleType,
    PageType,
    PartyType,
    SystemType,
    TeamType,
    TimezoneType,
    UserAssignmentType,
)
from app.core.service.core_action import ActionService
from app.core.service.core_app import AppService
from app.core.service.core_app_settings import AppSettingsService
from app.core.service.core_company import CompanyService
from app.core.service.core_company_system_link import CompanySystemLinkService
from app.core.service.core_country import CountryService
from app.core.service.core_currency import CurrencyService
from app.core.service.core_entity import EntityService
from app.core.service.core_feature import FeatureService
from app.core.service.core_lang import LangService
from app.core.service.core_module import ModuleService
from app.core.service.core_page import PageService
from app.core.service.core_party import PartyService
from app.core.service.core_system import SystemService
from app.core.service.core_team import TeamService
from app.core.service.core_timezone import TimezoneService
from app.core.service.core_user_assignment import UserAssignmentService
from app.infrastructure.JWTBearer import HasScopedAccess, IsAuthenticated, get_current_user_id

SystemReadAccess = HasScopedAccess("core", "system", "read")
TeamReadAccess = HasScopedAccess("core", "team", "read")
ModuleReadAccess = HasScopedAccess("core", "module", "read")
EntityReadAccess = HasScopedAccess("core", "entity", "read")
FeatureReadAccess = HasScopedAccess("core", "feature", "read")
ActionReadAccess = HasScopedAccess("core", "action", "read")
UserAssignmentReadAccess = HasScopedAccess("core", "user_assignment", "read")
CountryReadAccess = HasScopedAccess("core", "country", "read")
CurrencyReadAccess = HasScopedAccess("core", "currency", "read")
LangReadAccess = HasScopedAccess("core", "lang", "read")
CompanyReadAccess = HasScopedAccess("core", "company", "read")
CompanySystemLinkReadAccess = HasScopedAccess("core", "company_system_link", "read")
PartyReadAccess = HasScopedAccess("core", "party", "read")
AppReadAccess = HasScopedAccess("core", "app", "read")
AppSettingReadAccess = HasScopedAccess("core", "app_setting", "read")
TimezoneReadAccess = HasScopedAccess("core", "timezone", "read")
PageReadAccess = HasScopedAccess("core", "page", "read")


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, world!"

    @strawberry.field(permission_classes=[SystemReadAccess])
    async def get_all_systems(self) -> list[SystemType]:
        return await SystemService.get_all()

    @strawberry.field(permission_classes=[SystemReadAccess])
    async def get_system_by_code(self, code: str) -> SystemType | None:
        return await SystemService.get_by_code(code)

    @strawberry.field(permission_classes=[SystemReadAccess])
    async def get_teams_by_system(self, system_id: int) -> list[TeamType]:
        return await SystemService.get_teams(system_id)

    @strawberry.field(permission_classes=[TeamReadAccess])
    async def get_all_teams(self) -> list[TeamType]:
        return await TeamService.get_all()

    @strawberry.field(permission_classes=[TeamReadAccess])
    async def get_team_by_id(self, team_id: int) -> TeamType | None:
        return await TeamService.get_by_id(team_id)

    @strawberry.field(permission_classes=[TeamReadAccess])
    async def get_modules_by_team(self, team_id: int) -> list[ModuleType]:
        return await TeamService.get_modules(team_id)

    @strawberry.field(permission_classes=[ModuleReadAccess])
    async def get_entities_by_module(self, module_id: int) -> list[EntityType]:
        return await ModuleService.get_entities(module_id)

    @strawberry.field(permission_classes=[ModuleReadAccess])
    async def get_all_modules(self) -> list[ModuleType]:
        return await ModuleService.get_all()

    @strawberry.field(permission_classes=[ModuleReadAccess])
    async def get_module_by_id(self, module_id: int) -> ModuleType | None:
        return await ModuleService.get_by_id(module_id)

    @strawberry.field(permission_classes=[EntityReadAccess])
    async def get_features_by_entity(self, entity_id: int) -> list[FeatureType]:
        return await EntityService.get_features(entity_id)

    @strawberry.field(permission_classes=[EntityReadAccess])
    async def get_actions_by_entity(self, entity_id: int) -> list[ActionType]:
        return await EntityService.get_actions(entity_id)

    @strawberry.field(permission_classes=[EntityReadAccess])
    async def get_all_entities(self) -> list[EntityType]:
        return await EntityService.get_all()

    @strawberry.field(permission_classes=[EntityReadAccess])
    async def get_entity_by_id(self, entity_id: int) -> EntityType | None:
        return await EntityService.get_by_id(entity_id)

    @strawberry.field(permission_classes=[FeatureReadAccess])
    async def get_all_features(self) -> list[FeatureType]:
        return await FeatureService.get_all()

    @strawberry.field(permission_classes=[FeatureReadAccess])
    async def get_feature_by_id(self, feature_id: int) -> FeatureType | None:
        return await FeatureService.get_by_id(feature_id)

    @strawberry.field(permission_classes=[ActionReadAccess])
    async def get_all_actions(self) -> list[ActionType]:
        return await ActionService.get_all()

    @strawberry.field(permission_classes=[ActionReadAccess])
    async def get_action_by_id(self, action_id: int) -> ActionType | None:
        return await ActionService.get_by_id(action_id)

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_all_user_assignments(self) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_all()

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_user_assignments_by_user(self, user_id: int) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_by_user(user_id)

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_user_assignments_by_system(self, system_id: int) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_by_scope(system_id=system_id)

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_user_assignments_by_team(self, team_id: int) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_by_scope(team_id=team_id)

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_user_assignments_by_module(self, module_id: int) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_by_scope(module_id=module_id)

    @strawberry.field(permission_classes=[UserAssignmentReadAccess])
    async def get_user_assignments_by_entity(self, entity_id: int) -> list[UserAssignmentType]:
        return await UserAssignmentService.get_by_scope(entity_id=entity_id)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_my_landing_path(self, info: strawberry.Info) -> str | None:
        user_id = await get_current_user_id(info)
        return await UserAssignmentService.get_my_landing_path(user_id)

    @strawberry.field(permission_classes=[CountryReadAccess])
    async def get_all_countries(self) -> list[CountryType]:
        return await CountryService.get_all()

    @strawberry.field(permission_classes=[CountryReadAccess])
    async def get_country_by_code(self, code: str) -> CountryType | None:
        return await CountryService.get_by_code(code)

    @strawberry.field(permission_classes=[CurrencyReadAccess])
    async def get_all_currencies(self) -> list[CurrencyType]:
        return await CurrencyService.get_all()

    @strawberry.field(permission_classes=[CurrencyReadAccess])
    async def get_currency_by_code(self, code: str) -> CurrencyType | None:
        return await CurrencyService.get_by_code(code)

    @strawberry.field(permission_classes=[LangReadAccess])
    async def get_all_langs(self) -> list[LangType]:
        return await LangService.get_all()

    @strawberry.field(permission_classes=[LangReadAccess])
    async def get_lang_by_code(self, code: str) -> LangType | None:
        return await LangService.get_by_code(code)

    @strawberry.field(permission_classes=[CompanyReadAccess])
    async def get_all_companies(self) -> list[CompanyType]:
        return await CompanyService.get_all()

    @strawberry.field(permission_classes=[CompanyReadAccess])
    async def get_company_by_id(self, company_id: int) -> CompanyType | None:
        return await CompanyService.get_by_id(company_id)

    @strawberry.field(permission_classes=[CompanySystemLinkReadAccess])
    async def get_all_company_system_links(self) -> list[CompanySystemLinkType]:
        return await CompanySystemLinkService.get_all()

    @strawberry.field(permission_classes=[CompanySystemLinkReadAccess])
    async def get_company_system_link(
        self, company_id: int, system_id: int
    ) -> CompanySystemLinkType | None:
        return await CompanySystemLinkService.get_by_ids(company_id, system_id)

    @strawberry.field(permission_classes=[CompanySystemLinkReadAccess])
    async def get_company_system_links_by_company(
        self, company_id: int
    ) -> list[CompanySystemLinkType]:
        return await CompanySystemLinkService.get_by_company(company_id)

    @strawberry.field(permission_classes=[CompanySystemLinkReadAccess])
    async def get_company_system_links_by_system(
        self, system_id: int
    ) -> list[CompanySystemLinkType]:
        return await CompanySystemLinkService.get_by_system(system_id)

    @strawberry.field(permission_classes=[PartyReadAccess])
    async def get_all_parties(self) -> list[PartyType]:
        return await PartyService.get_all()

    @strawberry.field(permission_classes=[PartyReadAccess])
    async def get_party_by_id(self, party_id: int) -> PartyType | None:
        return await PartyService.get_by_id(party_id)

    @strawberry.field(permission_classes=[AppReadAccess])
    async def get_all_apps(self) -> list[AppType]:
        return await AppService.get_all()

    @strawberry.field(permission_classes=[AppReadAccess])
    async def get_app_by_id(self, app_id: int) -> AppType | None:
        return await AppService.get_by_id(app_id)

    @strawberry.field(permission_classes=[AppReadAccess])
    async def get_apps_by_keys(self, keys: JSON) -> list[AppType]:
        return await AppService.get_by_keys(keys)

    @strawberry.field(permission_classes=[AppSettingReadAccess])
    async def get_all_app_settings(self) -> list[AppSettingsType]:
        return await AppSettingsService.get_all()

    @strawberry.field(permission_classes=[AppSettingReadAccess])
    async def get_app_setting_by_id(self, setting_id: int) -> AppSettingsType | None:
        return await AppSettingsService.get_by_id(setting_id)

    @strawberry.field(permission_classes=[AppSettingReadAccess])
    async def get_app_settings_by_app(self, app_id: int) -> list[AppSettingsType]:
        return await AppSettingsService.get_by_app(app_id)

    @strawberry.field(permission_classes=[AppSettingReadAccess])
    async def get_app_setting_by_key(
        self, app_id: int, key: str
    ) -> AppSettingsType | None:
        return await AppSettingsService.get_by_app_and_key(app_id, key)

    @strawberry.field(permission_classes=[TimezoneReadAccess])
    async def get_all_timezones(self) -> list[TimezoneType]:
        return await TimezoneService.get_all()

    @strawberry.field(permission_classes=[TimezoneReadAccess])
    async def get_timezones_by_country(self, country_id: int) -> list[TimezoneType]:
        return await TimezoneService.get_by_country(country_id)

    @strawberry.field(permission_classes=[TimezoneReadAccess])
    async def get_timezone_by_code(self, code: str) -> TimezoneType | None:
        return await TimezoneService.get_by_code(code)

    @strawberry.field(permission_classes=[PageReadAccess])
    async def get_all_pages(self) -> list[PageType]:
        return await PageService.get_all()

    @strawberry.field(permission_classes=[PageReadAccess])
    async def get_page_by_id(self, page_id: int) -> PageType | None:
        return await PageService.get_by_id(page_id)

    @strawberry.field(permission_classes=[PageReadAccess])
    async def get_page_by_name(self, name: JSON) -> PageType | None:
        return await PageService.get_by_name(name)

    @strawberry.field(permission_classes=[PageReadAccess])
    async def get_page_by_keys(self, keys: JSON) -> list[PageType]:
        return await PageService.get_by_keys(keys)

    @strawberry.field(permission_classes=[IsAuthenticated, PageReadAccess])
    async def get_dashboard(
        self,
        info: strawberry.Info,
        keys: JSON,
        lang_code: str | None = None,
    ) -> JSON:
        user_id = await get_current_user_id(info)
        return await PageService.get_dashboard(
            keys=keys,
            user_id=user_id,
            lang_code=lang_code,
        )
