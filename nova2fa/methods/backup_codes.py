"""
Backup codes method implementation.
"""
import random
import string
from typing import Dict, List, Any
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .base import Base2FAMethod


class BackupCodesMethod(Base2FAMethod):
    """
    Backup codes for account recovery.
    """
    name = "backup"
    verbose_name = "Backup Codes"
    
    def send(self, user) -> bool:
        """
        Backup codes don't need to be sent.
        """
        return True
    
    def verify(self, user, token: str) -> bool:
        """
        Verify a backup code.
        """
        from nova2fa.models import UserTwoFactorSettings
        
        try:
            settings_obj = UserTwoFactorSettings.objects.get(user=user)
            return settings_obj.verify_backup_code(token)
        except UserTwoFactorSettings.DoesNotExist:
            return False
    
    def setup(self, user) -> Dict[str, Any]:
        """
        Generate new backup codes.
        Returns both plain text codes (for user display) and hashed codes (for storage).
        """
        count = getattr(settings, 'NOVA2FA_BACKUP_CODE_COUNT', 8)
        plain_codes = self._generate_codes(count)
        hashed_codes = [make_password(code) for code in plain_codes]
        
        return {
            'codes': plain_codes,        # Plain text for user to save
            'hashed_codes': hashed_codes  # Hashed for database storage
        }
    
    def _generate_codes(self, count: int = 8) -> List[str]:
        """
        Generate backup codes.
        """
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        return codes
    
    def is_configured(self, user) -> bool:
        """
        Check if backup codes are configured.
        """
        from nova2fa.models import UserTwoFactorSettings
        
        try:
            settings_obj = UserTwoFactorSettings.objects.get(user=user)
            return len(settings_obj.backup_codes) > 0
        except UserTwoFactorSettings.DoesNotExist:
            return False