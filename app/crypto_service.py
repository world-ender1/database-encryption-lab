# app/crypto_service.py
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 32
NONCE_SIZE = 12


class IntegrityFailure(Exception):
    """Giải mã thất bại: sai key, nonce, AAD, dữ liệu đã bị sửa, hoặc plaintext không phải UTF-8."""


@dataclass(frozen=True)
class EncryptedValue:
    ciphertext: bytes
    nonce: bytes
    key_version: str


class CryptoService:
    def __init__(self, key: bytes, key_version: str = "v1") -> None:
        if len(key) != KEY_SIZE:  # AESGCM nhận cả key 16/24 byte nên phải tự chặn
            raise ValueError("Key phải đúng 32 byte")
        self._aes = AESGCM(key)
        self.key_version = key_version

    @staticmethod
    def _aad(student_id: str, field: str, key_version: str) -> bytes:
        return f"student:{student_id}|field:{field}|key:{key_version}".encode("utf-8")

    def encrypt(self, value: str, student_id: str, field: str) -> EncryptedValue:
        nonce = os.urandom(NONCE_SIZE)  # nonce mới cho MỖI lần mã hóa
        ct = self._aes.encrypt(nonce, value.encode("utf-8"),
                               self._aad(student_id, field, self.key_version))
        return EncryptedValue(ct, nonce, self.key_version)

    def decrypt(self, ev: EncryptedValue, student_id: str, field: str) -> str:
        if ev.key_version != self.key_version:
            raise IntegrityFailure("Không có key cho phiên bản này")
        if len(ev.nonce) != NONCE_SIZE:  # nonce dưới 8 byte: AESGCM ném ValueError chứ không phải InvalidTag
            raise IntegrityFailure("Nonce sai độ dài")
        try:
            pt = self._aes.decrypt(ev.nonce, ev.ciphertext,
                                   self._aad(student_id, field, ev.key_version))
        except InvalidTag as exc:
            raise IntegrityFailure("Authentication failed") from exc
        try:
            return pt.decode("utf-8")
        except UnicodeDecodeError as exc:  # tag đúng nhưng không phải UTF-8: chỉ người có key tạo được
            raise IntegrityFailure("Plaintext không phải UTF-8") from exc
