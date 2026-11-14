# scripts/benchmark.py
"""Benchmark plaintext vs AES-256-GCM DB insert/read latency and payload size.

Run from repository root:
    python -m scripts.benchmark
Outputs benchmark_results.csv in the repository root.
"""
import csv
import statistics
import time
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    select,
)

from app.crypto_service import CryptoService, EncryptedValue
from app.key_manager import decode_key

SIZES = (100, 1_000, 10_000)
REPEATS = 3
FIELDS = ("national_id", "phone", "address")
SAMPLE = {
    "national_id": "012345678901",
    "phone": "0901234567",
    "address": "Ha Noi (fictional)",
}


def _load_config() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        raise SystemExit("Missing .env file. Run `python scripts/init_env.py` first.")
    raw = dotenv_values(env_path)
    missing = [k for k in ("DATABASE_URL", "ENCRYPTION_KEY_B64") if not raw.get(k)]
    if missing:
        raise SystemExit(f"Missing keys in .env: {', '.join(missing)}")
    return {k: str(v) for k, v in raw.items() if v is not None}


def plain_rows(n: int) -> list[dict]:
    return [{"id": i, **SAMPLE} for i in range(n)]


def encrypted_rows(n: int, crypto: CryptoService) -> list[dict]:
    rows = []
    for i in range(n):
        row: dict = {"id": i}
        sid = str(i)
        for field in FIELDS:
            ev = crypto.encrypt(SAMPLE[field], sid, field)
            row[f"{field}_ct"] = ev.ciphertext
            row[f"{field}_nonce"] = ev.nonce
        rows.append(row)
    return rows


def run_insert(engine, table: Table, make_rows, n: int) -> float:
    with engine.begin() as conn:
        conn.execute(delete(table))  # Cleanup excluded from measured time
    t0 = time.perf_counter()
    with engine.begin() as conn:
        conn.execute(insert(table), make_rows(n))
    return time.perf_counter() - t0


def run_read_plain(engine, bench_plain: Table) -> float:
    t0 = time.perf_counter()
    with engine.connect() as conn:
        conn.execute(select(bench_plain)).all()
    return time.perf_counter() - t0


def run_read_encrypted(engine, bench_encrypted: Table, crypto: CryptoService) -> float:
    t0 = time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(select(bench_encrypted)).mappings().all()
    for r in rows:
        sid = str(r["id"])
        for field in FIELDS:
            crypto.decrypt(
                EncryptedValue(r[f"{field}_ct"], r[f"{field}_nonce"], crypto.key_version),
                sid,
                field,
            )
    return time.perf_counter() - t0


def median_seconds(fn) -> float:
    fn()  # Warmup run excluded from statistics
    return statistics.median(fn() for _ in range(REPEATS))


def payload_bytes(rows: list[dict]) -> int:
    return sum(
        len(v) if isinstance(v, bytes) else len(str(v).encode("utf-8"))
        for r in rows
        for k, v in r.items()
        if k != "id"
    )


def main() -> None:
    env = _load_config()
    engine = create_engine(env["DATABASE_URL"])
    crypto = CryptoService(
        decode_key(env["ENCRYPTION_KEY_B64"]),
        env.get("KEY_VERSION") or "v1",
    )

    meta = MetaData()
    bench_plain = Table(
        "bench_plain",
        meta,
        Column("id", Integer, primary_key=True),
        *[Column(f, String(255), nullable=False) for f in FIELDS],
    )
    bench_encrypted = Table(
        "bench_encrypted",
        meta,
        Column("id", Integer, primary_key=True),
        *[
            Column(f"{f}_{part}", LargeBinary, nullable=False)
            for f in FIELDS
            for part in ("ct", "nonce")
        ],
    )
    meta.create_all(engine)

    results = []
    for n in SIZES:
        for mode, table, make_rows, read_fn in (
            ("plain", bench_plain, plain_rows, lambda: run_read_plain(engine, bench_plain)),
            (
                "aes-gcm",
                bench_encrypted,
                lambda count: encrypted_rows(count, crypto),
                lambda: run_read_encrypted(engine, bench_encrypted, crypto),
            ),
        ):
            ins = median_seconds(lambda t=table, m=make_rows, count=n: run_insert(engine, t, m, count))
            rd = median_seconds(read_fn)
            results.append(
                {
                    "n": n,
                    "mode": mode,
                    "insert_seconds_median": round(ins, 6),
                    "read_seconds_median": round(rd, 6),
                    "payload_bytes": payload_bytes(make_rows(n)),
                }
            )
            print(results[-1])

    out_path = Path(__file__).resolve().parents[1] / "benchmark_results.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {out_path.name}")


if __name__ == "__main__":
    main()
