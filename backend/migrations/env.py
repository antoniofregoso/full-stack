import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlmodel import SQLModel

# IMPORTANTE: Importar tus modelos aquí para que Alembic los detecte
from app.auth.models.auth_user import (
    AuthUser,
    AuthUserRole,
    AuthRole,
    AuthPermission,
    AuthRolePermission,
)
from app.core.models.core_party import CoreParty, CoreRole, CorePartyRole
from app.core.models.core_timezone import CoreTimezone
from app.core.models.core_lang import CoreLang
from app.core.models.core_country import CoreCountry
from app.core.models.core_country import CoreCountryState
from app.core.models.core_country_timezone_rel import CoreCountryTimezoneRel
from app.core.models.core_company import CoreCompany
from app.core.models.core_audit import CoreAudit
from app.core.models.core_currency import CoreCurrency
from app.core.models.core_entity import CoreEntity
from app.core.models.core_feature import CoreFeature
from app.core.models.core_module import CoreModule
from app.core.models.core_seed_run import CoreSeedRun
from app.core.models.core_page import CorePage
from app.core.models.core_system import CoreSystem
from app.core.models.core_team import CoreTeam
from app.core.models.core_user_assignment import CoreUserAssignment
from app.talent.models.talent_node_assignment import TalentNodeAssignment
from settings import settings  # Tu configuración centralizada

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL dynamically from settings
config.set_main_option("sqlalchemy.url", settings.DB_CONFIG)

# Add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
