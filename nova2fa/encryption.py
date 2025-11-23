"""
Encryption utilities for Nova2FA.
Handles encryption/decryption of sensitive data like TOTP secrets.
"""
from typing import Optional
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Get the encryption key from Django settings.
    
    Returns:
        bytes: Fernet-compatible encryption key
        
    Raises:
        ImproperlyConfigured: If NOVA2FA_SECRET_KEY is not set
    """
    secret_key = getattr(settings, 'NOVA2FA_SECRET_KEY', None)
    
    if not secret_key:
        # Fall back to Django's SECRET_KEY for backward compatibility
        secret_key = settings.SECRET_KEY
    
    # Derive a Fernet key from the secret key
    # Use SHA256 to get 32 bytes, then base64 encode for Fernet
    key_bytes = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def get_cipher() -> Fernet:
    """
    Get a Fernet cipher instance.
    
    Returns:
        Fernet: Cipher instance for encryption/decryption
    """
    key = get_encryption_key()
    return Fernet(key)


def encrypt_secret(secret: str) -> str:
    """
    Encrypt a TOTP secret.
    
    Args:
        secret: Plain text secret to encrypt
        
    Returns:
        str: Encrypted secret (base64 encoded)
    """
    if not secret:
        return ""
    
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(secret.encode())
    return encrypted_bytes.decode('utf-8')


def decrypt_secret(encrypted: str) -> str:
    """
    Decrypt a TOTP secret.
    
    Args:
        encrypted: Encrypted secret (base64 encoded)
        
    Returns:
        str: Decrypted plain text secret
        
    Raises:
        ValueError: If decryption fails
    """
    if not encrypted:
        return ""
    
    try:
        cipher = get_cipher()
        decrypted_bytes = cipher.decrypt(encrypted.encode())
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt secret: {str(e)}")


def is_encrypted(value: Optional[str]) -> bool:
    """
    Check if a value appears to be encrypted.
    
    Args:
        value: String to check
        
    Returns:
        bool: True if value appears encrypted, False otherwise
    """
    if not value:
        return False
    
    # Fernet tokens start with 'gAAAAA' after base64 encoding
    # This is a heuristic check
    try:
        return value.startswith('gAAAAA') and len(value) > 50
    except (AttributeError, TypeError):
        return False
