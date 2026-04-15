from app.services.crypto import encrypt, decrypt

def test_encrypt_decrypt_roundtrip():
    plaintext = "session_id=abc123; token=xyz789"
    encrypted = encrypt(plaintext)
    assert isinstance(encrypted, bytes)
    assert len(encrypted) > 12
    decrypted = decrypt(encrypted)
    assert decrypted == plaintext

def test_different_encryptions_differ():
    plaintext = "same_cookie"
    e1 = encrypt(plaintext)
    e2 = encrypt(plaintext)
    assert e1 != e2  # random IV
    assert decrypt(e1) == decrypt(e2) == plaintext
