# scripts/attack_lab.py
"""Controlled attack simulation A1-A5 against the local demo PostgreSQL DB.

Run from the repository root after seeding SV9001 and SV9002:
    python -m scripts.demo_client
    python -m scripts.attack_lab
"""
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values
from sqlalchemy import MetaData, Table, create_engine, select, update

PLAIN_NATIONAL_IDS = (b"012345678901", b"098765432109")


def _load_config() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        raise SystemExit("Missing .env file. Run `python scripts/init_env.py` first.")
    raw = dotenv_values(env_path)
    missing = [k for k in ("DATABASE_URL", "ADMIN_TOKEN", "VIEWER_TOKEN") if not raw.get(k)]
    if missing:
        raise SystemExit(f"Missing keys in .env: {', '.join(missing)}")
    return {k: str(v) for k, v in raw.items() if v is not None}


def _status(client: httpx.Client, method: str, path: str, headers=None) -> int:
    return client.request(method, path, headers=headers).status_code


def a1(client: httpx.Client) -> int:
    code = _status(client, "GET", "/students/SV9001")
    print("[A1] Missing bearer token ->", code)
    return code


def a2(client: httpx.Client, admin_headers: dict[str, str], viewer_headers: dict[str, str]) -> int:
    code = _status(client, "DELETE", "/students/SV9001", headers=viewer_headers)
    row_exists = _status(client, "GET", "/students/SV9001", headers=admin_headers) == 200
    print("[A2] Viewer attempts DELETE ->", code, "| row still there:", row_exists)
    return code


def a3(conn, students: Table) -> bool:
    cts = conn.execute(select(students.c.national_id_ct)).scalars().all()
    leaked = any(plain in ct for ct in cts for plain in PLAIN_NATIONAL_IDS)
    print("[A3] DB contains ciphertext, not the plaintext:", not leaked)
    return not leaked


def a4(
    conn,
    students: Table,
    client: httpx.Client,
    admin_headers: dict[str, str],
) -> int:
    sv9001 = students.c.student_id == "SV9001"
    original = conn.execute(select(students.c.national_id_ct).where(sv9001)).scalar_one()
    try:
        tampered = bytes([original[0] ^ 0x01]) + original[1:]
        conn.execute(update(students).where(sv9001).values(national_id_ct=tampered))
        conn.commit()
        code = _status(client, "GET", "/students/SV9001", headers=admin_headers)
        print("[A4] Tampered 1 ciphertext byte ->", code)
        return code
    finally:
        conn.rollback()
        conn.execute(update(students).where(sv9001).values(national_id_ct=original))
        conn.commit()


def a5(
    conn,
    students: Table,
    client: httpx.Client,
    admin_headers: dict[str, str],
) -> int:
    sv9001 = students.c.student_id == "SV9001"
    sv9002 = students.c.student_id == "SV9002"
    cols = (students.c.national_id_ct, students.c.national_id_nonce)
    orig = conn.execute(select(*cols).where(sv9001)).one()
    other = conn.execute(select(*cols).where(sv9002)).one()
    try:
        conn.execute(
            update(students)
            .where(sv9001)
            .values(national_id_ct=other[0], national_id_nonce=other[1])
        )
        conn.commit()
        code = _status(client, "GET", "/students/SV9001", headers=admin_headers)
        print("[A5] Swapped fields between students ->", code)
        return code
    finally:
        conn.rollback()
        conn.execute(
            update(students)
            .where(sv9001)
            .values(national_id_ct=orig[0], national_id_nonce=orig[1])
        )
        conn.commit()


def main() -> int:
    env = _load_config()
    api_url = f"http://127.0.0.1:{env.get('API_PORT') or '8000'}"
    admin_headers = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}
    viewer_headers = {"Authorization": f"Bearer {env['VIEWER_TOKEN']}"}

    engine = create_engine(env["DATABASE_URL"])
    students = Table("students", MetaData(), autoload_with=engine)

    with httpx.Client(base_url=api_url, timeout=10, trust_env=False) as client:
        precheck = _status(client, "GET", "/students/SV9001", headers=admin_headers)
        precheck_2 = _status(client, "GET", "/students/SV9002", headers=admin_headers)
        if precheck != 200 or precheck_2 != 200:
            print(
                f"Expected SV9001 ({precheck}) and SV9002 ({precheck_2}) to return 200. "
                "Run `python -m scripts.demo_client --reset` first."
            )
            return 1

        c1 = a1(client)
        c2 = a2(client, admin_headers, viewer_headers)
        with engine.connect() as conn:
            c3 = a3(conn, students)
            c4 = a4(conn, students, client, admin_headers)
            c5 = a5(conn, students, client, admin_headers)
        restored = _status(client, "GET", "/students/SV9001", headers=admin_headers)
        print("[Restore] legitimate read ->", restored)

    ok = (c1 == 401 and c2 == 403 and c3 and c4 == 409 and c5 == 409 and restored == 200)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
