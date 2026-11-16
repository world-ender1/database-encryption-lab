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

SENSITIVE_FIELDS = ("national_id", "phone", "address")
DEMO_IDS = ("SV9001", "SV9002")


def _load_config() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        raise SystemExit("Missing .env file. Run `python scripts/init_env.py` first.")
    raw = dotenv_values(env_path)
    missing = [k for k in ("DATABASE_URL", "ADMIN_TOKEN", "VIEWER_TOKEN") if not raw.get(k)]
    if missing:
        raise SystemExit(f"Missing keys in .env: {', '.join(missing)}")
    return {k: str(v) for k, v in raw.items() if v is not None}


def _row(conn, students: Table, student_id: str) -> dict:
    return dict(conn.execute(select(students).where(students.c.student_id == student_id)).mappings().one())


def _read_unchanged(client: httpx.Client, headers: dict[str, str], expected: dict) -> bool:
    response = client.get(f"/students/{expected['student_id']}", headers=headers)
    return response.status_code == 200 and response.json() == expected


def _integrity_failure(response: httpx.Response, expected: dict) -> bool:
    if response.status_code != 409:
        return False
    try:
        body = response.json()
    except ValueError:
        return False
    return (
        isinstance(body, dict)
        and body.get("code") == "integrity_failure"
        and not any(field in body for field in SENSITIVE_FIELDS)
        and not any(str(expected[field]) in response.text for field in SENSITIVE_FIELDS)
    )


def a1(client: httpx.Client) -> int:
    code = client.get("/students/SV9001").status_code
    print("[A1] Missing bearer token ->", code)
    return code


def a2(conn, students: Table, client: httpx.Client, admin_headers: dict[str, str],
       viewer_headers: dict[str, str], expected: dict) -> bool:
    before = _row(conn, students, expected["student_id"])
    response = client.delete(f"/students/{expected['student_id']}", headers=viewer_headers)
    unchanged = _row(conn, students, expected["student_id"]) == before
    readable = _read_unchanged(client, admin_headers, expected)
    ok = response.status_code == 403 and unchanged and readable
    print("[A2] Viewer DELETE ->", response.status_code,
          "| DB and API payload unchanged:", unchanged and readable)
    return ok


def a3(conn, students: Table, expected: dict[str, dict]) -> bool:
    ok = True
    for student_id, payload in expected.items():
        row = _row(conn, students, student_id)
        for field in SENSITIVE_FIELDS:
            plain = payload[field].encode("utf-8")
            ct, nonce = row[f"{field}_ct"], row[f"{field}_nonce"]
            ok &= (
                isinstance(ct, bytes) and isinstance(nonce, bytes)
                and len(ct) == len(plain) + 16 and len(nonce) == 12
                and plain not in ct and plain not in nonce
            )
    print("[A3] All demo sensitive columns contain ciphertext:", bool(ok))
    return bool(ok)


def a4(
    conn,
    students: Table,
    client: httpx.Client,
    admin_headers: dict[str, str],
    expected: dict,
) -> bool:
    student_id = expected["student_id"]
    predicate = students.c.student_id == student_id
    original = _row(conn, students, student_id)
    try:
        ct = original["national_id_ct"]
        tampered = bytes([ct[0] ^ 0x01]) + ct[1:]
        conn.execute(update(students).where(predicate).values(national_id_ct=tampered))
        conn.commit()
        response = client.get(f"/students/{student_id}", headers=admin_headers)
        rejected = _integrity_failure(response, expected)
        print("[A4] Tampered ciphertext ->", response.status_code,
              "integrity_failure:", rejected)
    finally:
        conn.rollback()
        conn.execute(update(students).where(predicate).values(national_id_ct=original["national_id_ct"]))
        conn.commit()
        if _row(conn, students, student_id) != original:
            raise RuntimeError("A4 failed to restore the original DB row")
    restored = _read_unchanged(client, admin_headers, expected)
    print("[A4] Original DB bytes and API payload restored:", restored)
    return rejected and restored


def a5(
    conn,
    students: Table,
    client: httpx.Client,
    admin_headers: dict[str, str],
    expected: dict[str, dict],
) -> bool:
    original = {sid: _row(conn, students, sid) for sid in DEMO_IDS}
    predicate = students.c.student_id == "SV9001"
    try:
        other = original["SV9002"]
        conn.execute(
            update(students)
            .where(predicate)
            .values(national_id_ct=other["national_id_ct"],
                    national_id_nonce=other["national_id_nonce"])
        )
        conn.commit()
        response = client.get("/students/SV9001", headers=admin_headers)
        rejected = _integrity_failure(response, expected["SV9001"])
        print("[A5] Swapped ciphertext and nonce ->", response.status_code,
              "integrity_failure:", rejected)
    finally:
        conn.rollback()
        conn.execute(
            update(students)
            .where(predicate)
            .values(national_id_ct=original["SV9001"]["national_id_ct"],
                    national_id_nonce=original["SV9001"]["national_id_nonce"])
        )
        conn.commit()
        if any(_row(conn, students, sid) != original[sid] for sid in DEMO_IDS):
            raise RuntimeError("A5 failed to restore the original DB rows")
    restored = all(_read_unchanged(client, admin_headers, expected[sid]) for sid in DEMO_IDS)
    print("[A5] Both DB rows and API payloads restored:", restored)
    return rejected and restored


def main() -> int:
    env = _load_config()
    api_url = f"http://127.0.0.1:{env.get('API_PORT') or '8000'}"
    admin_headers = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}
    viewer_headers = {"Authorization": f"Bearer {env['VIEWER_TOKEN']}"}

    engine = create_engine(env["DATABASE_URL"])
    try:
        students = Table("students", MetaData(), autoload_with=engine)
        with httpx.Client(base_url=api_url, timeout=10, trust_env=False) as client:
            expected = {}
            for student_id in DEMO_IDS:
                response = client.get(f"/students/{student_id}", headers=admin_headers)
                if response.status_code != 200:
                    print(f"Expected {student_id} to return 200. Seed disposable demo data first.")
                    return 1
                expected[student_id] = response.json()

            c1 = a1(client)
            with engine.connect() as conn:
                c2 = a2(conn, students, client, admin_headers, viewer_headers, expected["SV9001"])
                c3 = a3(conn, students, expected)
                c4 = a4(conn, students, client, admin_headers, expected["SV9001"])
                c5 = a5(conn, students, client, admin_headers, expected)
            return 0 if c1 == 401 and c2 and c3 and c4 and c5 else 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(main())
