import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator

from app.main import app
from app.core.db import get_session
from app.core.config import settings

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    echo=False
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator:
    """Creates the tables, yields the session, then drops tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(async_session) -> AsyncGenerator:
    """Overrides the DB dependency and adds API Key headers."""
    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session
    
    api_key = str(settings.API_SECRET_KEY) if settings.API_SECRET_KEY else "test_secret"
    headers = {"X-Admin-Key": api_key}
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test",
        headers=headers
    ) as c:
        yield c
    
    app.dependency_overrides.clear()
