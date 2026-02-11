from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from app.core.config import settings
import os

db_url = str(
    settings.DATABASE_URL_DOCKER if os.getenv("DOCKER_ENV") else settings.DATABASE_URL
)

if not db_url:
    raise ValueError("No Database URL found in environment variables!")

# Only enable SQL echo if explicitly requested
echo_sql = os.getenv("ECHO_SQL", "false").lower() == "true"

engine = create_async_engine(db_url, echo=echo_sql, future=True)

async_session_factory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
