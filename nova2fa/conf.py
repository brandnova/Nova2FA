"""
Settings configuration for Nova2FA.
"""
from django.conf import settings


class Nova2FASettings:
    """
    Helper class to access Nova2FA settings with defaults.
    """
    
    @property
    def ENABLED_METHODS(self):
        """Available 2FA methods."""
        return getattr(settings, 'NOVA2FA_ENABLED_METHODS', ['email', 'totp'])
    
    @property
    def VERIFICATION_WINDOW_DAYS(self):
        """Days before re-verification is required."""
        return getattr(settings, 'NOVA2FA_VERIFICATION_WINDOW_DAYS', 14)
    
    @property
    def EMAIL_OTP_EXPIRY_MINUTES(self):
        """Minutes before email OTP expires."""
        return getattr(settings, 'NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES', 10)
    
    @property
    def EMAIL_SUBJECT(self):
        """Email subject for OTP emails."""
        return getattr(settings, 'NOVA2FA_EMAIL_SUBJECT', 'Your One-Time Password')
    
    @property
    def TOTP_ISSUER(self):
        """Issuer name for TOTP."""
        return getattr(settings, 'NOVA2FA_TOTP_ISSUER', 'Nova2FA')
    
    @property
    def BACKUP_CODE_COUNT(self):
        """Number of backup codes to generate."""
        return getattr(settings, 'NOVA2FA_BACKUP_CODE_COUNT', 8)
    
    @property
    def EXEMPT_SUPERUSERS(self):
        """Exempt superusers from 2FA."""
        return getattr(settings, 'NOVA2FA_EXEMPT_SUPERUSERS', False)
    
    @property
    def EXEMPT_PATHS(self):
        """Paths to exempt from 2FA verification."""
        return getattr(settings, 'NOVA2FA_EXEMPT_PATHS', [])
    
    @property
    def PROTECTED_PATHS(self):
        """Paths that require 2FA (wildcard * means all)."""
        return getattr(settings, 'NOVA2FA_PROTECTED_PATHS', ['*'])
    
    @property
    def BASE_TEMPLATE(self):
        """Base template for Nova2FA templates."""
        return getattr(settings, 'NOVA2FA_BASE_TEMPLATE', 'nova2fa/base_2fa.html')


# Create a singleton instance
nova2fa_settings = Nova2FASettings()