from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
import datetime
import logging

logger = logging.getLogger(__name__)


class UserTwoFactorSettings(models.Model):
    """
    Model to store user's two-factor authentication settings.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nova2fa_settings'
    )
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(
        max_length=20,
        choices=[],  # Will be populated dynamically
        default='totp'
    )
    totp_secret = models.CharField(max_length=512, blank=True, null=True)  # Encrypted, needs more space
    backup_codes = models.JSONField(default=list, blank=True)  # Now stores hashed codes
    used_backup_codes = models.JSONField(default=list, blank=True)  # Stores hashed codes
    last_verified = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.IntegerField(default=0)  # Track failed verification attempts
    locked_until = models.DateTimeField(null=True, blank=True)  # Account lockout timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - 2FA Settings"

    def needs_verification(self):
        """
        Check if the user needs to verify 2FA.
        """
        if not self.is_enabled:
            return False

        # Check session verification
        from django.contrib import auth
        request = getattr(auth, 'get_request', lambda: None)()
        if request and request.session.get('nova2fa_verified_at'):
            try:
                verified_at = timezone.datetime.fromisoformat(
                    request.session['nova2fa_verified_at']
                )
                
                if timezone.is_naive(verified_at):
                    verified_at = timezone.make_aware(verified_at)
                
                verification_window_hours = getattr(
                    settings,
                    'NOVA2FA_VERIFICATION_WINDOW_DAYS',
                    14
                ) * 24
                now = timezone.now()
                verification_valid = (now - verified_at) < datetime.timedelta(
                    hours=verification_window_hours
                )
                
                if verification_valid:
                    return False
            except Exception as e:
                logger.error(f"Error checking 2FA session verification: {str(e)}")

        if self.last_verified:
            verification_window_hours = getattr(
                settings,
                'NOVA2FA_VERIFICATION_WINDOW_DAYS',
                14
            ) * 24
            now = timezone.now()
            verification_valid = (now - self.last_verified) < datetime.timedelta(
                hours=verification_window_hours
            )
            
            if verification_valid:
                return False

        return True

    def update_last_verified(self):
        """
        Update the last_verified timestamp.
        """
        self.last_verified = timezone.now()
        self.save(update_fields=['last_verified'])

    def verify_backup_code(self, code):
        """
        Verify a backup code and mark it as used.
        Backup codes are stored as hashed values for security.
        """
        code = code.upper().strip()
        
        # Check if account is locked
        if self.is_locked():
            return False
        
        # Check each hashed backup code
        for hashed_code in self.backup_codes:
            if hashed_code in self.used_backup_codes:
                continue
            
            if check_password(code, hashed_code):
                # Mark as used by storing the hash
                self.used_backup_codes.append(hashed_code)
                self.reset_failed_attempts()
                self.save(update_fields=['used_backup_codes', 'failed_attempts'])
                return True
        
        # Increment failed attempts
        self.increment_failed_attempts()
        return False

    def get_available_backup_codes(self):
        """
        Get count of available (unused) backup codes.
        Note: Codes are hashed, so we can't return the actual codes.
        """
        return [code for code in self.backup_codes if code not in self.used_backup_codes]

    def get_available_backup_codes_count(self):
        """
        Get count of available backup codes.
        """
        return len(self.get_available_backup_codes())

    def get_used_backup_codes(self):
        """
        Get list of used backup codes (hashed).
        """
        return self.used_backup_codes
    
    def is_locked(self):
        """
        Check if account is locked due to too many failed attempts.
        """
        if not self.locked_until:
            return False
        
        if timezone.now() < self.locked_until:
            return True
        
        # Lock period expired, reset
        self.locked_until = None
        self.failed_attempts = 0
        self.save(update_fields=['locked_until', 'failed_attempts'])
        return False
    
    def increment_failed_attempts(self):
        """
        Increment failed verification attempts and lock if threshold exceeded.
        """
        self.failed_attempts += 1
        
        # Lock account after 5 failed attempts for 15 minutes
        max_attempts = getattr(settings, 'NOVA2FA_MAX_ATTEMPTS', 5)
        lockout_duration = getattr(settings, 'NOVA2FA_LOCKOUT_DURATION_MINUTES', 15)
        
        if self.failed_attempts >= max_attempts:
            self.locked_until = timezone.now() + datetime.timedelta(minutes=lockout_duration)
            logger.warning(f"User {self.user.email} locked out due to {self.failed_attempts} failed 2FA attempts")
        
        self.save(update_fields=['failed_attempts', 'locked_until'])
    
    def reset_failed_attempts(self):
        """
        Reset failed attempts counter after successful verification.
        """
        self.failed_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_attempts', 'locked_until'])
    
    def get_method_display(self):
        """Get human-readable method name."""
        from .registry import get_method
        method = get_method(self.method)
        return method.verbose_name if method else self.method.upper()

    def has_available_backup_codes(self):
        """
        Check if there are any available backup codes.
        """
        return len(self.get_available_backup_codes()) > 0
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_enabled']),
            models.Index(fields=['last_verified']),
            models.Index(fields=['locked_until']),
        ]
        verbose_name = _('Two Factor Settings')
        verbose_name_plural = _('Two Factor Settings')


class EmailOTP(models.Model):
    """
    Stores email one-time password codes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nova2fa_email_otps'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"
    
    def is_valid(self):
        """
        Check if the OTP is still valid.
        """
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """
        Mark the OTP as used.
        """
        self.is_used = True
        self.save(update_fields=['is_used'])

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_used', 'expires_at']),
            models.Index(fields=['created_at']),
        ]
        get_latest_by = 'created_at'