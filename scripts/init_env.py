# scripts/init_env.py
"""Sinh .env cục bộ cho demo. Không ghi đè nếu .env đã tồn tại."""
import base64
import secrets
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
API_PORT = 8000
DB_PORT = 55432


def main(env_path: Path = ENV_PATH) -> int:
    if env_path.exists():
        print(".env already exists - kept as is (a new key could not decrypt existing data).")
        return 0
    pg_password = secrets.token_urlsafe(24)
    lines = [
        f"ENCRYPTION_KEY_B64={base64.b64encode(secrets.token_bytes(32)).decode('ascii')}",
        "KEY_VERSION=v1",
        f"ADMIN_TOKEN={secrets.token_urlsafe(32)}",
        f"VIEWER_TOKEN={secrets.token_urlsafe(32)}",
        f"POSTGRES_PASSWORD={pg_password}",
        f"API_PORT={API_PORT}",
        f"DB_PORT={DB_PORT}",
        f"DATABASE_URL=postgresql+psycopg://demo:{pg_password}@127.0.0.1:{DB_PORT}/encryption_demo",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Created .env - do NOT commit this file.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
