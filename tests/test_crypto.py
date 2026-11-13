# tests/test_crypto.py
import dataclasses
import inspect

import pytest

from app.crypto_service import CryptoService, EncryptedValue, IntegrityFailure

KEY = bytes(range(32))
OTHER_KEY = bytes(32)

# Bản tạm Sprint 0 chưa mã hóa thật nên 3 test đánh dấu dưới đây chưa thể đạt.
# strict=True: nếu test bỗng đạt thì pytest báo lỗi, buộc phải gỡ marker.
# Gỡ marker ở W1-09 – đó là bước "đỏ" trước khi viết AES-GCM.
needs_real_crypto = pytest.mark.xfail(strict=True, reason="Bản tạm Sprint 0 chưa mã hóa thật – gỡ ở W1-09")


@pytest.fixture
def crypto():
    return CryptoService(KEY, "v1")


def flip(data: bytes, pos: int) -> bytes:
    out = bytearray(data)
    out[pos] ^= 0x01
    return bytes(out)


# ---------- H1: hình dạng hợp đồng ----------

def test_h1_signatures():
    init = inspect.signature(CryptoService.__init__).parameters
    assert list(init) == ["self", "key", "key_version"]
    assert init["key_version"].default == "v1"
    assert list(inspect.signature(CryptoService.encrypt).parameters) == ["self", "value", "student_id", "field"]
    assert list(inspect.signature(CryptoService.decrypt).parameters) == ["self", "ev", "student_id", "field"]


def test_h1_encrypted_value_layout(crypto):
    ev = crypto.encrypt("Ha Noi", "SV9001", "address")
    assert [f.name for f in dataclasses.fields(EncryptedValue)] == ["ciphertext", "nonce", "key_version"]
    assert len(ev.nonce) == 12
    assert len(ev.ciphertext) == len("Ha Noi".encode("utf-8")) + 16
    assert ev.key_version == "v1"
    with pytest.raises(dataclasses.FrozenInstanceError):
        ev.nonce = bytes(12)


@pytest.mark.parametrize("size", [16, 31, 33])
def test_h1_key_must_be_32_bytes(size):
    with pytest.raises(ValueError):
        CryptoService(bytes(size))


@needs_real_crypto
def test_h1_known_vector_matches_aad_contract(crypto):
    # AES-256-GCM, key = bytes(range(32)), nonce = bytes(range(12)),
    # AAD = b"student:SV9001|field:address|key:v1", plaintext = "Ha Noi".
    # Ciphertext + tag tính sẵn; đổi định dạng AAD là test này đỏ.
    ev = EncryptedValue(bytes.fromhex("0f63f655aa8ccd733631070afa0ddf496bfbad142ec5"), bytes(range(12)), "v1")
    assert crypto.decrypt(ev, "SV9001", "address") == "Ha Noi"


# ---------- C01: mã hóa rồi giải mã ra đúng dữ liệu ----------

@pytest.mark.parametrize("text", ["Hà Nội – Phường Giả Lập", "", "012345678901"],
                         ids=["vietnamese", "empty", "digits"])
def test_c01_roundtrip(crypto, text):
    ev = crypto.encrypt(text, "SV9001", "address")
    assert crypto.decrypt(ev, "SV9001", "address") == text


def test_c01_new_instance_with_same_key_can_decrypt(crypto):
    ev = crypto.encrypt("0901234567", "SV9001", "phone")
    assert CryptoService(KEY, "v1").decrypt(ev, "SV9001", "phone") == "0901234567"


# ---------- C02: mỗi lần mã hóa một nonce mới, không lộ plaintext ----------

def test_c02_nonce_and_ciphertext_differ(crypto):
    a = crypto.encrypt("0901234567", "SV9001", "phone")
    b = crypto.encrypt("0901234567", "SV9001", "phone")
    assert a.nonce != b.nonce
    assert a.ciphertext != b.ciphertext


@needs_real_crypto
def test_c02_ciphertext_hides_plaintext(crypto):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    assert b"012345678901" not in ev.ciphertext


# ---------- C03: sai key ----------

@needs_real_crypto
def test_c03_wrong_key(crypto):  # A6
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        CryptoService(OTHER_KEY, "v1").decrypt(ev, "SV9001", "national_id")


# ---------- C04: dữ liệu lưu bị sửa ----------

@pytest.mark.parametrize("mutate", [
    lambda ct: flip(ct, 0),    # byte đầu ciphertext
    lambda ct: flip(ct, -1),   # byte cuối của tag
    lambda ct: ct[:10],        # bị cắt, ngắn hơn tag
    lambda ct: b"",            # rỗng
], ids=["first_byte", "last_tag_byte", "truncated", "empty"])
def test_c04_tampered_ciphertext(crypto, mutate):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, ciphertext=mutate(ev.ciphertext)), "SV9001", "national_id")


@pytest.mark.parametrize("mutate", [
    lambda n: flip(n, 0),
    lambda n: n[:11],
    lambda n: b"",
], ids=["flipped", "11_bytes", "empty"])
def test_c04_tampered_nonce(crypto, mutate):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, nonce=mutate(ev.nonce)), "SV9001", "national_id")


# ---------- C05: sai AAD (tráo hàng, tráo cột, sai key_version) ----------

@pytest.mark.parametrize("sid, field", [("SV9002", "national_id"), ("SV9001", "phone")],
                         ids=["other_student", "other_field"])
def test_c05_wrong_aad(crypto, sid, field):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(ev, sid, field)


def test_c05_wrong_key_version(crypto):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, key_version="v2"), "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        CryptoService(KEY, "v2").decrypt(ev, "SV9001", "national_id")
