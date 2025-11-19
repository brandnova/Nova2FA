from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
    totp_secret = models.CharField(max_length=255, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    used_backup_codes = models.JSONField(default=list, blank=True)
    last_verified = models.DateTimeField(null=True, blank=True)
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
        """
        code = code.upper().strip()
        if code in self.backup_codes and code not in self.used_backup_codes:
            self.used_backup_codes.append(code)
            self.save(update_fields=['used_backup_codes'])
            return True
        return False

    def get_available_backup_codes(self):
        """
        Get list of available (unused) backup codes.
        """
        return [code for code in self.backup_codes if code not in self.used_backup_codes]

    def get_used_backup_codes(self):
        """
        Get list of used backup codes.
        """
        return self.used_backup_codes
    
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