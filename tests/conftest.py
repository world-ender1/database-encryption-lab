"""H5 bootstrap for TV2; TV3 owns this shared fixture after handover.

In-memory SQLite only: never load the real .env or contact PostgreSQL in pytest.
"""
import base64
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set BEFORE importing any module that creates the engine or cached settings.
os.environ.update({
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "ENCRYPTION_KEY_B64": base64.b64encode(bytes(range(32))).decode("ascii"),
    "KEY_VERSION": "v1",
    "ADMIN_TOKEN": "test-only-admin",
    "VIEWER_TOKEN": "test-only-viewer",
})

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:",
                           connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_db():
        yield db_session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test-only-admin"}


@pytest.fixture
def viewer_headers():
    return {"Authorization": "Bearer test-only-viewer"}


@pytest.fixture
def sample_student():
    return {"student_id": "SV9001", "full_name": "Nguyễn Văn A", "major": "An toàn thông tin",
            "national_id": "012345678901", "phone": "0901234567", "address": "Hà Nội (giả lập)"}
