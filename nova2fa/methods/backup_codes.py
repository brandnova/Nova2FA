"""
Backup codes method implementation.
"""
import random
import string
from django.conf import settings
from .base import Base2FAMethod


class BackupCodesMethod(Base2FAMethod):
    """
    Backup codes for account recovery.
    """
    name = "backup"
    verbose_name = "Backup Codes"
    
    def send(self, user):
        """
        Backup codes don't need to be sent.
        """
        return True
    
    def verify(self, user, token):
        """
        Verify a backup code.
        """
        from nova2fa.models import UserTwoFactorSettings
        
        try:
            settings_obj = UserTwoFactorSettings.objects.get(user=user)
            return settings_obj.verify_backup_code(token)
        except UserTwoFactorSettings.DoesNotExist:
            return False
    
    def setup(self, user):
        """
        Generate new backup codes.
        """
        count = getattr(settings, 'NOVA2FA_BACKUP_CODE_COUNT', 8)
        codes = self._generate_codes(count)
        
        return {
            'codes': codes
        }
    
    def _generate_codes(self, count=8):
        """
        Generate backup codes.
        """
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        return codes
    
    def is_configured(self, user):
        """
        Check if backup codes are configured.
        """
        from nova2fa.models import UserTwoFactorSettings
        
        try:
            settings_obj = UserTwoFactorSettings.objects.get(user=user)
            return len(settings_obj.backup_codes) > 0
        except UserTwoFactorSettings.DoesNotExist:
            return False