import pytest
from src.storage.crypto import Crypto

def test_crypto_encrypt_decrypt():
    crypto = Crypto()
    original_text = "sk-test-123456"
    
    encrypted = crypto.encrypt(original_text)
    assert encrypted != original_text
    assert len(encrypted) > 0
    
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == original_text

def test_crypto_empty():
    crypto = Crypto()
    assert crypto.encrypt("") == ""
    assert crypto.decrypt("") == ""

def test_crypto_custom_key():
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    crypto = Crypto(key=key)
    
    text = "secret"
    encrypted = crypto.encrypt(text)
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == text
