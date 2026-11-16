from functools import lru_cache

from app.config import get_settings
from app.crypto_service import CryptoService
from app.key_manager import decode_key


@lru_cache
def get_crypto() -> CryptoService:
    settings = get_settings()
    return CryptoService(decode_key(settings.encryption_key_b64), settings.key_version)
