# tests/test_key_manager.py
import base64

import pytest

from app.key_manager import decode_key

KEY = bytes(range(32))


def b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def test_c06_valid_key_decodes_to_32_bytes():
    assert decode_key(b64(KEY)) == KEY


@pytest.mark.parametrize(
    "bad",
    ["not-base64!!", "", b64(bytes(16)), b64(bytes(33)), b64(KEY) + "!"],
    ids=["not_base64", "empty", "16_bytes", "33_bytes", "junk_char"],
)
def test_c06_bad_key_rejected(bad):
    with pytest.raises(ValueError):
        decode_key(bad)


def test_c06_error_message_does_not_leak_key():
    bad = b64(b"SECRET-KEY-16B!!")
    with pytest.raises(ValueError) as exc:
        decode_key(bad)
    assert bad not in str(exc.value)
    assert "SECRET" not in str(exc.value)
