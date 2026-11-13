# app/key_manager.py
import base64
import binascii

KEY_SIZE = 32


def decode_key(encoded_key: str) -> bytes:
    """Giải mã ENCRYPTION_KEY_B64. Sai Base64 hoặc khác 32 byte: raise ValueError."""
    try:
        key = base64.b64decode(encoded_key, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("ENCRYPTION_KEY_B64 không phải Base64 hợp lệ") from exc
    if len(key) != KEY_SIZE:
        raise ValueError(f"Key phải đúng {KEY_SIZE} byte, nhận được {len(key)} byte")
    return key
