import asyncio
import os
import sys
from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def pytest_configure(config: pytest.Config) -> None:
    try:
        import prometheus_client  # noqa: F401
    except ImportError:
        pytest.exit(
            "Tests require project dependencies (including prometheus_client).\n"
            "From the project root run:\n"
            "  poetry install\n"
            "  poetry run pytest\n"
            "Bare `pytest` uses your global Python and skips the Poetry venv.\n",
            returncode=1,
        )


def _test_db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/app_test",
    )


def _ensure_test_db_exists(url: str) -> None:
    import psycopg2

    dbname = url.rsplit("/", 1)[-1].split("?", 1)[0]
    admin_url = url.rsplit("/", 1)[0] + "/postgres"

    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f'CREATE DATABASE "{dbname}"')
    finally:
        conn.close()


def _alembic_cfg(test_db_url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", test_db_url)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def _configure_test_env() -> None:
    os.environ["DATABASE_URL"] = _test_db_url()


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database(_configure_test_env: None) -> None:
    url = _test_db_url()
    _ensure_test_db_exists(url)
    command.upgrade(_alembic_cfg(url), "head")


@pytest.fixture(scope="session")
def app(_setup_test_database: None):
    from app.db.session import get_db  # noqa: WPS433
    from main import app as fastapi_app  # noqa: WPS433

    test_engine = create_async_engine(
        os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg_async://", 1),
        echo=False,
        pool_pre_ping=True,
    )
    TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def get_test_db() -> AsyncIterator[AsyncSession]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = get_test_db
    return fastapi_app


@pytest.fixture()
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture(scope="session")
def _test_engine(_setup_test_database: None):
    return create_async_engine(
        os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg_async://", 1),
        echo=False,
        pool_pre_ping=True,
    )


@pytest.fixture()
async def db_session(_test_engine) -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def _clean_db_between_tests(_test_engine) -> AsyncIterator[None]:
    yield
    from app.db.base import Base  # noqa: WPS433

    tables = sorted(Base.metadata.tables.keys())
    if not tables:
        return
    stmt = "TRUNCATE TABLE " + ", ".join(f'"{t}"' for t in tables) + " RESTART IDENTITY CASCADE;"
    async with _test_engine.begin() as conn:
        await conn.execute(text(stmt))


async def register_and_login(client: AsyncClient, *, email: str = "t@example.com", password: str = "pass12345"):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "name": "Tester", "password": password},
    )
    assert r.status_code == 201
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["user"]
