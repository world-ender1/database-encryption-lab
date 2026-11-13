# app/crypto_service.py  (BẢN TẠM SPRINT 0)
# BẢN TẠM SPRINT 0 – KHÔNG MÃ HÓA THẬT – KHÔNG DÙNG ĐỂ DEMO
import hashlib
import hmac
import os
from dataclasses import dataclass

NONCE_SIZE = 12
TAG_SIZE = 16


class IntegrityFailure(Exception):
    """Giải mã thất bại: sai key, nonce, AAD hoặc dữ liệu đã bị sửa."""


@dataclass(frozen=True)
class EncryptedValue:
    ciphertext: bytes
    nonce: bytes
    key_version: str


class CryptoService:
    def __init__(self, key: bytes, key_version: str = "v1") -> None:
        if len(key) != 32:
            raise ValueError("Key phải đúng 32 byte")
        self.key_version = key_version

    @staticmethod
    def _aad(student_id: str, field: str, key_version: str) -> bytes:
        return f"student:{student_id}|field:{field}|key:{key_version}".encode("utf-8")

    @staticmethod
    def _fake_tag(nonce: bytes, aad: bytes, data: bytes) -> bytes:
        return hashlib.sha256(nonce + aad + data).digest()[:TAG_SIZE]

    def encrypt(self, value: str, student_id: str, field: str) -> EncryptedValue:
        nonce = os.urandom(NONCE_SIZE)
        data = value.encode("utf-8")
        aad = self._aad(student_id, field, self.key_version)
        return EncryptedValue(data + self._fake_tag(nonce, aad, data), nonce, self.key_version)

    def decrypt(self, ev: EncryptedValue, student_id: str, field: str) -> str:
        if ev.key_version != self.key_version or len(ev.ciphertext) < TAG_SIZE:
            raise IntegrityFailure("Authentication failed")
        data, tag = ev.ciphertext[:-TAG_SIZE], ev.ciphertext[-TAG_SIZE:]
        aad = self._aad(student_id, field, ev.key_version)
        if not hmac.compare_digest(tag, self._fake_tag(ev.nonce, aad, data)):
            raise IntegrityFailure("Authentication failed")
        return data.decode("utf-8")
