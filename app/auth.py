# app/auth.py
import secrets
from typing import Literal, Protocol

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

Role = Literal["admin", "viewer"]
_bearer = HTTPBearer(auto_error=False)


class TokenSettings(Protocol):
    """Hai field H4 mà auth cần. `Settings` của TV2 có sẵn hai field này."""

    admin_token: str
    viewer_token: str


def get_token_settings() -> TokenSettings:
    """Lấy token từ cấu hình H4 (`app.config` của TV2).

    Import trong thân hàm: import `app.auth` không cần `config.py`, nên TV1 viết và test
    `auth.py` độc lập với TV2. Test thay hàm này bằng `dependency_overrides`.
    """
    from app.config import get_settings

    return get_settings()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _same(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def require_reader(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: TokenSettings = Depends(get_token_settings),
) -> Role:
    if creds is None:
        raise _unauthorized()
    if _same(creds.credentials, settings.admin_token):
        return "admin"
    if _same(creds.credentials, settings.viewer_token):
        return "viewer"
    raise _unauthorized()


def require_admin(role: Role = Depends(require_reader)) -> Role:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return role
