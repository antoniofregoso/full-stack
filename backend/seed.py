import argparse
import asyncio

from config import db
from logging_config import configure_logging, get_logger
from app.auth.models.auth_user import (
    AuthPermission,
    AuthRole,
    AuthRolePermission,
    AuthUser,
    AuthUserRole,
)
from app.core.models.core_company import CoreCompany
from app.core.models.core_country import CoreCountry, CoreCountryState
from app.core.models.core_country_timezone_rel import CoreCountryTimezoneRel
from app.core.models.core_currency import CoreCurrency
from app.core.models.core_entity import CoreEntity
from app.core.models.core_feature import CoreFeature
from app.core.models.core_lang import CoreLang
from app.core.models.core_module import CoreModule
from app.core.models.core_page import CorePage
from app.core.models.core_party import CoreParty, CorePartyRole, CoreRole
from app.core.models.core_seed_run import CoreSeedRun
from app.core.models.core_system import CoreSystem
from app.core.models.core_team import CoreTeam
from app.core.models.core_timezone import CoreTimezone
from app.core.models.core_user_assignment import CoreUserAssignment
from app.core.service.core_bootstrap import (
    seed_auth_permissions,
    seed_auth_roles,
    seed_auth_role_permissions,
    seed_auth_users,
    seed_core_countries,
    seed_core_currencies,
    seed_core_langs,
    seed_core_pages,
    seed_core_systems,
    seed_core_user_assignments,
)


configure_logging()
logger = get_logger(__name__)


async def _run_seed(target: str) -> None:
    try:
        if target in {"auth", "users", "roles", "permissions", "all"}:
            inserted, updated = await seed_auth_users()
            logger.info(
                "Auth users seed finished. Inserted=%s Updated=%s",
                inserted,
                updated,
            )
            inserted_roles, updated_roles, assigned_roles = await seed_auth_roles()
            logger.info(
                "Auth roles seed finished. Inserted=%s Updated=%s Assigned=%s",
                inserted_roles,
                updated_roles,
                assigned_roles,
            )
            inserted_permissions, updated_permissions = await seed_auth_permissions()
            logger.info(
                "Auth permissions seed finished. Inserted=%s Updated=%s",
                inserted_permissions,
                updated_permissions,
            )
            assigned_permissions, skipped_permissions = await seed_auth_role_permissions()
            logger.info(
                "Auth role permissions seed finished. Assigned=%s Skipped=%s",
                assigned_permissions,
                skipped_permissions,
            )

        if target in {"currencies", "all"}:
            inserted, updated = await seed_core_currencies()
            logger.info(
                "Currencies seed finished. Inserted=%s Updated=%s",
                inserted,
                updated,
            )

        if target in {"langs", "languages", "all"}:
            inserted, updated = await seed_core_langs()
            logger.info(
                "Languages seed finished. Inserted=%s Updated=%s",
                inserted,
                updated,
            )

        if target in {"pages", "page", "all"}:
            inserted, updated = await seed_core_pages()
            logger.info(
                "Pages seed finished. Inserted=%s Updated=%s",
                inserted,
                updated,
            )

        if target in {"countries", "country", "country_states", "country-states", "all"}:
            inserted_countries, updated_countries, inserted_states, updated_states = (
                await seed_core_countries()
            )
            logger.info(
                "Countries and states seed finished. Countries inserted=%s updated=%s. States inserted=%s updated=%s",
                inserted_countries,
                updated_countries,
                inserted_states,
                updated_states,
            )

        if target in {"systems", "system", "teams", "all"}:
            inserted_systems, updated_systems, inserted_teams, updated_teams = (
                await seed_core_systems()
            )
            logger.info(
                "Systems and teams seed finished. Systems inserted=%s updated=%s. Teams inserted=%s updated=%s",
                inserted_systems,
                updated_systems,
                inserted_teams,
                updated_teams,
            )

        if target in {"user_assignments", "user-assignments", "assignments", "all"}:
            inserted, updated = await seed_core_user_assignments()
            logger.info(
                "Core user assignments seed finished. Inserted=%s Updated=%s",
                inserted,
                updated,
            )
    finally:
        await db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core data seeds manually.")
    parser.add_argument(
        "target",
        choices=[
            "all",
            "auth",
            "users",
            "roles",
            "permissions",
            "currencies",
            "langs",
            "languages",
            "pages",
            "page",
            "countries",
            "country",
            "country_states",
            "country-states",
            "systems",
            "system",
            "teams",
            "user_assignments",
            "user-assignments",
            "assignments",
        ],
        nargs="?",
        default="all",
        help="Seed target to execute. 'countries' also loads core_country_state records.",
    )
    args = parser.parse_args()
    asyncio.run(_run_seed(args.target))


if __name__ == "__main__":
    main()
