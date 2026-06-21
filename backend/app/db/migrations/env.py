"""Alembic environment configuration.

Configures how migrations connect to the database and which models
are tracked for autogenerate support.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.db.base import Base
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.user import User  # noqa: F401 -- registers model with Base.metadata
from app.models.document import Document  # noqa: F401

# Alembic Config object, provides access to .ini file values
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from our application settings (not alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# This is the metadata Alembic compares against the live database
# to auto-generate migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live database connection.

    Generates SQL scripts based on the model metadata, useful for
    reviewing changes before applying them.
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


def do_run_migrations(connection) -> None:
    """Configure and execute migrations using an active connection.

    Args:
        connection: An active synchronous-style database connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations through it.

    Required because our application uses asyncpg, but Alembic's
    migration execution is synchronous internally.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()