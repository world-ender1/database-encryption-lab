# Kế hoạch thực hiện – TV2: PostgreSQL, API & Docker

> Nguồn: `Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx` (bản 4: việc của mỗi người làm và kiểm được độc lập; bản 3: nhóm tự viết mã nguồn).
> Nhánh: `sprint0/skeleton` (ngày 1–2), sau đó `feature/api-db`. Thời gian: 4 tuần.
> Làm lần lượt từ Bước 1 đến Bước 23. Mỗi bước có điều kiện “Xong khi”; chưa đạt thì chưa sang bước sau.

---

## 1. Vai trò

TV2 dựng phần “thân” của hệ thống: cấu hình, database, API CRUD, Docker. API nhận dữ liệu rõ, gọi `CryptoService` của TV1 để mã hóa 3 trường nhạy cảm, lưu ciphertext vào PostgreSQL và giải mã khi người có quyền đọc. TV2 không tự viết mã hóa và không tự viết kiểm tra token: hai phần đó lấy từ TV1 qua hợp đồng H1. Ngoài code, TV2 viết Chương 3–4 của báo cáo.

### File TV2 sở hữu (chỉ TV2 sửa)

| File | Nội dung |
|---|---|
| `app/__init__.py`, `app/config.py` | Đọc biến môi trường H4 |
| `app/database.py` | Engine, `SessionLocal`, `Base`, `get_db` |
| `app/models.py` | Bảng `students` (H3) |
| `app/schemas.py` | `StudentPayload`, `StudentUpdate`, `StudentOut` |
| `app/dependencies.py` | `get_crypto()` tạo `CryptoService` dùng chung |
| `app/student_service.py` | Chuyển payload ↔ ciphertext |
| `app/main.py` | Route CRUD, `/health`, định dạng lỗi |
| `app/init_db.py`, `Dockerfile`, `compose.yaml` | Tạo bảng, chạy DB + API |
| `scripts/demo_client.py` | Tạo SV9001, SV9002 qua API |
| `tests/test_api.py` | Test CRUD và status |
| `docs/api_db.md` | Tài liệu cấu hình, schema, endpoint |

### Hợp đồng liên quan

- **TV2 là chủ:** H2 (API), H3 (schema DB), H4 (cấu hình `.env`), một phần H5 (`demo_client`).
- **TV2 dùng:** H1 của TV1 (`decode_key`, `CryptoService`, `IntegrityFailure`, `require_admin`, `require_reader`), fixture trong `tests/conftest.py` của TV3.

**H2 – API**

| HTTP | Endpoint | Quyền | Đầu ra |
|---|---|---|---|
| GET | `/health` | Không cần token | 200 |
| POST | `/students` | admin | 201 + dữ liệu đã giải mã; trùng mã → 409 `duplicate_student` |
| GET | `/students` | admin/viewer | 200 + danh sách; có hồ sơ hỏng → 409 cả danh sách |
| GET | `/students/{student_id}` | admin/viewer | 200, 404, hoặc 409 `integrity_failure` |
| PUT | `/students/{student_id}` | admin | 200 (body `StudentUpdate`, không có `student_id`) |
| DELETE | `/students/{student_id}` | admin | 204 |

Quy ước chung: thiếu/sai token → 401 (do `auth.py` của TV1); viewer ghi → 403; `student_id` sai mẫu `^[A-Za-z0-9]{1,16}$` → 422; lỗi 409 có body `{"detail": ..., "code": ...}`.

### Cần gì từ người khác

| Cần gì | Từ ai | Khi nào |
|---|---|---|
| `decode_key`, `CryptoService` (bản tạm), `require_admin`, `require_reader`, `scripts/init_env.py` | TV1 | Ngày 1: TV1 push 9 file ngay (chạy được khi chưa có file của ai), trước khi TV2 tự kiểm `/health` |
| `requirements.txt` có `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg[binary]`, `pydantic-settings`, `httpx` | TV3 | Ngày 1: TV3 push ngay (không phụ thuộc ai) |
| Fixture `client`, `admin_headers`, `viewer_headers`, `sample_student` | TV3 | Sprint 0 |
| AES-GCM thật | TV1 | Không cần chờ; dùng bản tạm tới khi TV1 merge |

---

## 2. Lịch tổng quát

| Thời gian | Bước | Mốc |
|---|---|---|
| Ngày 1–2 (Sprint 0) | 1–9 | Khung + Docker trên `sprint0/skeleton`; `/health` = 200; PR Sprint 0 merge |
| Tuần 1 (ngày 3–7) | 10–13 | `student_service`, POST, GET một hồ sơ, GET danh sách; review PR crypto |
| Tuần 2 | 14–18 | PUT, DELETE, `demo_client`, `test_api`, `api_db.md`; PR api-db merge |
| Tuần 3 | 19–21 | Kiểm tra DB thật sau khi có AES-GCM, sửa lỗi, nháp Chương 3–4 |
| Tuần 4 | 22–23 | Slide hệ thống, demo Swagger, tổng duyệt |

---

## 3. Các bước theo thứ tự

### Sprint 0 (ngày 1–2)

#### Bước 1. Họp chốt hợp đồng (cả nhóm, TV3 chủ trì)

- [ ] Trình bày H2 (bảng trên), H3 (schema ở Bước 4), H4 (tên biến `.env`).
- [ ] Chốt với TV1: `config.py` cung cấp `get_settings()`, field viết thường `database_url`, `encryption_key_b64`, `key_version`, `admin_token`, `viewer_token`. `auth.py` của TV1 chỉ dùng hai field token, gọi `get_settings()` khi chạy (qua `get_token_settings()`), không import `config.py` lúc import – TV1 không chờ file này.
- [ ] Chốt `DATABASE_URL` cho script trên máy: `postgresql+psycopg://demo:<POSTGRES_PASSWORD>@127.0.0.1:<DB_PORT>/encryption_demo`.
- [ ] Chốt với TV3: fixture trong `conftest.py` override `get_db` của `app.database`. Ghi vào H3/H5 các **tên trong code** mà TV3 dùng, sau Sprint 0 không đổi nếu chưa qua issue: `app.database.Base`, `app.database.get_db`, `app.models.Student`, `app.main.app`.
- [ ] Chốt thứ tự push Sprint 0: TV1 và TV3 push phần không phụ thuộc ai ngay ngày 1; TV2 pull về rồi mới tự kiểm `/health` (Bước 9).

**Xong khi:** H1–H5 được ghi lại và cả ba đồng ý.

#### Bước 2. Lấy repo và chuyển sang nhánh chung

Repo do TV1 tạo. Gửi TV1 tên tài khoản GitHub, chấp nhận lời mời collaborator, rồi:

```bash
git clone https://github.com/world-ender1/database-encryption-lab.git
cd database-encryption-lab
git switch sprint0/skeleton
```

#### Bước 3. `app/__init__.py` và `app/config.py`

`app/__init__.py` để trống. `config.py`:

```python
# app/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    encryption_key_b64: str
    key_version: str = "v1"
    admin_token: str
    viewer_token: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Biến môi trường thật luôn được ưu tiên hơn giá trị trong `.env`. Nhờ vậy `compose.yaml` ghi đè được `DATABASE_URL` cho container, và `conftest.py` của TV3 ép được cấu hình test.

**Xong khi:** `python -c "from app.config import get_settings; print(get_settings().key_version)"` in ra `v1` (sau khi đã có `.env`).

#### Bước 4. `app/database.py` và `app/models.py`

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# app/models.py
from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    major: Mapped[str] = mapped_column(String(100))
    national_id_ct: Mapped[bytes] = mapped_column(LargeBinary)
    national_id_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    phone_ct: Mapped[bytes] = mapped_column(LargeBinary)
    phone_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    address_ct: Mapped[bytes] = mapped_column(LargeBinary)
    address_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    key_version: Mapped[str] = mapped_column(String(20))
```

`LargeBinary` thành `BYTEA` trên PostgreSQL. Sau Sprint 0 **không đổi tên bảng hay tên cột** (H3): `attack_lab.py` của TV3 đọc thẳng các cột này.

#### Bước 5. `app/schemas.py`

```python
# app/schemas.py
from pydantic import BaseModel, ConfigDict, Field

STUDENT_ID_PATTERN = r"^[A-Za-z0-9]{1,16}$"


class StudentUpdate(BaseModel):
    """Body của PUT: không có student_id. Gửi kèm student_id → 422 (extra=forbid)."""
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=150)
    major: str = Field(min_length=1, max_length=100)
    national_id: str = Field(min_length=1, max_length=32)
    phone: str = Field(min_length=1, max_length=32)
    address: str = Field(min_length=1, max_length=255)


class StudentPayload(StudentUpdate):
    """Body của POST."""
    student_id: str = Field(pattern=STUDENT_ID_PATTERN)


class StudentOut(StudentPayload):
    """Dữ liệu trả về sau khi giải mã."""
```

#### Bước 6. `app/dependencies.py`

```python
# app/dependencies.py
from functools import lru_cache

from app.config import get_settings
from app.crypto_service import CryptoService
from app.key_manager import decode_key


@lru_cache
def get_crypto() -> CryptoService:
    settings = get_settings()
    return CryptoService(decode_key(settings.encryption_key_b64), settings.key_version)
```

#### Bước 7. `app/main.py` – khung

Route CRUD tạm trả 501, nhưng **gắn sẵn `require_admin`/`require_reader`**. Nhờ vậy test 401/403 của TV3 đã chạy được ngay từ Sprint 0.

```python
# app/main.py  (KHUNG SPRINT 0)
from fastapi import Depends, FastAPI, HTTPException

from app.auth import require_admin, require_reader

app = FastAPI(title="Database Encryption Demo")


def _todo():
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/students", status_code=201, dependencies=[Depends(require_admin)])
def create_student():
    _todo()


@app.get("/students", dependencies=[Depends(require_reader)])
def list_students():
    _todo()


@app.get("/students/{student_id}", dependencies=[Depends(require_reader)])
def get_student(student_id: str):
    _todo()


@app.put("/students/{student_id}", dependencies=[Depends(require_admin)])
def update_student(student_id: str):
    _todo()


@app.delete("/students/{student_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_student(student_id: str):
    _todo()
```

#### Bước 8. `app/init_db.py`, `Dockerfile`, `compose.yaml`

```python
# app/init_db.py
from app import models  # noqa: F401  (đăng ký bảng vào Base.metadata)
from app.database import Base, engine


def main() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

```yaml
# compose.yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?run scripts/init_env.py first}
      POSTGRES_DB: encryption_demo
    ports:
      - "127.0.0.1:${DB_PORT:-55432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U demo -d encryption_demo"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    env_file: .env
    environment:
      # Ghi đè DATABASE_URL của .env: trong mạng Docker, DB tên là "db", cổng 5432
      DATABASE_URL: postgresql+psycopg://demo:${POSTGRES_PASSWORD}@db:5432/encryption_demo
    ports:
      - "127.0.0.1:${API_PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

- Docker Compose tự đọc `.env` ở thư mục gốc để thay `${...}`; `environment:` ưu tiên hơn `env_file:`.
- Mọi cổng chỉ bind `127.0.0.1`. Ai trùng cổng thì đổi `API_PORT`/`DB_PORT` trong `.env` của mình, không sửa file này.

#### Bước 9. Tự kiểm tra và push lên nhánh chung

Bước 3–8 viết được mà không cần file của ai. Riêng lần tự kiểm `/health` cần 3 file của người khác đã có trên nhánh chung từ ngày 1: `app/auth.py` của TV1 (`main.py` import), `scripts/init_env.py` của TV1 (sinh `.env` cho `compose.yaml`), `requirements.txt` của TV3 (`Dockerfile` chép). Lấy về trước khi kiểm; **không** tự viết hay chép các file này.

```bash
git pull --rebase origin sprint0/skeleton   # lấy file TV1, TV3 đã push ngày 1
python scripts/init_env.py           # file của TV1, chỉ chạy nếu chưa có .env
docker compose up -d --build
docker compose ps                    # db: healthy, api: running
curl http://127.0.0.1:8000/health    # {"status":"ok"}
git add app/__init__.py app/config.py app/database.py app/models.py app/schemas.py
git add app/dependencies.py app/main.py app/init_db.py Dockerfile compose.yaml
git status                           # chỉ file của TV2, không có .env
git commit -m "chore(api): sprint 0 skeleton – config, schema, docker"
git pull --rebase origin sprint0/skeleton
git push origin sprint0/skeleton
```

- [ ] Review PR Sprint 0 do TV3 mở.

**Xong khi:** PR Sprint 0 merge vào `main` trước hết ngày 2; trên `main`, `docker compose up` cho `/health` = 200.

### Tuần 1 (ngày 3–7)

#### Bước 10. Tạo nhánh và viết `app/student_service.py`

```bash
git switch main && git pull --ff-only origin main
git switch -c feature/api-db
```

```python
# app/student_service.py
from app.crypto_service import CryptoService, EncryptedValue
from app.models import Student
from app.schemas import StudentOut, StudentUpdate

SENSITIVE_FIELDS = ("national_id", "phone", "address")


def apply_sensitive(row: Student, data: StudentUpdate, crypto: CryptoService) -> None:
    """Mã hóa 3 trường nhạy cảm vào row. Mỗi lần gọi sinh nonce mới."""
    for field in SENSITIVE_FIELDS:
        ev = crypto.encrypt(getattr(data, field), row.student_id, field)
        setattr(row, f"{field}_ct", ev.ciphertext)
        setattr(row, f"{field}_nonce", ev.nonce)
    row.key_version = crypto.key_version


def to_out(row: Student, crypto: CryptoService) -> StudentOut:
    """Giải mã row. Dữ liệu hỏng: IntegrityFailure lan ra ngoài cho main.py xử lý."""
    values = {
        field: crypto.decrypt(
            EncryptedValue(getattr(row, f"{field}_ct"), getattr(row, f"{field}_nonce"),
                           row.key_version),
            row.student_id, field)
        for field in SENSITIVE_FIELDS
    }
    return StudentOut(student_id=row.student_id, full_name=row.full_name, major=row.major, **values)
```

- [ ] Tên field truyền vào encrypt và decrypt phải giống hệt nhau (H1).
- [ ] Không gọi `AESGCM`, không tự sinh nonce ở đây.

#### Bước 11. Định dạng lỗi, POST và GET một hồ sơ

Thay `main.py` khung bằng bản thật. Cẩn thận hai thứ tên gần giống nhau: `IntegrityFailure` (của TV1, giải mã thất bại) và `sqlalchemy.exc.IntegrityError` (DB báo trùng khóa).

```python
# app/main.py
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as DBIntegrityError
from sqlalchemy.orm import Session

from app.auth import require_admin, require_reader
from app.crypto_service import CryptoService, IntegrityFailure
from app.database import get_db
from app.dependencies import get_crypto
from app.models import Student
from app.schemas import STUDENT_ID_PATTERN, StudentOut, StudentPayload, StudentUpdate
from app.student_service import apply_sensitive, to_out

app = FastAPI(title="Database Encryption Demo")

StudentIdPath = Annotated[str, Path(pattern=STUDENT_ID_PATTERN)]
DB = Annotated[Session, Depends(get_db)]
Crypto = Annotated[CryptoService, Depends(get_crypto)]


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, detail: str, **extra):
        self.status_code, self.code, self.detail, self.extra = status_code, code, detail, extra


@app.exception_handler(ApiError)
def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.detail, "code": exc.code, **exc.extra})


def _get_or_404(db: Session, student_id: str) -> Student:
    row = db.get(Student, student_id)
    if row is None:
        raise ApiError(404, "not_found", "Student not found")
    return row


def _decrypt_or_409(row: Student, crypto: CryptoService) -> StudentOut:
    try:
        return to_out(row, crypto)
    except IntegrityFailure:
        raise ApiError(409, "integrity_failure", "Encrypted data failed authentication",
                       student_ids=[row.student_id]) from None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/students", status_code=201, response_model=StudentOut,
          dependencies=[Depends(require_admin)])
def create_student(payload: StudentPayload, db: DB, crypto: Crypto):
    if db.get(Student, payload.student_id) is not None:
        raise ApiError(409, "duplicate_student", "Student already exists")
    row = Student(student_id=payload.student_id, full_name=payload.full_name, major=payload.major)
    apply_sensitive(row, payload, crypto)
    db.add(row)
    try:
        db.commit()
    except DBIntegrityError:
        db.rollback()
        raise ApiError(409, "duplicate_student", "Student already exists") from None
    return _decrypt_or_409(row, crypto)


@app.get("/students/{student_id}", response_model=StudentOut,
         dependencies=[Depends(require_reader)])
def get_student(student_id: StudentIdPath, db: DB, crypto: Crypto):
    return _decrypt_or_409(_get_or_404(db, student_id), crypto)
```

- [ ] Không ghi plaintext hay token vào log.
- [ ] Truy vấn chỉ qua ORM (`db.get`, `select`), không ghép chuỗi SQL.

**Xong khi:** qua Swagger (`/docs`), POST SV9001 trả 201; POST lại trả 409 `duplicate_student`; GET SV9001 trả 200; GET SV9999 trả 404.

#### Bước 12. GET danh sách

Có hồ sơ không giải mã được thì trả 409 cho **cả danh sách** (thà không trả gì còn hơn trả dữ liệu sai):

```python
# app/main.py  (thêm)
@app.get("/students", response_model=list[StudentOut], dependencies=[Depends(require_reader)])
def list_students(db: DB, crypto: Crypto):
    rows = db.scalars(select(Student).order_by(Student.student_id)).all()
    out, failed = [], []
    for row in rows:
        try:
            out.append(to_out(row, crypto))
        except IntegrityFailure:
            failed.append(row.student_id)
    if failed:
        raise ApiError(409, "integrity_failure", "Encrypted data failed authentication",
                       student_ids=failed)
    return out
```

#### Bước 13. Review PR crypto của TV1

- [ ] Chữ ký H1 không đổi so với Sprint 0.
- [ ] Mọi lỗi giải mã đều thành `IntegrityFailure` (không lọt `InvalidTag` hay `ValueError` ra ngoài).
- [ ] Không log key.

**Xong khi:** đã approve hoặc để lại nhận xét trên PR crypto.

### Tuần 2

#### Bước 14. PUT và DELETE

```python
# app/main.py  (thêm)
@app.put("/students/{student_id}", response_model=StudentOut,
         dependencies=[Depends(require_admin)])
def update_student(student_id: StudentIdPath, payload: StudentUpdate, db: DB, crypto: Crypto):
    row = _get_or_404(db, student_id)
    row.full_name, row.major = payload.full_name, payload.major
    apply_sensitive(row, payload, crypto)   # mã hóa lại cả 3 trường, nonce mới
    db.commit()
    return _decrypt_or_409(row, crypto)


@app.delete("/students/{student_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_student(student_id: StudentIdPath, db: DB) -> None:
    db.delete(_get_or_404(db, student_id))
    db.commit()
```

DELETE không giải mã, nên xóa được cả hồ sơ đã hỏng (dùng khi dọn dữ liệu tạo bằng bản crypto tạm).

**Xong khi:** PUT đổi địa chỉ trả 200; PUT có `student_id` trong body trả 422; DELETE trả 204, GET lại trả 404.

#### Bước 15. `scripts/demo_client.py`

```python
# scripts/demo_client.py
"""Tạo SV9001, SV9002 qua API (H5).
Chạy từ thư mục gốc repo:  python -m scripts.demo_client  [--reset]
--reset: xóa SV9001, SV9002 trước khi tạo lại (dùng sau khi đổi bản crypto tạm sang AES-GCM)."""
import sys

import httpx
from dotenv import dotenv_values

env = dotenv_values(".env")
API = f"http://127.0.0.1:{env.get('API_PORT') or '8000'}"
ADMIN = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}

STUDENTS = [
    {"student_id": "SV9001", "full_name": "Nguyen Van A", "major": "Computer Science",
     "national_id": "012345678901", "phone": "0901234567", "address": "Ha Noi (fictional)"},
    {"student_id": "SV9002", "full_name": "Tran Thi B", "major": "Information Security",
     "national_id": "098765432109", "phone": "0912345678", "address": "Da Nang (fictional)"},
]


def main() -> int:
    with httpx.Client(base_url=API, headers=ADMIN, timeout=10) as client:
        if "--reset" in sys.argv:
            for s in STUDENTS:
                print(f"DELETE {s['student_id']} ->", client.delete(f"/students/{s['student_id']}").status_code)
        for s in STUDENTS:
            r = client.post("/students", json=s)
            if r.status_code == 201:
                print(f"{s['student_id']}: created (201)")
            elif r.status_code == 409 and r.json().get("code") == "duplicate_student":
                print(f"{s['student_id']}: already exists, skipped")
            else:
                print(f"{s['student_id']}: error {r.status_code} {r.text}")
                return 1
        print("GET /students/SV9001 ->", client.get("/students/SV9001").status_code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`dotenv` có sẵn vì `pydantic-settings` phụ thuộc `python-dotenv`. Script không in token. Thông báo `print` để tiếng Anh không dấu: trên Windows, khi output bị chuyển hướng, in tiếng Việt có dấu sẽ lỗi `UnicodeEncodeError`.

#### Bước 16. `tests/test_api.py`

Dùng fixture của TV3 (`client`, `admin_headers`, `sample_student`, `db_session`). Test quyền và tamper **không** viết ở đây (thuộc `test_security.py` của TV3).

Test cuối (`test_sensitive_columns_store_only_crypto_output`) giúp TV2 tự kiểm phần “cột nhạy cảm không chứa plaintext” **mà không chờ AES-GCM của TV1**: nó kiểm mỗi cột `*_ct`, `*_nonce` lưu đúng thứ `CryptoService` trả về. Khi đó, cột chứa plaintext hay không chỉ còn phụ thuộc `CryptoService` (việc của TV1, đã có test riêng). Đã thử ngày 13/11/2026 trên code dựng từ kế hoạch: cố ý cài lỗi “lưu plaintext vào `*_ct` rồi đọc thẳng ra, bỏ qua giải mã” thì 8 test còn lại vẫn xanh, chỉ test này bắt được.

```python
# tests/test_api.py
def _create(client, admin_headers, student):
    r = client.post("/students", json=student, headers=admin_headers)
    assert r.status_code == 201, r.text
    return r


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_returns_decrypted_data(client, admin_headers, sample_student):
    body = _create(client, admin_headers, sample_student).json()
    assert body == sample_student


def test_duplicate_returns_409_with_code(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    r = client.post("/students", json=sample_student, headers=admin_headers)
    assert r.status_code == 409
    assert r.json()["code"] == "duplicate_student"


def test_get_one_and_list(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    sid = sample_student["student_id"]
    assert client.get(f"/students/{sid}", headers=admin_headers).json()["phone"] == sample_student["phone"]
    assert [s["student_id"] for s in client.get("/students", headers=admin_headers).json()] == [sid]


def test_get_missing_returns_404(client, admin_headers):
    assert client.get("/students/SV9999", headers=admin_headers).status_code == 404


def test_put_updates_address(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    sid = sample_student["student_id"]
    update = {k: v for k, v in sample_student.items() if k != "student_id"}
    update["address"] = "Hue (fictional)"
    r = client.put(f"/students/{sid}", json=update, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["address"] == "Hue (fictional)"


def test_put_with_student_id_in_body_returns_422(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    r = client.put(f"/students/{sample_student['student_id']}", json=sample_student, headers=admin_headers)
    assert r.status_code == 422


def test_delete_then_404(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    sid = sample_student["student_id"]
    assert client.delete(f"/students/{sid}", headers=admin_headers).status_code == 204
    assert client.get(f"/students/{sid}", headers=admin_headers).status_code == 404


def test_sensitive_columns_store_only_crypto_output(client, admin_headers, sample_student, db_session):
    # Kiểm phần của TV2 mà không cần AES-GCM thật: cột *_ct/*_nonce lưu đúng thứ CryptoService
    # trả về (không lưu plaintext, không tự mã hóa). Bọc CryptoService đang có trên main để ghi lại.
    from app.dependencies import get_crypto
    from app.main import app
    from app.models import Student

    real, issued = get_crypto(), {}

    class RecordingCrypto:
        key_version = real.key_version

        def encrypt(self, value, student_id, field):
            issued[field] = real.encrypt(value, student_id, field)
            return issued[field]

        def decrypt(self, ev, student_id, field):
            return real.decrypt(ev, student_id, field)

    app.dependency_overrides[get_crypto] = RecordingCrypto
    _create(client, admin_headers, sample_student)
    row = db_session.get(Student, sample_student["student_id"])
    assert set(issued) == {"national_id", "phone", "address"}
    for field, ev in issued.items():
        assert getattr(row, f"{field}_ct") == ev.ciphertext
        assert getattr(row, f"{field}_nonce") == ev.nonce
    assert row.key_version == real.key_version
```

**Xong khi:** `python -m pytest tests/test_api.py -q` xanh.

#### Bước 17. `docs/api_db.md`

1. Cấu hình: bảng biến H4, biến nào API dùng, biến nào chỉ script trên máy dùng; vì sao container dùng `db:5432`.
2. Schema `students` (mục 5.3 tài liệu): cột rõ, cột ciphertext, cột nonce, `key_version`.
3. Bảng endpoint, quyền, mã lỗi và `code` (H2).
4. Luồng POST và GET (mục 5.4, 5.5).
5. Cách chạy: `init_env` → `docker compose up -d --build` → `/docs` → `demo_client`; cách xem ciphertext bằng `psql`.
6. Hạn chế: không tìm kiếm `WHERE phone = ...` trên cột mã hóa; token tĩnh chỉ cho demo.

#### Bước 18. Mở PR api-db

```bash
python -m pytest -q
git add app/__init__.py app/config.py app/database.py app/models.py app/schemas.py
git add app/dependencies.py app/student_service.py app/main.py app/init_db.py
git add Dockerfile compose.yaml scripts/demo_client.py tests/test_api.py docs/api_db.md
git status                       # KHÔNG có .env, KHÔNG có file của TV1/TV3
git commit -m "feat(api): persist encrypted students and expose role-protected CRUD"
git push -u origin feature/api-db
```

- [ ] Gán TV1 và TV3 review.
- [ ] Review PR `feature/security-benchmark` của TV3 khi được gán: tên bảng/cột dùng đúng H3, test không phụ thuộc chi tiết nội bộ ngoài H2/H3.

**Xong khi:** PR api-db merge (mốc Vòng 1, cuối tuần 2).

### Tuần 3

#### Bước 19. Kiểm tra trên PostgreSQL sau khi có AES-GCM thật (nghiệm thu chung)

```bash
git switch main && git pull --ff-only origin main
docker compose up -d --build
python -m scripts.demo_client --reset          # dọn dữ liệu tạo bằng bản crypto tạm
docker compose exec db psql -U demo -d encryption_demo -c "SELECT student_id, full_name, encode(phone_ct, 'hex') AS phone_ct FROM students ORDER BY student_id;"
```

- [ ] `phone_ct` là chuỗi hex, không phải số điện thoại.
- [ ] `full_name`, `major` vẫn ở dạng rõ (đúng thiết kế).

#### Bước 20. Sửa lỗi theo issue

- [ ] Mỗi lỗi một PR nhỏ, chỉ trong file của TV2, kèm test tái hiện.
- [ ] Đổi H2/H3/H4 phải qua issue và được TV1, TV3 đồng ý.

#### Bước 21. Nháp Chương 3–4

- [ ] Chương 3 (Phân tích và thiết kế): vì sao chọn mã hóa tầng ứng dụng, kiến trúc, schema, phân quyền.
- [ ] Chương 4 (Triển khai): môi trường, Docker, API, quy trình Git; ghép phần module mã hóa và xác thực do TV1 gửi.
- [ ] Gửi TV1 trước cuối tuần 3 để ghép báo cáo.

### Tuần 4

#### Bước 22. Slide và demo phần 2:00–5:00

- [ ] Slide kiến trúc hệ thống và luồng POST/GET.
- [ ] Demo Swagger: Authorize bằng token admin (không chiếu token), POST rồi GET thấy dữ liệu rõ.
- [ ] Mở `psql` cho thấy cùng hồ sơ đó trong DB chỉ là hex.

#### Bước 23. Tổng duyệt

- [ ] Chạy thử phần của mình đúng 3 phút.
- [ ] Cả nhóm chạy demo 12 phút trên máy demo.

---

## 4. Definition of Done – TV2

**Phần TV2 tự kiểm được, không cần chờ ai** (dùng code TV1, TV3 đã có trên `main` từ Sprint 0, kể cả bản crypto tạm):

- [ ] `docker compose up` lên DB + API, `/health` = 200.
- [ ] CRUD đúng status và `code` lỗi theo H2; mỗi route gắn đúng `require_admin`/`require_reader`.
- [ ] Schema đúng H3; tên `Base`, `get_db`, `Student`, `app` đúng như đã chốt.
- [ ] `test_api.py` xanh, gồm `test_sensitive_columns_store_only_crypto_output` (cột `*_ct`, `*_nonce` lưu đúng thứ `CryptoService` trả về); `demo_client` tạo được SV9001, SV9002.
- [ ] `docs/api_db.md` đầy đủ; không leak key hay token.

**Nghiệm thu chung** (cần AES-GCM của TV1 và `attack_lab` của TV3 trên `main`, mốc tuần 3; không phải việc riêng của TV2):

- [ ] Cột nhạy cảm trong PostgreSQL thật không chứa plaintext (Bước 19).
- [ ] TV3 chạy được `attack_lab` trên hệ thống.

## 5. Rủi ro

| Rủi ro | Dấu hiệu | Cách xử lý |
|---|---|---|
| Nhầm `IntegrityFailure` với `sqlalchemy.exc.IntegrityError` | Trùng mã trả 500, hoặc dữ liệu hỏng trả 409 sai `code` | Import `IntegrityError` dưới tên `DBIntegrityError` như Bước 11 |
| Đổi tên cột sau Sprint 0 | `attack_lab` của TV3 lỗi | H3 đã đóng băng; muốn đổi phải qua issue |
| API container dùng nhầm `DATABASE_URL` trỏ `127.0.0.1` | API không kết nối được DB | `environment:` trong `compose.yaml` ghi đè như Bước 8 |
| Tạo lại `.env` sau khi volume DB đã có | DB báo sai mật khẩu | Khôi phục `.env` cũ hoặc `docker compose down -v` (mất dữ liệu demo) |
| Dữ liệu tạo bằng bản crypto tạm | 409 sau khi TV1 merge AES-GCM | `python -m scripts.demo_client --reset` |
| Trùng cổng 8000/55432 | `docker compose up` báo port in use | Đổi `API_PORT`/`DB_PORT` trong `.env`, sửa cổng trong `DATABASE_URL` |
