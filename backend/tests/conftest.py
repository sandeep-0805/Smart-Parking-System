import pytest
from app.config import settings

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
