import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models.user_model import User
from routers.auth import bcrypt_context, get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)

TestingSession = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def override_get_db():
    async with TestingSession() as db:
        yield db


async def override_current_user():
    return {
        "id": 1,
        "username": "TestUser2004",
        "email": "test@gmail.com",
        "password": "Some_password@2004"
    }


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def create_user():
    hashed_password = bcrypt_context.encrypt("Panel@2004")
    user = User(
        username="SomeUser2004",
        email="someuser2004@gmail.com",
        hashed_password=hashed_password,
    )
    async with TestingSession() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    yield user
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users"))
        await conn.commit()
