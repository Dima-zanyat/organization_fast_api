import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import Model, get_session
from tests.constant import (
    TEST_DATABASE_URL,
    BASE_URL_TEST,
    PATCH_DEPARTMENT,
    CREATE_DEPARTMENT_URL,
    BASE_DEPARTMENT_NAME,
    DELETE_DEPARTMENT,
)

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


@pytest_asyncio.fixture
async def base_department(client):
    response = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT_NAME,
            "parent_id": None,
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def department_tree(client):

    root = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT_NAME,
            "parent_id": None,
        },
    )
    root = root.json()

    dep_a = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": "dep_a",
            "parent_id": root.get("id"),
        },
    )
    dep_a = dep_a.json()

    dep_b = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": "dep_b",
            "parent_id": root.get("id"),
        },
    )
    dep_b = dep_b.json()

    dep_c = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": "dep_c",
            "parent_id": dep_a.get("id"),
        },
    )
    dep_c = dep_c.json()
    return {
        "root": root,
        "dep_a": dep_a,
        "dep_b": dep_b,
        "dep_c": dep_c,
    }


@pytest_asyncio.fixture
async def get_patch_url(department_tree):
    return PATCH_DEPARTMENT + str(department_tree.get("dep_c").get("id"))


@pytest_asyncio.fixture
async def delete_dep_url_cascade(department_tree):
    return DELETE_DEPARTMENT + str(department_tree.get("dep_b").get("id"))


@pytest_asyncio.fixture
async def delete_dep_url_reassign(department_tree):
    return DELETE_DEPARTMENT + str(department_tree.get("dep_c").get("id"))
