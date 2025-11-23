"""
Tests for Nova2FA encryption utilities.
"""
import pytest
from nova2fa.encryption import (
    encrypt_secret,
    decrypt_secret,
    is_encrypted,
    get_cipher
)


class TestEncryption:
    """Tests for encryption utilities."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly."""
        plain_text = "JBSWY3DPEHPK3PXP"
        
        encrypted = encrypt_secret(plain_text)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == plain_text
    
    def test_encrypted_value_is_different(self):
        """Test that encrypted value is different from plain text."""
        plain_text = "JBSWY3DPEHPK3PXP"
        encrypted = encrypt_secret(plain_text)
        
        assert encrypted != plain_text
    
    def test_is_encrypted_detects_encrypted_value(self):
        """Test that is_encrypted correctly identifies encrypted values."""
        plain_text = "JBSWY3DPEHPK3PXP"
        encrypted = encrypt_secret(plain_text)
        
        assert is_encrypted(encrypted)
        assert not is_encrypted(plain_text)
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        encrypted = encrypt_secret("")
        assert encrypted == ""
    
    def test_decrypt_empty_string(self):
        """Test decrypting empty string."""
        decrypted = decrypt_secret("")
        assert decrypted == ""
    
    def test_decrypt_invalid_value_raises_error(self):
        """Test that decrypting invalid value raises error."""
        with pytest.raises(ValueError):
            decrypt_secret("invalid_encrypted_value")
    
    def test_get_cipher_returns_fernet(self):
        """Test that get_cipher returns a Fernet instance."""
        from cryptography.fernet import Fernet
        cipher = get_cipher()
        assert isinstance(cipher, Fernet)
