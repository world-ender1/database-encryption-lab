from typing import Annotated

from fastapi import Depends, FastAPI, Path, Request, Response
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
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.extra = extra


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
    """Liveness only; DB readiness is checked by Compose separately."""
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
        # A concurrent POST can win after the initial existence check.
        # Other DB constraints must not be mislabeled as duplicate IDs.
        if db.get(Student, payload.student_id) is not None:
            raise ApiError(409, "duplicate_student", "Student already exists") from None
        raise
    return _decrypt_or_409(row, crypto)


@app.get("/students", response_model=list[StudentOut], dependencies=[Depends(require_reader)])
def list_students(db: DB, crypto: Crypto):
    out, failed = [], []
    for row in db.scalars(select(Student).order_by(Student.student_id)):
        try:
            out.append(to_out(row, crypto))
        except IntegrityFailure:
            failed.append(row.student_id)
    if failed:
        raise ApiError(409, "integrity_failure", "Encrypted data failed authentication",
                       student_ids=failed)
    return out


@app.get("/students/{student_id}", response_model=StudentOut,
         dependencies=[Depends(require_reader)])
def get_student(student_id: StudentIdPath, db: DB, crypto: Crypto):
    return _decrypt_or_409(_get_or_404(db, student_id), crypto)


@app.put("/students/{student_id}", response_model=StudentOut,
         dependencies=[Depends(require_admin)])
def update_student(student_id: StudentIdPath, payload: StudentUpdate, db: DB, crypto: Crypto):
    row = _get_or_404(db, student_id)
    apply_sensitive(row, payload, crypto)
    row.full_name, row.major = payload.full_name, payload.major
    db.commit()
    return _decrypt_or_409(row, crypto)


@app.delete("/students/{student_id}", status_code=204, response_class=Response,
            dependencies=[Depends(require_admin)])
def delete_student(student_id: StudentIdPath, db: DB):
    # No decryption: an admin can remove damaged or old-stub records.
    db.delete(_get_or_404(db, student_id))
    db.commit()
    return Response(status_code=204)
