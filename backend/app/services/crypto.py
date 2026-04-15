import os
from hashlib import pbkdf2_hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings

_SALT = b"juflow-cookie-encryption"
_KEY = pbkdf2_hmac("sha256", settings.secret_key.encode(), _SALT, 100000)


def encrypt(plaintext: str) -> bytes:
    iv = os.urandom(12)
    aesgcm = AESGCM(_KEY)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
    return iv + ciphertext


def decrypt(data: bytes) -> str:
    iv = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(_KEY)
    return aesgcm.decrypt(iv, ciphertext, None).decode()
