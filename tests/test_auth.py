# tests/test_auth.py
import sys
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import get_token_settings, require_admin, require_reader

ADMIN = "admin-token-123"
VIEWER = "viewer-token-456"


@pytest.fixture
def client():
    # App nhỏ chỉ để thử auth; không cần DB, không đọc .env, không cần app/config.py của TV2.
    app = FastAPI()

    @app.get("/read")
    def read(role: str = Depends(require_reader)):
        return {"role": role}

    @app.delete("/write")
    def write(role: str = Depends(require_admin)):
        return {"role": role}

    app.dependency_overrides[get_token_settings] = lambda: SimpleNamespace(admin_token=ADMIN, viewer_token=VIEWER)
    return TestClient(app)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("headers", [
    {},
    bearer("sai-token"),
    {"Authorization": "Basic YWRtaW46YWRtaW4="},
    {"Authorization": "Bearer "},
    bearer(ADMIN[:-1]),
], ids=["missing", "wrong_token", "basic_scheme", "empty_token", "admin_prefix"])
def test_auth_401_without_valid_token(client, headers):
    for r in (client.get("/read", headers=headers), client.delete("/write", headers=headers)):
        assert r.status_code == 401
        assert r.headers["www-authenticate"] == "Bearer"


def test_auth_reader_accepts_viewer_and_admin(client):
    assert client.get("/read", headers=bearer(VIEWER)).json() == {"role": "viewer"}
    assert client.get("/read", headers=bearer(ADMIN)).json() == {"role": "admin"}


def test_auth_viewer_cannot_write(client):
    assert client.delete("/write", headers=bearer(VIEWER)).status_code == 403


def test_auth_admin_can_write(client):
    r = client.delete("/write", headers=bearer(ADMIN))
    assert r.status_code == 200
    assert r.json() == {"role": "admin"}


def test_auth_non_ascii_token_gives_401_not_500(client):
    r = client.get("/read", headers={"Authorization": "Bearer t\u00e9st".encode("latin-1")})
    assert r.status_code == 401


def test_auth_tokens_come_from_app_config(monkeypatch):
    # Lúc chạy thật, token lấy từ app.config.get_settings() (H4, TV2).
    # Dùng module giả thay app.config nên test không cần file config.py của TV2.
    fake_config = ModuleType("app.config")
    fake_config.get_settings = lambda: SimpleNamespace(admin_token=ADMIN, viewer_token=VIEWER)
    monkeypatch.setitem(sys.modules, "app.config", fake_config)
    settings = get_token_settings()
    assert (settings.admin_token, settings.viewer_token) == (ADMIN, VIEWER)
