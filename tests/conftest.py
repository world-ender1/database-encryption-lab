# tests/conftest.py
"""Shared pytest fixtures (contract H5).

Forces in-memory SQLite and test credentials before importing app modules so
tests never touch the local .env file or PostgreSQL database.
"""
import base64
import os

os.environ.update({
    "DATABASE_URL": "sqlite://",
    "ENCRYPTION_KEY_B64": base64.b64encode(bytes(range(32))).decode("ascii"),
    "KEY_VERSION": "v1",
    "ADMIN_TOKEN": "test-admin-token",
    "VIEWER_TOKEN": "test-viewer-token",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402


@pytest.fixture
def db_session():
    """Isolated in-memory SQLite session shared between test and FastAPI app."""
    # Lazy imports inside fixture so TV1 crypto/auth tests run without TV2 API/DB files.
    import app.models  # noqa: F401
    from app.database import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient wired to the isolated in-memory db_session."""
    from app.database import get_db
    from app.main import app

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
    return {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def viewer_headers():
    return {"Authorization": "Bearer test-viewer-token"}


@pytest.fixture
def sample_student():
    return {
        "student_id": "SV9001",
        "full_name": "Nguyen Van A",
        "major": "Computer Science",
        "national_id": "012345678901",
        "phone": "0901234567",
        "address": "Ha Noi (fictional)",
    }
