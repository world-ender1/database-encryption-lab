"""TV2: CRUD, validation, transactions and the H2 error contract."""
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.main import ApiError, create_student
from app.models import Student
from app.schemas import StudentPayload
from scripts.demo_client import STUDENTS, seed


def _create(client, admin_headers, student):
    response = client.post("/students", json=student, headers=admin_headers)
    assert response.status_code == 201, response.text
    assert response.json() == student
    return response


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_crud_roundtrip_and_empty_delete(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    path = f"/students/{sample_student['student_id']}"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == sample_student
    update = {k: v for k, v in sample_student.items() if k != "student_id"}
    update.update(full_name="Trần Thị B", major="Khoa học máy tính", address="Huế (giả lập)")
    response = client.put(path, json=update, headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == {"student_id": sample_student["student_id"], **update}
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(path, headers=admin_headers).status_code == 404


def test_duplicate_is_409_and_original_unchanged(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    response = client.post("/students", json={**sample_student, "phone": "new"}, headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "duplicate_student"
    assert client.get("/students/SV9001", headers=admin_headers).json() == sample_student


def test_list_is_ordered(client, admin_headers, sample_student):
    assert client.get("/students", headers=admin_headers).json() == []
    second = {**sample_student, "student_id": "SV9002"}
    _create(client, admin_headers, second)
    _create(client, admin_headers, sample_student)
    response = client.get("/students", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == [sample_student, second]


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_record(client, admin_headers, sample_student, method):
    kwargs = {"headers": admin_headers}
    if method == "put":
        kwargs["json"] = {k: v for k, v in sample_student.items() if k != "student_id"}
    response = getattr(client, method)("/students/SV9999", **kwargs)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


@pytest.mark.parametrize("sid", ["' OR 1=1--", "SV-1", "x" * 17, "SV1\n", "sinhviên"])
def test_invalid_ids_in_post_and_paths(client, admin_headers, sample_student, sid):
    from urllib.parse import quote
    response = client.post("/students", json={**sample_student, "student_id": sid}, headers=admin_headers)
    assert response.status_code == 422
    update = {k: v for k, v in sample_student.items() if k != "student_id"}
    for method in ("get", "put", "delete"):
        kwargs = {"headers": admin_headers}
        if method == "put":
            kwargs["json"] = update
        assert getattr(client, method)(f"/students/{quote(sid, safe='')}", **kwargs).status_code == 422


@pytest.mark.parametrize("field,limit", [("full_name", 150), ("major", 100),
                                        ("national_id", 32), ("phone", 32), ("address", 255)])
def test_invalid_field_lengths(client, admin_headers, sample_student, field, limit):
    for value in ("", "x" * (limit + 1)):
        assert client.post("/students", json={**sample_student, field: value},
                           headers=admin_headers).status_code == 422


def test_put_rejects_id_extra_and_partial_body(client, admin_headers, sample_student):
    _create(client, admin_headers, sample_student)
    for body in (sample_student, {"address": "new"}, {**sample_student, "extra": "bad"}):
        assert client.put("/students/SV9001", json=body, headers=admin_headers).status_code == 422
    assert client.get("/students/SV9001", headers=admin_headers).json() == sample_student
    assert client.post("/students", json={**sample_student, "extra": "bad"},
                       headers=admin_headers).status_code == 422


def test_put_refreshes_every_nonce(client, admin_headers, sample_student, db_session):
    _create(client, admin_headers, sample_student)
    row = db_session.get(Student, sample_student["student_id"])
    fields = ("national_id", "phone", "address")
    before = [getattr(row, f"{field}_nonce") for field in fields]
    update = {k: v for k, v in sample_student.items() if k != "student_id"}
    assert client.put("/students/SV9001", json=update, headers=admin_headers).status_code == 200
    db_session.refresh(row)
    assert all(old != getattr(row, f"{field}_nonce") for old, field in zip(before, fields))


def test_failed_decryption_blocks_entire_list_and_allows_delete(
    client, admin_headers, sample_student, db_session,
):
    for sid in ("SV9001", "SV9002", "SV9003"):
        _create(client, admin_headers, {**sample_student, "student_id": sid})
    for sid in ("SV9001", "SV9003"):
        db_session.get(Student, sid).phone_ct = b""
    db_session.commit()
    response = client.get("/students", headers=admin_headers)
    assert response.status_code == 409
    assert response.json() == {"detail": "Encrypted data failed authentication",
                               "code": "integrity_failure", "student_ids": ["SV9001", "SV9003"]}
    response = client.get("/students/SV9001", headers=admin_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "integrity_failure"
    assert client.delete("/students/SV9001", headers=admin_headers).status_code == 204


@pytest.mark.parametrize("method,path", [("post", "/students"), ("get", "/students"),
    ("get", "/students/SV9001"), ("put", "/students/SV9001"), ("delete", "/students/SV9001")])
def test_every_route_requires_token(client, sample_student, method, path):
    for headers in ({}, {"Authorization": "Bearer wrong"}):
        response = client.request(method, path, headers=headers, json=sample_student)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_viewer_can_read_but_cannot_write(client, admin_headers, viewer_headers, sample_student):
    _create(client, admin_headers, sample_student)
    for path in ("/students", "/students/SV9001"):
        assert client.get(path, headers=viewer_headers).status_code == 200
    for method, path in (("post", "/students"), ("put", "/students/SV9001"),
                         ("delete", "/students/SV9001")):
        assert client.request(method, path, json=sample_student, headers=viewer_headers).status_code == 403
    assert client.get("/students/SV9001", headers=admin_headers).json() == sample_student


def test_concurrent_duplicate_rolls_back(sample_student):
    db = Mock()
    db.get.side_effect = [None, object()]
    db.commit.side_effect = IntegrityError("insert", {}, Exception("unique violation"))
    with pytest.raises(ApiError) as exc:
        create_student(StudentPayload(**sample_student), db, Mock(key_version="v1"))
    assert exc.value.code == "duplicate_student"
    db.rollback.assert_called_once()


def test_other_database_constraint_not_mislabeled(sample_student):
    db = Mock()
    db.get.return_value = None
    db.commit.side_effect = IntegrityError("insert", {}, Exception("not-null violation"))
    with pytest.raises(IntegrityError):
        create_student(StudentPayload(**sample_student), db, Mock(key_version="v1"))
    db.rollback.assert_called_once()


def test_demo_client_repeat_and_reset(client, admin_headers):
    client.headers.update(admin_headers)
    assert seed(client) == 0
    assert seed(client) == 0
    assert seed(client, reset=True) == 0
    assert client.get("/students").json() == STUDENTS


def test_demo_client_fails_when_reset_is_denied(client, viewer_headers):
    client.headers.update(viewer_headers)
    assert seed(client, reset=True) == 1
