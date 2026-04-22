import asyncio
import sys
from pathlib import Path

# Make imports work regardless of current working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import db
from logging_config import configure_logging, get_logger
from settings import settings
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

# Import models so SQLModel metadata includes all tables.
from app.auth.models.auth_user import (  # noqa: F401
    AuthPermission,
    AuthRole,
    AuthRolePermission,
    AuthUser,
    AuthUserRole,
)
from app.core.models.core_company import CoreCompany  # noqa: F401
from app.core.models.core_country import CoreCountry, CoreCountryState  # noqa: F401
from app.core.models.core_country_timezone_rel import CoreCountryTimezoneRel  # noqa: F401
from app.core.models.core_currency import CoreCurrency  # noqa: F401
from app.core.models.core_entity import CoreEntity  # noqa: F401
from app.core.models.core_feature import CoreFeature  # noqa: F401
from app.core.models.core_lang import CoreLang  # noqa: F401
from app.core.models.core_module import CoreModule  # noqa: F401
from app.core.models.core_page import CorePage  # noqa: F401
from app.core.models.core_party import CoreParty, CorePartyRole, CoreRole  # noqa: F401
from app.core.models.core_seed_run import CoreSeedRun  # noqa: F401
from app.core.models.core_system import CoreSystem  # noqa: F401
from app.core.models.core_team import CoreTeam  # noqa: F401
from app.core.models.core_timezone import CoreTimezone  # noqa: F401
from app.core.models.core_user_assignment import CoreUserAssignment  # noqa: F401
from app.talent.models.talent_node_assignment import TalentNodeAssignment  # noqa: F401
from seed import _run_seed


configure_logging()
logger = get_logger(__name__)


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


async def _ensure_database_exists() -> None:
    target_url = make_url(settings.DB_CONFIG)
    target_db_name = target_url.database

    if not target_db_name:
        raise RuntimeError("DB_CONFIG must include a database name.")

    if target_db_name == "postgres":
        logger.info("Target database is 'postgres'; skipping database creation step.")
        return

    admin_url = target_url.set(database="postgres")
    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
        echo=False,
    )

    try:
        async with admin_engine.connect() as conn:
            exists_result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": target_db_name},
            )
            if exists_result.scalar_one_or_none():
                logger.info("Database '%s' already exists.", target_db_name)
                return

            quoted_name = _quote_ident(target_db_name)
            logger.info("Creating database '%s'...", target_db_name)
            await conn.execute(text(f"CREATE DATABASE {quoted_name}"))
            logger.info("Database '%s' created.", target_db_name)
    finally:
        await admin_engine.dispose()


async def _init_db() -> None:
    try:
        await _ensure_database_exists()
        logger.info("Creating database tables with SQLModel metadata...")
        await db.create_all()
        logger.info("Running initial seeds...")
        await _run_seed("all")
        logger.info("Database initialized successfully.")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(_init_db())
