import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# --- IMPORT SQLMODEL AND YOUR MODELS ---
from sqlmodel import SQLModel
from app.core.config import settings
from app.models.recipe import Recipe
from app.models.subscriber import Subscriber
from app.models.recipe import Ingredient # Added for completeness
# ---------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def render_item(type_, obj, autogen_context):
    """
    Automagically fixes the 'sqlmodel.sql.sqltypes' path bug in generated files.
    """
    if type_ == "type" and hasattr(obj, "__module__") and obj.__module__.startswith("sqlmodel"):
        return f"sqlmodel.{obj.__class__.__name__}"
    return False

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item  # Added here
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """
    This is where the actual migration happens for the online/async flow.
    """
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        render_item=render_item  # Crucial: Added here for autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Creates an engine and runs the sync migration function."""
    section = config.get_section(config.config_ini_section, {})
    
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    if os.getenv("DOCKER_ENV") == "true":
        url = str(settings.DATABASE_URL_DOCKER)
    else:
        url = str(settings.DATABASE_URL)
    
    escaped_url = url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", escaped_url)
    
    print(f"DEBUG: Alembic using URL: {url}")

    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
