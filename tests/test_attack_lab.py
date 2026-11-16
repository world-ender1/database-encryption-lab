"""Check that attack_lab rejects false passes and restores demo DB bytes."""
import httpx
import pytest
from sqlalchemy import Column, LargeBinary, MetaData, String, Table, create_engine, insert
from sqlalchemy.pool import StaticPool

from scripts.attack_lab import _row, a2, a3, a4, a5
from scripts.demo_client import STUDENTS


@pytest.fixture
def lab_db():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    students = Table(
        "students", MetaData(),
        Column("student_id", String, primary_key=True),
        Column("national_id_ct", LargeBinary), Column("national_id_nonce", LargeBinary),
        Column("phone_ct", LargeBinary), Column("phone_nonce", LargeBinary),
        Column("address_ct", LargeBinary), Column("address_nonce", LargeBinary),
        Column("key_version", String),
    )
    students.create(engine)
    with engine.connect() as conn:
        for index, payload in enumerate(STUDENTS, 1):
            values = {"student_id": payload["student_id"], "key_version": "v1"}
            for field in ("national_id", "phone", "address"):
                values[f"{field}_ct"] = bytes([index + 64]) * (len(payload[field].encode()) + 16)
                values[f"{field}_nonce"] = bytes([index]) * 12
            conn.execute(insert(students).values(**values))
        conn.commit()
        yield conn, students
    engine.dispose()


def _client(responses):
    queue = iter(responses)

    def handle(request):
        item = next(queue)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.Client(transport=httpx.MockTransport(handle), base_url="http://test")


def _ok(payload):
    return httpx.Response(200, json=payload)


def test_a2_fails_when_delete_403_but_row_not_readable(lab_db):
    conn, students = lab_db
    with _client([httpx.Response(403), httpx.Response(404)]) as client:
        assert not a2(conn, students, client, {}, {}, STUDENTS[0])
    assert _row(conn, students, "SV9001")["student_id"] == "SV9001"


@pytest.mark.parametrize("bad_response", [
    httpx.Response(409, json={"code": "duplicate_student"}),
    httpx.Response(409, json={"detail": "wrong error"}),
    httpx.Response(409, text="not JSON"),
    httpx.Response(409, json={"code": "integrity_failure", "phone": "leaked"}),
])
def test_a4_rejects_wrong_error_and_restores_bytes(lab_db, bad_response):
    conn, students = lab_db
    before = _row(conn, students, "SV9001")
    with _client([bad_response, _ok(STUDENTS[0])]) as client:
        assert not a4(conn, students, client, {}, STUDENTS[0])
    assert _row(conn, students, "SV9001") == before


def test_a5_rejects_wrong_error_and_restores_both_rows(lab_db):
    conn, students = lab_db
    before = {payload["student_id"]: _row(conn, students, payload["student_id"])
              for payload in STUDENTS}
    with _client([httpx.Response(409, json={"code": "duplicate_student"}),
                  *(_ok(payload) for payload in STUDENTS)]) as client:
        assert not a5(conn, students, client, {}, {
            payload["student_id"]: payload for payload in STUDENTS})
    assert all(_row(conn, students, sid) == row for sid, row in before.items())


@pytest.mark.parametrize("attack", ["a4", "a5"])
def test_http_error_still_restores_db_bytes(lab_db, attack):
    conn, students = lab_db
    before = {payload["student_id"]: _row(conn, students, payload["student_id"])
              for payload in STUDENTS}
    with _client([httpx.ReadError("simulated network failure")]) as client:
        with pytest.raises(httpx.ReadError):
            if attack == "a4":
                a4(conn, students, client, {}, STUDENTS[0])
            else:
                a5(conn, students, client, {}, {p["student_id"]: p for p in STUDENTS})
    assert all(_row(conn, students, sid) == row for sid, row in before.items())


def test_a3_checks_all_three_fields(lab_db):
    conn, students = lab_db
    expected = {p["student_id"]: p for p in STUDENTS}
    assert a3(conn, students, expected)
    conn.execute(students.update().where(students.c.student_id == "SV9002")
                 .values(address_ct=STUDENTS[1]["address"].encode() + b"0" * 16))
    conn.commit()
    assert not a3(conn, students, expected)
