import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import Model, get_session
from tests.constant import TEST_DATABASE_URL, BASE_URL_TEST

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


# dependency override
async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=BASE_URL_TEST,
    ) as ac:
        yield ac
