# tests/test_security.py
"""Security tests verifying threat-model controls A1-A5 and A8 (contracts H2, H3)."""
import pytest
from sqlalchemy import func, select

WAIT_API = pytest.mark.xfail(reason="chờ API CRUD của TV2 trên main", strict=False)


def _student_model():
    from app.models import Student

    return Student


def _create(client, admin_headers, student):
    response = client.post("/students", json=student, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response


def _count(db_session):
    student_cls = _student_model()
    return db_session.scalar(select(func.count()).select_from(student_cls))


# ---------- A1: Thiếu hoặc sai Bearer token -> 401 ----------


@WAIT_API
def test_a1_missing_token_401(client):
    for path in ("/students", "/students/SV9001"):
        response = client.get(path)
        assert response.status_code == 401
        assert response.headers.get("www-authenticate") == "Bearer"


@WAIT_API
@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": "Bearer wrong-token"},
        {"Authorization": "Basic YWRtaW46YWRtaW4="},
        {"Authorization": "Bearer "},
    ],
    ids=["wrong_token", "basic_scheme", "empty_bearer"],
)
def test_a1_wrong_token_401(client, headers):
    response = client.get("/students", headers=headers)
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


# ---------- A2: Viewer không được ghi/xóa -> 403 ----------


@WAIT_API
def test_a2_viewer_cannot_write_403(client, viewer_headers, sample_student):
    assert client.post("/students", json=sample_student, headers=viewer_headers).status_code == 403
    update_payload = {k: v for k, v in sample_student.items() if k != "student_id"}
    assert client.put("/students/SV9001", json=update_payload, headers=viewer_headers).status_code == 403
    assert client.delete("/students/SV9001", headers=viewer_headers).status_code == 403


@WAIT_API
def test_a2_viewer_delete_keeps_row(client, admin_headers, viewer_headers, sample_student):
    _create(client, admin_headers, sample_student)
    assert client.delete("/students/SV9001", headers=viewer_headers).status_code == 403
    get_resp = client.get("/students/SV9001", headers=viewer_headers)
    assert get_resp.status_code == 200
    assert get_resp.json() == sample_student


# ---------- A3: Cột nhạy cảm trong DB không chứa plaintext ----------


@WAIT_API
def test_a3_db_has_no_plaintext(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    student_cls = _student_model()
    row = db_session.get(student_cls, "SV9001")
    assert row is not None
    assert row.key_version == "v1"
    for field in ("national_id", "phone", "address"):
        plaintext_bytes = sample_student[field].encode("utf-8")
        ct = getattr(row, f"{field}_ct")
        nonce = getattr(row, f"{field}_nonce")
        assert isinstance(ct, bytes) and isinstance(nonce, bytes)
        assert len(nonce) == 12
        assert len(ct) == len(plaintext_bytes) + 16
        assert plaintext_bytes not in ct
        assert plaintext_bytes not in nonce


# ---------- A4: Sửa ciphertext hoặc nonce/tag -> 409 integrity_failure ----------


@WAIT_API
def test_a4_tampered_ciphertext_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    student_cls = _student_model()
    row = db_session.get(student_cls, "SV9001")
    ct = bytearray(row.national_id_ct)
    ct[0] ^= 0x01
    row.national_id_ct = bytes(ct)
    db_session.commit()

    single = client.get("/students/SV9001", headers=admin_headers)
    assert single.status_code == 409
    assert single.json()["code"] == "integrity_failure"

    listing = client.get("/students", headers=admin_headers)
    assert listing.status_code == 409
    assert listing.json()["code"] == "integrity_failure"
    assert listing.json()["student_ids"] == ["SV9001"]


@WAIT_API
def test_a4_tampered_nonce_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    student_cls = _student_model()
    row = db_session.get(student_cls, "SV9001")
    nonce = bytearray(row.phone_nonce)
    nonce[0] ^= 0x01
    row.phone_nonce = bytes(nonce)
    db_session.commit()

    response = client.get("/students/SV9001", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "integrity_failure"


# ---------- A5: Tráo ciphertext giữa hai hàng / hai cột -> 409 (AAD mismatch) ----------


@WAIT_API
def test_a5_swapped_between_rows_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    _create(
        client,
        admin_headers,
        {**sample_student, "student_id": "SV9002", "national_id": "098765432109"},
    )
    student_cls = _student_model()
    row_a = db_session.get(student_cls, "SV9001")
    row_b = db_session.get(student_cls, "SV9002")
    row_a.national_id_ct = row_b.national_id_ct
    row_a.national_id_nonce = row_b.national_id_nonce
    db_session.commit()

    response = client.get("/students/SV9001", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "integrity_failure"


@WAIT_API
def test_a5_swapped_between_fields_same_row_409(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    student_cls = _student_model()
    row = db_session.get(student_cls, "SV9001")
    row.national_id_ct = row.phone_ct
    row.national_id_nonce = row.phone_nonce
    db_session.commit()

    response = client.get("/students/SV9001", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "integrity_failure"


# ---------- PUT phải sinh nonce mới cho cả 3 trường ----------


@WAIT_API
def test_put_reencrypts_all_sensitive_fields_with_fresh_nonces(
    client, admin_headers, sample_student, db_session
):
    _create(client, admin_headers, sample_student)
    student_cls = _student_model()
    row = db_session.get(student_cls, "SV9001")
    old_nonces = (row.national_id_nonce, row.phone_nonce, row.address_nonce)
    old_cts = (row.national_id_ct, row.phone_ct, row.address_ct)

    update_payload = {k: v for k, v in sample_student.items() if k != "student_id"}
    resp = client.put("/students/SV9001", json=update_payload, headers=admin_headers)
    assert resp.status_code == 200

    db_session.expire_all()
    updated = db_session.get(student_cls, "SV9001")
    new_nonces = (updated.national_id_nonce, updated.phone_nonce, updated.address_nonce)
    new_cts = (updated.national_id_ct, updated.phone_ct, updated.address_ct)
    for old_n, new_n, old_c, new_c in zip(old_nonces, new_nonces, old_cts, new_cts):
        assert old_n != new_n
        assert old_c != new_c


# ---------- A8: Chuỗi kiểu SQL injection -> 422, DB không đổi ----------


@WAIT_API
@pytest.mark.parametrize(
    "bad_id",
    [
        "SV9001' OR '1'='1",
        "SV9001;DROP TABLE students;--",
    ],
    ids=["or_injection", "drop_table"],
)
def test_a8_sql_like_id_422_and_db_unchanged(
    client, admin_headers, sample_student, db_session, bad_id
):
    _create(client, admin_headers, sample_student)
    before = _count(db_session)

    get_resp = client.get(f"/students/{bad_id}", headers=admin_headers)
    assert get_resp.status_code == 422

    post_resp = client.post(
        "/students",
        json={**sample_student, "student_id": bad_id},
        headers=admin_headers,
    )
    assert post_resp.status_code == 422
    assert _count(db_session) == before
