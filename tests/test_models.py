"""
Tests for Nova2FA models.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password

from nova2fa.models import UserTwoFactorSettings, EmailOTP


@pytest.mark.django_db
class TestUserTwoFactorSettings:
    """Tests for UserTwoFactorSettings model."""
    
    def test_create_settings(self, two_factor_settings):
        """Test creating 2FA settings via fixture."""
        # Verify the fixture created settings correctly
        assert two_factor_settings.user.username == 'testuser'
        assert not two_factor_settings.is_enabled
        assert two_factor_settings.method == 'totp'
    
    def test_verify_backup_code_success(self, user2, enabled_2fa_settings):
        """Test successful backup code verification."""
        # Get a plain text code (we need to generate one)
        from nova2fa.methods.backup_codes import BackupCodesMethod
        backup_method = BackupCodesMethod()
        backup_data = backup_method.setup(user2)
        
        # Update settings with new codes
        enabled_2fa_settings.backup_codes = backup_data['hashed_codes']
        enabled_2fa_settings.save()
        
        # Verify with plain text code
        plain_code = backup_data['codes'][0]
        assert enabled_2fa_settings.verify_backup_code(plain_code)
        
        # Verify code is marked as used
        assert len(enabled_2fa_settings.used_backup_codes) == 1
    
    def test_verify_backup_code_already_used(self, user2, enabled_2fa_settings):
        """Test that used backup codes cannot be reused."""
        from nova2fa.methods.backup_codes import BackupCodesMethod
        backup_method = BackupCodesMethod()
        backup_data = backup_method.setup(user2)
        
        enabled_2fa_settings.backup_codes = backup_data['hashed_codes']
        enabled_2fa_settings.save()
        
        plain_code = backup_data['codes'][0]
        
        # First use should succeed
        assert enabled_2fa_settings.verify_backup_code(plain_code)
        
        # Second use should fail
        assert not enabled_2fa_settings.verify_backup_code(plain_code)
    
    def test_is_locked_after_max_attempts(self, enabled_2fa_settings):
        """Test account lockout after max failed attempts."""
        # Increment failed attempts to max
        for _ in range(5):
            enabled_2fa_settings.increment_failed_attempts()
        
        assert enabled_2fa_settings.is_locked()
        assert enabled_2fa_settings.locked_until is not None
    
    def test_reset_failed_attempts(self, enabled_2fa_settings):
        """Test resetting failed attempts."""
        enabled_2fa_settings.failed_attempts = 3
        enabled_2fa_settings.save()
        
        enabled_2fa_settings.reset_failed_attempts()
        
        assert enabled_2fa_settings.failed_attempts == 0
        assert enabled_2fa_settings.locked_until is None
    
    def test_get_available_backup_codes_count(self, user2, enabled_2fa_settings):
        """Test getting count of available backup codes."""
        from nova2fa.methods.backup_codes import BackupCodesMethod
        backup_method = BackupCodesMethod()
        backup_data = backup_method.setup(user2)
        
        enabled_2fa_settings.backup_codes = backup_data['hashed_codes']
        enabled_2fa_settings.save()
        
        # All codes should be available
        assert enabled_2fa_settings.get_available_backup_codes_count() == 8
        
        # Use one code
        enabled_2fa_settings.verify_backup_code(backup_data['codes'][0])
        
        # Should have 7 available
        assert enabled_2fa_settings.get_available_backup_codes_count() == 7


@pytest.mark.django_db
class TestEmailOTP:
    """Tests for EmailOTP model."""
    
    def test_create_email_otp(self, user):
        """Test creating an email OTP."""
        otp = EmailOTP.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        assert otp.user == user
        assert otp.code == '123456'
        assert not otp.is_used
    
    def test_is_valid_for_fresh_otp(self, email_otp):
        """Test that fresh OTP is valid."""
        assert email_otp.is_valid()
    
    def test_is_valid_for_expired_otp(self, expired_email_otp):
        """Test that expired OTP is invalid."""
        assert not expired_email_otp.is_valid()
    
    def test_is_valid_for_used_otp(self, email_otp):
        """Test that used OTP is invalid."""
        email_otp.mark_as_used()
        assert not email_otp.is_valid()
    
    def test_mark_as_used(self, email_otp):
        """Test marking OTP as used."""
        assert not email_otp.is_used
        email_otp.mark_as_used()
        assert email_otp.is_used
