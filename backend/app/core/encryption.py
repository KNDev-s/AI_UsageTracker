import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings


@dataclass(frozen=True)
class EncryptedPayload:
    ciphertext: bytes
    key_version: int


class CredentialEncryptor:
    """AES-256-GCM authenticated encryption for BYOK credentials."""

    NONCE_SIZE = 12

    def __init__(self, master_key_b64: str | None = None, key_version: int | None = None) -> None:
        settings = get_settings()
        raw_b64 = master_key_b64 or settings.encryption_master_key
        key_bytes = base64.urlsafe_b64decode(raw_b64.encode("ascii"))
        if len(key_bytes) != 32:
            raise ValueError("ENCRYPTION_MASTER_KEY must decode to 32 bytes (256 bits).")
        self._aesgcm = AESGCM(key_bytes)
        self.key_version = key_version or settings.encryption_key_version

    def encrypt(self, plaintext: str, aad: bytes | None = None) -> EncryptedPayload:
        nonce = os.urandom(self.NONCE_SIZE)
        encrypted = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad)
        return EncryptedPayload(ciphertext=nonce + encrypted, key_version=self.key_version)

    def decrypt(self, payload: bytes, aad: bytes | None = None) -> str:
        if len(payload) <= self.NONCE_SIZE:
            raise ValueError("Invalid encrypted credential payload.")
        nonce = payload[: self.NONCE_SIZE]
        ciphertext = payload[self.NONCE_SIZE :]
        return self._aesgcm.decrypt(nonce, ciphertext, aad).decode("utf-8")

