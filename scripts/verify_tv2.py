"""Verify TV2 against running PostgreSQL/API; creates and removes its own fake row.

Exit 0: all checks passed; 1: operational/API failure; 2: plaintext detected.
This is a smoke check, not TV3's attack lab or proof of cryptographic security.
"""
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    env = {**dotenv_values(ROOT / ".env"), **os.environ}
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "checks": {}}
    checks = report["checks"]
    sid = "T2" + secrets.token_hex(6)
    payload = {"student_id": sid, "full_name": "TV2 Smoke (fictional)", "major": "Testing",
               "national_id": "TV2-fake-national-id", "phone": "TV2-fake-phone",
               "address": "TV2 fictional address"}
    created = False
    engine = None
    result = 1

    def expect(name, response, status, code=None):
        checks[name] = response.status_code == status and (code is None or response.json().get("code") == code)
        if not checks[name]:
            raise RuntimeError(name)

    try:
        engine = create_engine(env["DATABASE_URL"], hide_parameters=True)
        if engine.dialect.name != "postgresql":
            raise RuntimeError("PostgreSQL required")
        with engine.connect() as conn:
            report["postgresql_version"] = conn.scalar(text("SHOW server_version"))
            columns = {c["name"]: str(c["type"]).upper() for c in inspect(conn).get_columns("students")}
            checks["schema_h3_bytea"] = all(columns.get(f"{f}_{suffix}") == "BYTEA"
                for f in ("national_id", "phone", "address") for suffix in ("ct", "nonce"))
        with httpx.Client(base_url=f"http://127.0.0.1:{env.get('API_PORT') or '8000'}",
                          timeout=15, trust_env=False) as client:
            admin = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}
            viewer = {"Authorization": f"Bearer {env['VIEWER_TOKEN']}"}
            path = f"/students/{sid}"
            try:
                expect("health_200", client.get("/health"), 200)
                expect("missing_token_401", client.get("/students"), 401)
                response = client.post("/students", json=payload, headers=admin)
                created = response.status_code == 201
                expect("create_201", response, 201)
                checks["create_roundtrip"] = response.json() == payload
                expect("duplicate_409", client.post("/students", json=payload, headers=admin),
                       409, "duplicate_student")
                response = client.get(path, headers=viewer)
                expect("viewer_read_200", response, 200)
                checks["read_roundtrip"] = response.json() == payload
                expect("viewer_write_403", client.delete(path, headers=viewer), 403)
                expect("put_id_422", client.put(path, json=payload, headers=admin), 422)
                with engine.connect() as conn:
                    row = conn.execute(text("SELECT * FROM students WHERE student_id=:sid"),
                                       {"sid": sid}).mappings().one()
                    checks["plaintext_absent_in_sensitive_columns"] = all(
                        payload[f].encode("utf-8") not in bytes(row[f"{f}_ct"])
                        for f in ("national_id", "phone", "address"))
                    checks["ciphertext_includes_16_byte_tag"] = all(
                        len(row[f"{f}_ct"]) == len(payload[f].encode("utf-8")) + 16
                        for f in ("national_id", "phone", "address"))
                    checks["stored_key_version"] = row["key_version"] == (env.get("KEY_VERSION") or "v1")
                    before = {f: bytes(row[f"{f}_nonce"]) for f in ("national_id", "phone", "address")}
                    checks["nonce_lengths_12"] = all(len(n) == 12 for n in before.values())
                update = {k: v for k, v in payload.items() if k != "student_id"}
                update["address"] = "Updated fictional address"
                response = client.put(path, json=update, headers=admin)
                expect("put_200", response, 200)
                checks["put_roundtrip"] = response.json() == {"student_id": sid, **update}
                with engine.connect() as conn:
                    row = conn.execute(text("SELECT * FROM students WHERE student_id=:sid"),
                                       {"sid": sid}).mappings().one()
                    checks["put_refreshes_three_nonces"] = all(
                        before[f] != bytes(row[f"{f}_nonce"]) for f in before)
                expect("delete_204", client.delete(path, headers=admin), 204)
                created = False
                expect("deleted_get_404", client.get(path, headers=admin), 404, "not_found")
            finally:
                if created:
                    cleanup = client.delete(path, headers=admin)
                    checks["cleanup"] = cleanup.status_code in (204, 404)
            failures = [name for name, passed in checks.items() if not passed]
            result = 0 if not failures else (2 if failures == ["plaintext_absent_in_sensitive_columns"] else 1)
    except Exception as exc:
        # Record only the type, never a DB URL, credentials or response body.
        report["error_type"] = type(exc).__name__
    finally:
        if engine is not None:
            engine.dispose()
    report["result"] = "pass" if result == 0 else "blocked_by_plaintext" if result == 2 else "failed"
    report["note"] = "A passing smoke check is not an AES-GCM security audit. Run TV1/TV3 suites too."
    (ROOT / "docs" / "tv2_verification.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    print(f"Result: {report['result']}; evidence: docs/tv2_verification.json")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
