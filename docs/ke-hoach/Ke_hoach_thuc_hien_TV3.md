# Kế hoạch thực hiện – TV3: Security, Benchmark, CI & Trưởng nhóm kỹ thuật

> Nguồn: `Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx` (bản 4: việc của mỗi người làm và kiểm được độc lập; bản 3: nhóm tự viết mã nguồn).
> Nhánh: `sprint0/skeleton` (ngày 1–2), sau đó `feature/security-benchmark`. Thời gian: 4 tuần.
> Repo: https://github.com/world-ender1/database-encryption-lab (Private). Việc tạo repo và bật branch protection đã chuyển cho TV1 (chủ repo).
> Làm lần lượt từ Bước 1 đến Bước 23. Mỗi bước có điều kiện “Xong khi”; chưa đạt thì chưa sang bước sau.

---

## 1. Vai trò

TV3 có hai vai:

- **Kiểm chứng:** viết test bảo mật, chạy tấn công thử có kiểm soát (A1–A8), đo hiệu năng plain và AES-GCM, chuẩn bị minh chứng và kịch bản demo.
- **Trưởng nhóm kỹ thuật:** chủ trì họp Sprint 0, mở PR Sprint 0, giữ CI và README, nghiệm thu trên máy sạch, gắn tag `v1.0.0`. (Tạo repo và bật branch protection: TV1, vì chỉ chủ repo cá nhân mới sửa được Settings.)

Ngoài code, TV3 viết Chương 5 của báo cáo.

### File TV3 sở hữu (chỉ TV3 sửa)

| File | Nội dung |
|---|---|
| `README.md`, `.gitignore` | Hướng dẫn chạy; bỏ qua `.env`, venv, kết quả benchmark |
| `requirements.txt` | Thư viện cho cả dự án |
| `.github/workflows/tests.yml` | CI chạy pytest |
| `tests/__init__.py`, `scripts/__init__.py` | Đánh dấu package |
| `tests/conftest.py` | Fixture dùng chung (H5) |
| `tests/test_security.py` | 401/403, plaintext, tamper, tráo hàng, A8 |
| `scripts/attack_lab.py` | A1–A5 trên PostgreSQL thật, tự khôi phục |
| `scripts/benchmark.py` | Đo plain và AES-GCM |
| `docs/threat_model.md`, `docs/demo_script.md` | Threat model, kịch bản demo |

### Hợp đồng TV3 dùng

- **H1** (TV1): `CryptoService`, `decode_key` cho benchmark.
- **H2** (TV2): endpoint, status, `code` lỗi (`duplicate_student`, `integrity_failure`), A8 → 422, GET danh sách có hồ sơ hỏng → 409 kèm `student_ids`.
- **H3** (TV2): bảng `students` và tên cột `national_id_ct`, `national_id_nonce`, `phone_ct`, …, `key_version`.
- **H4** (TV2): biến `.env`; script của TV3 đọc `DATABASE_URL`, `API_PORT`, `ADMIN_TOKEN`, `VIEWER_TOKEN`, `ENCRYPTION_KEY_B64`.
- **H5**: TV3 là chủ phần fixture; TV2 là chủ `demo_client` (SV9001, SV9002).

### Cần gì từ người khác

| Cần gì | Từ ai | Khi nào |
|---|---|---|
| Khung có `require_admin`/`require_reader` gắn sẵn trên route | TV1, TV2 | Sprint 0 |
| Tên `app.database.Base`, `get_db`, `app.main.app`, `app.models.Student` (chốt trong H3/H5). `conftest.py` chỉ import chúng **trong fixture**, nên viết và push `conftest.py` không cần chờ file của TV2 | TV2 | Họp Sprint 0 (chốt tên) |
| API CRUD chạy thật | TV2 | Cuối tuần 2 (trước đó dùng `xfail`) |
| AES-GCM thật | TV1 | Cuối tuần 1–2 (trước đó dùng `xfail`) |

---

## 2. Lịch tổng quát

| Thời gian | Bước | Mốc |
|---|---|---|
| Ngày 1 (sáng) | 1 | Đã nhận lời mời collaborator, clone được repo của TV1, đang ở nhánh `sprint0/skeleton` |
| Ngày 1–2 (Sprint 0) | 2–6 | Họp chốt H1–H5; `requirements`, CI, `conftest`; PR Sprint 0 merge |
| Tuần 1 (ngày 3–7) | 7–9 | `threat_model.md`, `test_security.py` (xfail), khung `attack_lab` |
| Tuần 2 | 10–13 | `benchmark.py`, chạy thử trên nhánh `try/integration`, README, PR vòng 1 |
| Tuần 3 | 14–18 | Gỡ xfail, attack lab + benchmark trên PostgreSQL, minh chứng, nháp Chương 5 |
| Tuần 4 | 19–23 | `demo_script.md`, slide, nghiệm thu máy sạch, tag `v1.0.0`, tổng duyệt |

---

## 3. Các bước theo thứ tự

### Trước Sprint 0 (sáng ngày 1)

#### Bước 1. Nhận repo (việc tạo repo đã chuyển cho TV1)

TV1 đã tạo repo `world-ender1/database-encryption-lab` (Private), push `README.md` tạm và `.gitignore` lên `main`, tạo nhánh `sprint0/skeleton`, bật branch protection cho `main` (bắt buộc PR, 1 review). Từ đây `README.md` và `.gitignore` vẫn là file của TV3.

`.gitignore` hiện có trên repo:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
benchmark_results.csv
*.db
```

- [ ] Gửi TV1 tên tài khoản GitHub để được mời làm collaborator, rồi chấp nhận lời mời (email hoặc https://github.com/notifications).
- [ ] Clone và chuyển sang nhánh chung:

```bash
git clone https://github.com/world-ender1/database-encryption-lab.git
cd database-encryption-lab
git switch sprint0/skeleton
```

- [ ] Token GitHub dùng để push phải có scope `workflow` (cần cho `.github/workflows/tests.yml` ở Bước 4). Kiểm tra: `gh auth status`; thiếu thì `gh auth refresh -s workflow`.

**Xong khi:** đang ở nhánh `sprint0/skeleton` trên repo của TV1.

### Sprint 0 (ngày 1–2)

#### Bước 2. Chủ trì họp chốt hợp đồng

- [ ] Đi qua H1 (TV1), H2–H4 (TV2), H5 (TV3) và ghi lại vào một issue “Hợp đồng H1–H5”.
- [ ] Chốt danh sách thư viện (Bước 3).
- [ ] Chốt quy tắc: mỗi người chỉ push file của mình lên `sprint0/skeleton`; hạn push là trưa ngày 2.
- [ ] Chốt **thứ tự push** để không ai phải chờ: file không phụ thuộc ai được push ngay trong ngày 1 – TV1: 9 file (`key_manager`, `crypto_service` bản tạm, `auth`, `init_env`, `.env.example`, 4 file test; chạy được khi chưa có file của ai); TV3: `requirements.txt`, `tests.yml`, 2 file `__init__.py`, `conftest.py`. TV2 pull về rồi mới tự kiểm `/health`, vì `main.py` import `auth.py`, `Dockerfile` chép `requirements.txt`, `compose.yaml` cần `.env` do `init_env.py` sinh.
- [ ] Ghi vào H3/H5 các tên trong code mà `conftest.py` và `test_security.py` dùng: `app.database.Base`, `app.database.get_db`, `app.models.Student`, `app.main.app`.

#### Bước 3. `requirements.txt`

```text
# requirements.txt
fastapi
uvicorn[standard]
sqlalchemy>=2.0
psycopg[binary]
pydantic-settings
cryptography
httpx
pytest
```

Sau khi cả nhóm cài thử thành công, chốt phiên bản cụ thể: `python -m pip freeze`, rồi sửa từng dòng thành dạng `tên==phiên_bản` cho các gói trên. Từ đó mọi người cài cùng phiên bản.

#### Bước 4. `.github/workflows/tests.yml`

```yaml
# .github/workflows/tests.yml
name: tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest -q
```

CI chạy bằng SQLite trong bộ nhớ (qua `conftest.py`), không cần Docker.

#### Bước 5. `tests/__init__.py`, `scripts/__init__.py`, `tests/conftest.py`

Hai file `__init__.py` để trống. `conftest.py` ép cấu hình test **trước khi** import app, nên test không bao giờ chạm DB hay khóa thật. Code của app (`app.database`, `app.models`, `app.main` – file của TV2) chỉ được import **trong fixture**, không import ở đầu file: pytest nạp `conftest.py` cho mọi file test trong `tests/`, nên import ở đầu file sẽ bắt cả test của TV1 (không dùng API) phải chờ và phụ thuộc code của TV2. (Đã thử ngày 13/11/2026 với code dựng từ kế hoạch: import ở đầu file mà thiếu file của TV2 thì test của TV1 không chạy được test nào – `ModuleNotFoundError: No module named 'app.database'`; import trong fixture thì test của TV1 vẫn `43 passed, 3 xfailed`, còn khi đủ code kết quả giống hệt.)

```python
# tests/conftest.py
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
    """Một DB SQLite trong bộ nhớ cho mỗi test; app và test dùng chung session này."""
    # Import trong fixture: test không dùng fixture này (test của TV1) không cần code của TV2.
    import app.models  # noqa: F401  (đăng ký bảng students vào Base.metadata)
    from app.database import Base

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def viewer_headers():
    return {"Authorization": "Bearer test-viewer-token"}


@pytest.fixture
def sample_student():
    return {"student_id": "SV9001", "full_name": "Nguyen Van A", "major": "Computer Science",
            "national_id": "012345678901", "phone": "0901234567", "address": "Ha Noi (fictional)"}
```

- [ ] Fixture `db_session` tự `import app.models` trước `create_all`, nên bảng `students` luôn được tạo, dù file test có import model hay không.
- [ ] Kiểm tính độc lập: khi chưa có file nào của TV2, `python -m pytest tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py -q` (test của TV1) vẫn chạy, không có lỗi import từ `conftest.py`.

#### Bước 6. Mở PR Sprint 0 và merge

Push **ngay trong ngày 1**, không chờ ai (5 file này không import code của TV1, TV2 ở đầu file); TV2 cần `requirements.txt` để build Docker:

```bash
git add requirements.txt .github/workflows/tests.yml tests/__init__.py scripts/__init__.py tests/conftest.py
git commit -m "chore(ci): sprint 0 – requirements, CI, shared fixtures"
git pull --rebase origin sprint0/skeleton
git push origin sprint0/skeleton
```

- [ ] Khi TV1, TV2 đã push đủ, mở **một** PR `sprint0/skeleton` → `main`. Nếu PR Sprint 0 trễ, không ai phải ngồi chờ: mỗi người tạm tách nhánh của mình từ `sprint0/skeleton`, merge xong thì `git rebase origin/main`.
- [ ] CI xanh; cả ba review; merge trước hết ngày 2.
- [ ] Báo TV1 bật “Require status checks” cho `main` với job `pytest` (collaborator không sửa được Settings của repo cá nhân).

**Xong khi:** `main` có khung chạy được; trên máy mình `docker compose up -d --build` cho `/health` = 200.

### Tuần 1 (ngày 3–7)

#### Bước 7. Tạo nhánh và viết `docs/threat_model.md`

```bash
git switch main && git pull --ff-only origin main
git switch -c feature/security-benchmark
```

Dàn ý (dựa trên bảng 1.3 của tài liệu):

1. Tài sản cần bảo vệ: `national_id`, `phone`, `address`; khóa AES; token admin/viewer.
2. Kẻ tấn công: người có bản dump DB; người có quyền ghi DB; người gọi API không token hoặc với token viewer.
3. Bảng kịch bản A1–A8: mục tiêu, cách thử, kết quả mong đợi.
4. Những gì **không** bảo vệ: metadata (tên, ngành, số lượng bản ghi), máy ứng dụng hoặc khóa bị chiếm, replay cùng hàng (A7).

**Xong khi:** gửi file cho TV1 (dùng cho Chương 2).

#### Bước 8. `tests/test_security.py`

Test viết theo hợp đồng H2/H3. Phần nào phụ thuộc code chưa có trên `main` thì gắn `xfail(strict=False)`, đến tuần 3 gỡ ra (Bước 14).

```python
# tests/test_security.py
import pytest
from sqlalchemy import func, select

from app.models import Student

WAIT_API = pytest.mark.xfail(reason="chờ API CRUD của TV2 trên main", strict=False)
WAIT_AES = pytest.mark.xfail(reason="chờ AES-GCM của TV1 trên main", strict=False)


def _create(client, admin_headers, student):
    r = client.post("/students", json=student, headers=admin_headers)
    assert r.status_code == 201, r.text


def _count(db_session):
    return db_session.scalar(select(func.count()).select_from(Student))


# A1 – không có hoặc sai token (chạy được từ Sprint 0 vì route khung đã gắn auth)
def test_a1_missing_token_401(client):
    r = client.get("/students")
    assert r.status_code == 401
    assert r.headers.get("www-authenticate") == "Bearer"


def test_a1_wrong_token_401(client):
    assert client.get("/students", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_a2_viewer_cannot_write_403(client, viewer_headers, sample_student):
    assert client.post("/students", json=sample_student, headers=viewer_headers).status_code == 403
    assert client.delete("/students/SV9001", headers=viewer_headers).status_code == 403


@WAIT_API
def test_a2_viewer_delete_keeps_row(client, admin_headers, viewer_headers, sample_student):
    _create(client, admin_headers, sample_student)
    assert client.delete("/students/SV9001", headers=viewer_headers).status_code == 403
    assert client.get("/students/SV9001", headers=viewer_headers).status_code == 200


@WAIT_API
@WAIT_AES
def test_a3_db_has_no_plaintext(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    row = db_session.get(Student, "SV9001")
    for field in ("national_id", "phone", "address"):
        assert sample_student[field].encode() not in getattr(row, f"{field}_ct")


@WAIT_API
def test_a4_tampered_ciphertext_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    row = db_session.get(Student, "SV9001")
    ct = bytearray(row.national_id_ct)
    ct[0] ^= 0x01
    row.national_id_ct = bytes(ct)
    db_session.commit()
    r = client.get("/students/SV9001", headers=admin_headers)
    assert r.status_code == 409
    assert r.json()["code"] == "integrity_failure"
    r = client.get("/students", headers=admin_headers)
    assert r.status_code == 409
    assert r.json()["student_ids"] == ["SV9001"]


@WAIT_API
def test_a5_swapped_between_rows_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    _create(client, admin_headers, {**sample_student, "student_id": "SV9002",
                                    "national_id": "098765432109"})
    a = db_session.get(Student, "SV9001")
    b = db_session.get(Student, "SV9002")
    a.national_id_ct, a.national_id_nonce = b.national_id_ct, b.national_id_nonce
    db_session.commit()
    assert client.get("/students/SV9001", headers=admin_headers).status_code == 409


@WAIT_API
def test_a8_sql_like_id_422_and_db_unchanged(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    before = _count(db_session)
    r = client.get("/students/SV9001' OR '1'='1", headers=admin_headers)
    assert r.status_code == 422
    assert _count(db_session) == before
```

**Xong khi:** `python -m pytest -q` xanh trên nhánh của mình (các test `xfail` hiện `x` hoặc `X`, không đỏ).

#### Bước 9. Khung `scripts/attack_lab.py`

Chỉ chạy trên DB demo của nhóm. Mọi sửa đổi DB được khôi phục trong `finally`. Bảng được đọc bằng reflection theo tên H3, không import code của TV2.

```python
# scripts/attack_lab.py
"""A1–A5 trên DB demo của nhóm. Chạy từ thư mục gốc repo: python -m scripts.attack_lab"""
import httpx
from dotenv import dotenv_values
from sqlalchemy import MetaData, Table, create_engine, select, update

env = dotenv_values(".env")
API = f"http://127.0.0.1:{env.get('API_PORT') or '8000'}"
ADMIN = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}
VIEWER = {"Authorization": f"Bearer {env['VIEWER_TOKEN']}"}
PLAIN_NATIONAL_IDS = (b"012345678901", b"098765432109")   # CCCD giả trong demo_client

engine = create_engine(env["DATABASE_URL"])
students = Table("students", MetaData(), autoload_with=engine)
SV9001 = students.c.student_id == "SV9001"
SV9002 = students.c.student_id == "SV9002"


def status(method: str, path: str, headers=None) -> int:
    return httpx.request(method, API + path, headers=headers, timeout=10).status_code


def a1() -> None:
    print("[A1] Missing bearer token ->", status("GET", "/students/SV9001"))


def a2() -> None:
    code = status("DELETE", "/students/SV9001", VIEWER)
    print("[A2] Viewer attempts DELETE ->", code,
          "| row still there:", status("GET", "/students/SV9001", ADMIN) == 200)


def a3(conn) -> None:
    cts = conn.execute(select(students.c.national_id_ct)).scalars().all()
    leaked = any(p in ct for ct in cts for p in PLAIN_NATIONAL_IDS)
    print("[A3] DB contains ciphertext, not the plaintext:", not leaked)


def a4(conn) -> None:
    original = conn.execute(select(students.c.national_id_ct).where(SV9001)).scalar_one()
    try:
        tampered = bytes([original[0] ^ 0x01]) + original[1:]
        conn.execute(update(students).where(SV9001).values(national_id_ct=tampered))
        conn.commit()
        print("[A4] Tampered 1 ciphertext byte ->", status("GET", "/students/SV9001", ADMIN))
    finally:
        conn.rollback()
        conn.execute(update(students).where(SV9001).values(national_id_ct=original))
        conn.commit()


def a5(conn) -> None:
    cols = (students.c.national_id_ct, students.c.national_id_nonce)
    orig = conn.execute(select(*cols).where(SV9001)).one()
    other = conn.execute(select(*cols).where(SV9002)).one()
    try:
        conn.execute(update(students).where(SV9001)
                     .values(national_id_ct=other[0], national_id_nonce=other[1]))
        conn.commit()
        print("[A5] Swapped fields between students ->", status("GET", "/students/SV9001", ADMIN))
    finally:
        conn.rollback()
        conn.execute(update(students).where(SV9001)
                     .values(national_id_ct=orig[0], national_id_nonce=orig[1]))
        conn.commit()


def main() -> None:
    a1()
    a2()
    with engine.connect() as conn:
        a3(conn)
        a4(conn)
        a5(conn)
    print("[Restore] legitimate read ->", status("GET", "/students/SV9001", ADMIN))


if __name__ == "__main__":
    main()
```

Kết quả mong đợi khi chạy trên hệ thống hoàn chỉnh: `A1 → 401`, `A2 → 403 | row still there: True`, `A3 → True`, `A4 → 409`, `A5 → 409`, `Restore → 200`.

**Xong khi:** file chạy được cú pháp (`python -m py_compile scripts/attack_lab.py`); chạy thật ở Bước 11.

### Tuần 2

#### Bước 10. `scripts/benchmark.py`

Đo thẳng DB qua SQLAlchemy, **không qua HTTP**. `insert` = (mã hóa nếu có) + INSERT + commit; `read` = SELECT + (giải mã nếu có). Chạy khởi động 1 lần không tính, rồi lấy trung vị 3 lần.

```python
# scripts/benchmark.py
"""Đo lưu plain và AES-GCM. Chạy: python -m scripts.benchmark → benchmark_results.csv"""
import csv
import statistics
import time

from dotenv import dotenv_values
from sqlalchemy import (Column, Integer, LargeBinary, MetaData, String, Table, create_engine,
                        delete, insert, select)

from app.crypto_service import CryptoService, EncryptedValue
from app.key_manager import decode_key

SIZES = (100, 1_000, 10_000)
REPEATS = 3
FIELDS = ("national_id", "phone", "address")
SAMPLE = {"national_id": "012345678901", "phone": "0901234567", "address": "Ha Noi (fictional)"}

env = dotenv_values(".env")
engine = create_engine(env["DATABASE_URL"])
crypto = CryptoService(decode_key(env["ENCRYPTION_KEY_B64"]), env.get("KEY_VERSION") or "v1")

meta = MetaData()
bench_plain = Table("bench_plain", meta, Column("id", Integer, primary_key=True),
                    *[Column(f, String(255), nullable=False) for f in FIELDS])
bench_encrypted = Table("bench_encrypted", meta, Column("id", Integer, primary_key=True),
                        *[Column(f"{f}_{part}", LargeBinary, nullable=False)
                          for f in FIELDS for part in ("ct", "nonce")])


def plain_rows(n):
    return [{"id": i, **SAMPLE} for i in range(n)]


def encrypted_rows(n):
    rows = []
    for i in range(n):
        row = {"id": i}
        for f in FIELDS:
            ev = crypto.encrypt(SAMPLE[f], str(i), f)
            row[f"{f}_ct"], row[f"{f}_nonce"] = ev.ciphertext, ev.nonce
        rows.append(row)
    return rows


def run_insert(table, make_rows, n):
    with engine.begin() as conn:
        conn.execute(delete(table))                 # dọn bảng: không tính giờ
    t0 = time.perf_counter()
    with engine.begin() as conn:
        conn.execute(insert(table), make_rows(n))   # tạo dữ liệu (và mã hóa) nằm trong giờ đo
    return time.perf_counter() - t0


def run_read_plain():
    t0 = time.perf_counter()
    with engine.connect() as conn:
        conn.execute(select(bench_plain)).all()
    return time.perf_counter() - t0


def run_read_encrypted():
    t0 = time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(select(bench_encrypted)).mappings().all()
    for r in rows:
        for f in FIELDS:
            crypto.decrypt(EncryptedValue(r[f"{f}_ct"], r[f"{f}_nonce"], crypto.key_version),
                           str(r["id"]), f)
    return time.perf_counter() - t0


def median_seconds(run):
    run()                                            # khởi động, không tính
    return statistics.median(run() for _ in range(REPEATS))


def payload_bytes(rows):
    return sum(len(v) if isinstance(v, bytes) else len(str(v).encode("utf-8"))
               for r in rows for k, v in r.items() if k != "id")


def main() -> None:
    meta.create_all(engine)
    results = []
    for n in SIZES:
        for mode, table, make_rows, read in (
            ("plain", bench_plain, plain_rows, run_read_plain),
            ("aes-gcm", bench_encrypted, encrypted_rows, run_read_encrypted),
        ):
            ins = median_seconds(lambda: run_insert(table, make_rows, n))
            rd = median_seconds(read)                # bảng đang có đúng n dòng
            results.append({"n": n, "mode": mode, "insert_seconds_median": round(ins, 6),
                            "read_seconds_median": round(rd, 6),
                            "payload_bytes": payload_bytes(make_rows(n))})
            print(results[-1])
    with open("benchmark_results.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
```

- [ ] Công thức overhead: `(T_aes - T_plain) / T_plain × 100%`. Overhead âm ở mẫu nhỏ là nhiễu đo, không kết luận “mã hóa làm nhanh hơn”.
- [ ] `payload_bytes` chỉ là dữ liệu 3 trường; không phải kích thước vật lý của bảng PostgreSQL.

#### Bước 11. Chạy thử trên nhánh `try/integration`

Dùng code chưa merge của TV1, TV2 để thử sớm. Nhánh `try/*` **không push**, xóa khi xong.

```bash
git add tests/test_security.py scripts/attack_lab.py scripts/benchmark.py
git commit -m "test(security): security tests, attack lab, benchmark"
git fetch origin
git switch -c try/integration
git merge origin/feature/crypto origin/feature/api-db
docker compose up -d --build
python -m scripts.demo_client --reset
python -m scripts.attack_lab
python -m scripts.benchmark
git switch feature/security-benchmark
git branch -D try/integration
```

- [ ] Ghi lại lỗi phát hiện được thành issue cho đúng chủ file (TV1 hoặc TV2).

#### Bước 12. `README.md`

1. Dự án làm gì (3–4 câu).
2. Cài đặt: Python 3.12, Docker; tạo venv; `pip install -r requirements.txt`.
3. Chạy: `python scripts/init_env.py` → `docker compose up -d --build` → `http://127.0.0.1:8000/docs` → `python -m scripts.demo_client`.
4. Kiểm tra: `python -m pytest -q`, `python -m scripts.attack_lab`, `python -m scripts.benchmark`.
5. Cách xem ciphertext bằng `psql`.
6. Trỏ tới `docs/crypto_design.md`, `docs/api_db.md`, `docs/threat_model.md`, `docs/demo_script.md`.
7. Cảnh báo: không commit `.env`; không chạy lại `init_env.py` khi DB còn dữ liệu.

#### Bước 13. Mở PR vòng 1 và review

```bash
python -m pytest -q
git add README.md docs/threat_model.md
git status                   # không có benchmark_results.csv, không có .env
git commit -m "docs: README and threat model"
git push -u origin feature/security-benchmark
```

- [ ] Gán TV2 review.
- [ ] Review PR `feature/api-db` của TV2 (cùng TV1): status và `code` lỗi đúng H2; tên cột đúng H3.

**Xong khi:** cả ba PR vòng 1 đã merge (cuối tuần 2).

### Tuần 3

#### Bước 14. Gỡ xfail

```bash
git switch main && git pull --ff-only origin main
git switch -c feature/security-round2
```

- [ ] Xóa `@WAIT_API`, `@WAIT_AES` và hai dòng định nghĩa chúng.
- [ ] `python -m pytest -q` phải xanh hoàn toàn, không còn `x`/`X`.
- [ ] Test nào đỏ: mở issue cho chủ file, đính kèm lệnh tái hiện.

#### Bước 15. Attack lab trên PostgreSQL thật và nhật ký

```bash
docker compose up -d --build
python -m scripts.demo_client --reset
python -m scripts.attack_lab
```

- [ ] Điền cột “Actual” trong nhật ký thực nghiệm mục 8.7 cho A1–A8 (A6, A7 lấy kết quả C03, C07 của TV1; A8 lấy kết quả `test_security`).
- [ ] Chụp ảnh: A1=401, A2=403, A4=409, A5=409, Restore=200; `psql` hiển thị hex; Swagger POST 201 và GET dữ liệu rõ; pytest summary; GitHub Actions xanh. Che token và key.

#### Bước 16. Benchmark thật

```bash
python -m scripts.benchmark
```

- [ ] Ghi cấu hình máy (CPU, RAM, OS, phiên bản Docker, PostgreSQL 17).
- [ ] Vẽ 2 biểu đồ theo n: thời gian INSERT, thời gian SELECT (plain và AES-GCM); thêm bảng `payload_bytes`.
- [ ] Không commit `benchmark_results.csv`; đưa số liệu vào báo cáo.

#### Bước 17. PR vòng 2

```bash
git add tests/test_security.py
git commit -m "test(security): remove xfail after integration"
git push -u origin feature/security-round2
```

#### Bước 18. Nháp Chương 5

- [ ] Unit/API/security test: bảng test case, kết quả.
- [ ] Attack lab: nhật ký expected/actual, ảnh minh chứng.
- [ ] Benchmark: cấu hình máy, biểu đồ, overhead, thảo luận nhiễu đo.
- [ ] Gửi TV1 trước cuối tuần 3 để ghép báo cáo.

### Tuần 4

#### Bước 19. `docs/demo_script.md`

Theo timeline 12 phút ở mục 9.2:

| Thời lượng | Người | Nội dung |
|---|---|---|
| 0:00–2:00 | TV1 | AES-GCM, key/nonce/tag/AAD, sơ đồ kiến trúc |
| 2:00–5:00 | TV2 | Swagger POST/GET, `psql` thấy ciphertext |
| 5:00–8:00 | TV3 | `attack_lab`: 401/403/409/restore |
| 8:00–10:00 | TV3 | Benchmark CSV + biểu đồ |
| 10:00–12:00 | Cả nhóm | Giới hạn, kết luận, hỏi đáp |

Ghi rõ câu thoại, lệnh sẽ chạy, ảnh dự phòng nếu máy hoặc DB lỗi.

#### Bước 20. Slide phần tấn công và benchmark

- [ ] Ma trận A1–A8 với kết quả thật; nói rõ A7 là giới hạn.
- [ ] 2 biểu đồ benchmark và bảng overhead.
- [ ] Gửi TV1 để ghép bộ slide chung.

#### Bước 21. Nghiệm thu trên máy sạch

```bash
git clone https://github.com/world-ender1/database-encryption-lab.git /tmp/clean-check
cd /tmp/clean-check
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/init_env.py
docker compose up -d --build
python -m scripts.demo_client
python -m pytest -q
python -m scripts.attack_lab
python -m scripts.benchmark
```

- [ ] Làm đúng theo README, không dùng kiến thức ngoài README. Bước nào phải đoán thì sửa README.
- [ ] Máy sạch dùng cổng mặc định; nếu đang chạy bản khác thì `docker compose down` bản đó trước.

#### Bước 22. Gắn tag release

```bash
git switch main && git pull --ff-only origin main
python -m pytest -q
git tag -a v1.0.0 -m "University database encryption demo release"
git push origin v1.0.0
```

#### Bước 23. Tổng duyệt

- [ ] Chuẩn bị máy demo theo mục 9.1: Docker chạy sẵn, `demo_client` đã chạy, terminal thứ hai mở `psql`, tắt thông báo, không mở `.env`.
- [ ] Cả nhóm chạy demo 12 phút; TV3 bấm giờ.

---

## 4. Definition of Done – TV3

**Phần TV3 tự kiểm được, không cần ai** (dùng code trên `main` từ Sprint 0, phần chờ người khác gắn `xfail`):

- [ ] `conftest.py` chỉ import code app trong fixture; test của TV1 chạy được khi chưa có file của TV2 (Bước 5).
- [ ] `test_security.py` chạy xanh trên nhánh của mình (test chờ người khác hiện `x`/`X`, không đỏ).
- [ ] `attack_lab.py` và `benchmark.py` chạy được trên DB demo (với bản crypto tạm số liệu chưa có ý nghĩa, chỉ kiểm script chạy đúng và `attack_lab` khôi phục dữ liệu).
- [ ] Workflow CI chạy trên PR; `threat_model.md` xong từ tuần 1; `demo_script.md` diễn giải cả thành công và giới hạn.

**Nghiệm thu chung** (cần code của cả nhóm trên `main`, mốc tuần 3–4; TV3 chủ trì nhưng không phải việc riêng của TV3):

- [ ] `python -m pytest -q` xanh, không còn `xfail`.
- [ ] `attack_lab` cho A1=401, A2=403, A3=True, A4=409, A5=409 và khôi phục dữ liệu (Restore=200).
- [ ] `benchmark_results.csv` từ số đo thật với AES-GCM, có biểu đồ và cấu hình máy.
- [ ] CI xanh trên `main`; branch protection (do TV1 bật) có yêu cầu CI pass.
- [ ] `README.md` chạy được trên máy sạch; tag `v1.0.0` đã gắn.

## 5. Rủi ro

| Rủi ro | Dấu hiệu | Cách xử lý |
|---|---|---|
| Test chạm DB/khóa thật | Test làm đổi dữ liệu demo | `conftest.py` ép `DATABASE_URL=sqlite://` trước khi import app |
| Code của TV2 lỗi import trên một nhánh làm hỏng test của cả repo | Mọi file test (kể cả test mật mã của TV1) báo `ERROR` lúc nạp `conftest.py` | `conftest.py` chỉ import `app.*` trong fixture (Bước 5); test không dùng fixture API không bị ảnh hưởng |
| Attack lab dừng giữa chừng | SV9001 còn ciphertext hỏng | `finally` khôi phục; nếu vẫn hỏng: `python -m scripts.demo_client --reset` |
| Viewer xóa được (lỗi phân quyền) | A2 trả 204 | Báo TV1 ngay; tạo lại dữ liệu bằng `demo_client` |
| TV2 đổi tên cột | `attack_lab` lỗi `KeyError`/`NoSuchColumnError` | H3 đã đóng băng; đổi phải qua issue |
| Benchmark nhiễu | Overhead âm hoặc dao động lớn | Tắt ứng dụng nặng, chạy lại; báo cáo trung vị và nêu nhiễu |
| Vai trưởng nhóm làm chậm phần kiểm thử | Tuần 3 dồn việc | Làm attack lab, benchmark trên `try/integration` từ tuần 2 |
