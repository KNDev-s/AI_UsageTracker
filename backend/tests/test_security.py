import pytest
from cryptography.exceptions import InvalidTag

from app.core.encryption import CredentialEncryptor
from app.core.security import hash_password, verify_password


def test_argon2id_password_hashing() -> None:
    hashed = hash_password("MySuperSecret123!")
    assert hashed.startswith("$argon2id$")
    assert verify_password("MySuperSecret123!", hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_aes_256_gcm_credential_encryptor_roundtrip() -> None:
    encryptor = CredentialEncryptor()
    aad = b"account:123|integration:456"
    payload = encryptor.encrypt("AIzaSyFakeKeyForUnitTestsOnly", aad=aad)

    assert payload.key_version == 1
    assert b"AIzaSyFakeKey" not in payload.ciphertext

    decrypted = encryptor.decrypt(payload.ciphertext, aad=aad)
    assert decrypted == "AIzaSyFakeKeyForUnitTestsOnly"

    with pytest.raises(InvalidTag):
        encryptor.decrypt(payload.ciphertext, aad=b"account:999|integration:456")

