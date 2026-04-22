import strawberry

from app.core.graphql.types import (
    ActionInput,
    ActionType,
    AppInput,
    AppSettingsInput,
    AppSettingsType,
    AppType,
    CompanyInput,
    CompanySystemLinkInput,
    CompanySystemLinkType,
    CompanyType,
    CountryInput,
    CountryType,
    CurrencyInput,
    CurrencyType,
    EntityInput,
    EntityType,
    FeatureInput,
    FeatureType,
    LangInput,
    LangType,
    ModuleInput,
    ModuleType,
    PageInput,
    PageType,
    PartyInput,
    PartyType,
    SystemInput,
    SystemType,
    TeamInput,
    TeamType,
    TimezoneInput,
    TimezoneType,
    UserAssignmentInput,
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
from app.infrastructure.JWTBearer import HasScopedAccess

SystemCreateAccess = HasScopedAccess("core", "system", "create")
SystemUpdateAccess = HasScopedAccess("core", "system", "update")
SystemDeleteAccess = HasScopedAccess("core", "system", "delete")
TeamCreateAccess = HasScopedAccess("core", "team", "create")
TeamUpdateAccess = HasScopedAccess("core", "team", "update")
TeamDeleteAccess = HasScopedAccess("core", "team", "delete")
ModuleCreateAccess = HasScopedAccess("core", "module", "create")
ModuleUpdateAccess = HasScopedAccess("core", "module", "update")
ModuleDeleteAccess = HasScopedAccess("core", "module", "delete")
EntityCreateAccess = HasScopedAccess("core", "entity", "create")
EntityUpdateAccess = HasScopedAccess("core", "entity", "update")
EntityDeleteAccess = HasScopedAccess("core", "entity", "delete")
FeatureCreateAccess = HasScopedAccess("core", "feature", "create")
FeatureUpdateAccess = HasScopedAccess("core", "feature", "update")
FeatureDeleteAccess = HasScopedAccess("core", "feature", "delete")
ActionCreateAccess = HasScopedAccess("core", "action", "create")
ActionUpdateAccess = HasScopedAccess("core", "action", "update")
ActionDeleteAccess = HasScopedAccess("core", "action", "delete")
UserAssignmentCreateAccess = HasScopedAccess("core", "user_assignment", "create")
UserAssignmentUpdateAccess = HasScopedAccess("core", "user_assignment", "update")
UserAssignmentDeleteAccess = HasScopedAccess("core", "user_assignment", "delete")
CountryCreateAccess = HasScopedAccess("core", "country", "create")
CountryUpdateAccess = HasScopedAccess("core", "country", "update")
CountryDeleteAccess = HasScopedAccess("core", "country", "delete")
CurrencyCreateAccess = HasScopedAccess("core", "currency", "create")
CurrencyUpdateAccess = HasScopedAccess("core", "currency", "update")
CurrencyDeleteAccess = HasScopedAccess("core", "currency", "delete")
LangCreateAccess = HasScopedAccess("core", "lang", "create")
LangUpdateAccess = HasScopedAccess("core", "lang", "update")
LangDeleteAccess = HasScopedAccess("core", "lang", "delete")
CompanyCreateAccess = HasScopedAccess("core", "company", "create")
CompanyUpdateAccess = HasScopedAccess("core", "company", "update")
CompanyDeleteAccess = HasScopedAccess("core", "company", "delete")
CompanySystemLinkCreateAccess = HasScopedAccess("core", "company_system_link", "create")
CompanySystemLinkUpdateAccess = HasScopedAccess("core", "company_system_link", "update")
CompanySystemLinkDeleteAccess = HasScopedAccess("core", "company_system_link", "delete")
PartyCreateAccess = HasScopedAccess("core", "party", "create")
PartyUpdateAccess = HasScopedAccess("core", "party", "update")
PartyDeleteAccess = HasScopedAccess("core", "party", "delete")
AppCreateAccess = HasScopedAccess("core", "app", "create")
AppUpdateAccess = HasScopedAccess("core", "app", "update")
AppDeleteAccess = HasScopedAccess("core", "app", "delete")
AppSettingCreateAccess = HasScopedAccess("core", "app_setting", "create")
AppSettingUpdateAccess = HasScopedAccess("core", "app_setting", "update")
AppSettingDeleteAccess = HasScopedAccess("core", "app_setting", "delete")
TimezoneCreateAccess = HasScopedAccess("core", "timezone", "create")
TimezoneUpdateAccess = HasScopedAccess("core", "timezone", "update")
TimezoneDeleteAccess = HasScopedAccess("core", "timezone", "delete")
PageCreateAccess = HasScopedAccess("core", "page", "create")
PageUpdateAccess = HasScopedAccess("core", "page", "update")
PageDeleteAccess = HasScopedAccess("core", "page", "delete")


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[SystemCreateAccess])
    async def create_system(self, payload: SystemInput) -> SystemType:
        return await SystemService.create(payload)

    @strawberry.mutation(permission_classes=[SystemUpdateAccess])
    async def update_system(self, system_id: int, payload: SystemInput) -> SystemType:
        return await SystemService.update(system_id, payload)

    @strawberry.mutation(permission_classes=[SystemDeleteAccess])
    async def delete_system(self, system_id: int) -> bool:
        return await SystemService.delete(system_id)

    @strawberry.mutation(permission_classes=[TeamCreateAccess])
    async def create_team(self, payload: TeamInput) -> TeamType:
        return await TeamService.create(payload)

    @strawberry.mutation(permission_classes=[TeamUpdateAccess])
    async def update_team(self, team_id: int, payload: TeamInput) -> TeamType:
        return await TeamService.update(team_id, payload)

    @strawberry.mutation(permission_classes=[TeamDeleteAccess])
    async def delete_team(self, team_id: int) -> bool:
        return await TeamService.delete(team_id)

    @strawberry.mutation(permission_classes=[ModuleCreateAccess])
    async def create_module(self, payload: ModuleInput) -> ModuleType:
        return await ModuleService.create(payload)

    @strawberry.mutation(permission_classes=[ModuleUpdateAccess])
    async def update_module(self, module_id: int, payload: ModuleInput) -> ModuleType:
        return await ModuleService.update(module_id, payload)

    @strawberry.mutation(permission_classes=[ModuleDeleteAccess])
    async def delete_module(self, module_id: int) -> bool:
        return await ModuleService.delete(module_id)

    @strawberry.mutation(permission_classes=[EntityCreateAccess])
    async def create_entity(self, payload: EntityInput) -> EntityType:
        return await EntityService.create(payload)

    @strawberry.mutation(permission_classes=[EntityUpdateAccess])
    async def update_entity(self, entity_id: int, payload: EntityInput) -> EntityType:
        return await EntityService.update(entity_id, payload)

    @strawberry.mutation(permission_classes=[EntityDeleteAccess])
    async def delete_entity(self, entity_id: int) -> bool:
        return await EntityService.delete(entity_id)

    @strawberry.mutation(permission_classes=[FeatureCreateAccess])
    async def create_feature(self, payload: FeatureInput) -> FeatureType:
        return await FeatureService.create(payload)

    @strawberry.mutation(permission_classes=[FeatureUpdateAccess])
    async def update_feature(self, feature_id: int, payload: FeatureInput) -> FeatureType:
        return await FeatureService.update(feature_id, payload)

    @strawberry.mutation(permission_classes=[FeatureDeleteAccess])
    async def delete_feature(self, feature_id: int) -> bool:
        return await FeatureService.delete(feature_id)

    @strawberry.mutation(permission_classes=[ActionCreateAccess])
    async def create_action(self, payload: ActionInput) -> ActionType:
        return await ActionService.create(payload)

    @strawberry.mutation(permission_classes=[ActionUpdateAccess])
    async def update_action(self, action_id: int, payload: ActionInput) -> ActionType:
        return await ActionService.update(action_id, payload)

    @strawberry.mutation(permission_classes=[ActionDeleteAccess])
    async def delete_action(self, action_id: int) -> bool:
        return await ActionService.delete(action_id)

    @strawberry.mutation(permission_classes=[UserAssignmentCreateAccess])
    async def create_user_assignment(self, payload: UserAssignmentInput) -> UserAssignmentType:
        return await UserAssignmentService.create(payload)

    @strawberry.mutation(permission_classes=[UserAssignmentUpdateAccess])
    async def update_user_assignment(
        self, assignment_id: int, payload: UserAssignmentInput
    ) -> UserAssignmentType:
        return await UserAssignmentService.update(assignment_id, payload)

    @strawberry.mutation(permission_classes=[UserAssignmentDeleteAccess])
    async def delete_user_assignment(self, assignment_id: int) -> bool:
        return await UserAssignmentService.delete(assignment_id)

    @strawberry.mutation(permission_classes=[CountryCreateAccess])
    async def create_country(self, payload: CountryInput) -> CountryType:
        return await CountryService.create(payload)

    @strawberry.mutation(permission_classes=[CountryUpdateAccess])
    async def update_country(self, country_id: int, payload: CountryInput) -> CountryType:
        return await CountryService.update(country_id, payload)

    @strawberry.mutation(permission_classes=[CountryDeleteAccess])
    async def delete_country(self, country_id: int) -> bool:
        return await CountryService.delete(country_id)

    @strawberry.mutation(permission_classes=[CurrencyCreateAccess])
    async def create_currency(self, payload: CurrencyInput) -> CurrencyType:
        return await CurrencyService.create(payload)

    @strawberry.mutation(permission_classes=[CurrencyUpdateAccess])
    async def update_currency(self, currency_id: int, payload: CurrencyInput) -> CurrencyType:
        return await CurrencyService.update(currency_id, payload)

    @strawberry.mutation(permission_classes=[CurrencyDeleteAccess])
    async def delete_currency(self, currency_id: int) -> bool:
        return await CurrencyService.delete(currency_id)

    @strawberry.mutation(permission_classes=[LangCreateAccess])
    async def create_lang(self, payload: LangInput) -> LangType:
        return await LangService.create(payload)

    @strawberry.mutation(permission_classes=[LangUpdateAccess])
    async def update_lang(self, lang_id: int, payload: LangInput) -> LangType:
        return await LangService.update(lang_id, payload)

    @strawberry.mutation(permission_classes=[LangDeleteAccess])
    async def delete_lang(self, lang_id: int) -> bool:
        return await LangService.delete(lang_id)

    @strawberry.mutation(permission_classes=[CompanyCreateAccess])
    async def create_company(self, payload: CompanyInput) -> CompanyType:
        return await CompanyService.create(payload)

    @strawberry.mutation(permission_classes=[CompanyUpdateAccess])
    async def update_company(self, company_id: int, payload: CompanyInput) -> CompanyType:
        return await CompanyService.update(company_id, payload)

    @strawberry.mutation(permission_classes=[CompanyDeleteAccess])
    async def delete_company(self, company_id: int) -> bool:
        return await CompanyService.delete(company_id)

    @strawberry.mutation(permission_classes=[CompanySystemLinkCreateAccess])
    async def create_company_system_link(
        self, payload: CompanySystemLinkInput
    ) -> CompanySystemLinkType:
        return await CompanySystemLinkService.create(payload)

    @strawberry.mutation(permission_classes=[CompanySystemLinkUpdateAccess])
    async def update_company_system_link(
        self,
        company_id: int,
        system_id: int,
        payload: CompanySystemLinkInput,
    ) -> CompanySystemLinkType:
        return await CompanySystemLinkService.update(company_id, system_id, payload)

    @strawberry.mutation(permission_classes=[CompanySystemLinkDeleteAccess])
    async def delete_company_system_link(self, company_id: int, system_id: int) -> bool:
        return await CompanySystemLinkService.delete(company_id, system_id)

    @strawberry.mutation(permission_classes=[PartyCreateAccess])
    async def create_party(self, payload: PartyInput) -> PartyType:
        return await PartyService.create(payload)

    @strawberry.mutation(permission_classes=[PartyUpdateAccess])
    async def update_party(self, party_id: int, payload: PartyInput) -> PartyType:
        return await PartyService.update(party_id, payload)

    @strawberry.mutation(permission_classes=[PartyDeleteAccess])
    async def delete_party(self, party_id: int) -> bool:
        return await PartyService.delete(party_id)

    @strawberry.mutation(permission_classes=[AppCreateAccess])
    async def create_app(self, payload: AppInput) -> AppType:
        return await AppService.create(payload)

    @strawberry.mutation(permission_classes=[AppUpdateAccess])
    async def update_app(self, app_id: int, payload: AppInput) -> AppType:
        return await AppService.update(app_id, payload)

    @strawberry.mutation(permission_classes=[AppDeleteAccess])
    async def delete_app(self, app_id: int) -> bool:
        return await AppService.delete(app_id)

    @strawberry.mutation(permission_classes=[AppSettingCreateAccess])
    async def create_app_setting(self, payload: AppSettingsInput) -> AppSettingsType:
        return await AppSettingsService.create(payload)

    @strawberry.mutation(permission_classes=[AppSettingUpdateAccess])
    async def update_app_setting(
        self, setting_id: int, payload: AppSettingsInput
    ) -> AppSettingsType:
        return await AppSettingsService.update(setting_id, payload)

    @strawberry.mutation(permission_classes=[AppSettingDeleteAccess])
    async def delete_app_setting(self, setting_id: int) -> bool:
        return await AppSettingsService.delete(setting_id)

    @strawberry.mutation(permission_classes=[TimezoneCreateAccess])
    async def create_timezone(self, payload: TimezoneInput) -> TimezoneType:
        return await TimezoneService.create(payload)

    @strawberry.mutation(permission_classes=[TimezoneUpdateAccess])
    async def update_timezone(self, timezone_id: int, payload: TimezoneInput) -> TimezoneType:
        return await TimezoneService.update(timezone_id, payload)

    @strawberry.mutation(permission_classes=[TimezoneDeleteAccess])
    async def delete_timezone(self, timezone_id: int) -> bool:
        return await TimezoneService.delete(timezone_id)

    @strawberry.mutation(permission_classes=[PageCreateAccess])
    async def create_page(self, payload: PageInput) -> PageType:
        return await PageService.create(payload)

    @strawberry.mutation(permission_classes=[PageUpdateAccess])
    async def update_page(self, page_id: int, payload: PageInput) -> PageType:
        return await PageService.update(page_id, payload)

    @strawberry.mutation(permission_classes=[PageDeleteAccess])
    async def delete_page(self, page_id: int) -> bool:
        return await PageService.delete(page_id)
