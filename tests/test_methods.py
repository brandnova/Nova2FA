"""
Tests for Nova2FA authentication methods.
"""
import pytest
import pyotp
from django.contrib.auth.hashers import check_password

from nova2fa.methods.totp import TOTPMethod
from nova2fa.methods.email_otp import EmailOTPMethod
from nova2fa.methods.backup_codes import BackupCodesMethod
from nova2fa.models import UserTwoFactorSettings


@pytest.mark.django_db
class TestTOTPMethod:
    """Tests for TOTP authentication method."""
    
    def test_setup_generates_secret(self, user):
        """Test that setup generates encrypted secret and QR code."""
        method = TOTPMethod()
        setup_data = method.setup(user)
        
        assert 'secret' in setup_data  # Encrypted
        assert 'secret_display' in setup_data  # Plain text
        assert 'qr_code_path' in setup_data
        assert 'totp_uri' in setup_data
        
        # Encrypted secret should be different from plain
        assert setup_data['secret'] != setup_data['secret_display']
    
    def test_verify_valid_token(self, user, two_factor_settings):
        """Test verifying a valid TOTP token."""
        method = TOTPMethod()
        setup_data = method.setup(user)
        
        # Store encrypted secret
        two_factor_settings.totp_secret = setup_data['secret']
        two_factor_settings.save()
        
        # Generate valid token using plain secret
        totp = pyotp.TOTP(setup_data['secret_display'])
        valid_token = totp.now()
        
        assert method.verify(user, valid_token)
    
    def test_verify_invalid_token(self, user, two_factor_settings):
        """Test that invalid token fails verification."""
        method = TOTPMethod()
        setup_data = method.setup(user)
        
        two_factor_settings.totp_secret = setup_data['secret']
        two_factor_settings.save()
        
        assert not method.verify(user, '000000')
    
    def test_verify_resets_failed_attempts_on_success(self, user, two_factor_settings):
        """Test that successful verification resets failed attempts."""
        method = TOTPMethod()
        setup_data = method.setup(user)
        
        two_factor_settings.totp_secret = setup_data['secret']
        two_factor_settings.failed_attempts = 3
        two_factor_settings.save()
        
        totp = pyotp.TOTP(setup_data['secret_display'])
        valid_token = totp.now()
        
        method.verify(user, valid_token)
        two_factor_settings.refresh_from_db()
        
        assert two_factor_settings.failed_attempts == 0


@pytest.mark.django_db
class TestEmailOTPMethod:
    """Tests for Email OTP authentication method."""
    
    def test_send_creates_otp(self, user):
        """Test that send creates an OTP record."""
        method = EmailOTPMethod()
        
        # Note: This will try to send email, which may fail in tests
        # In real tests, you'd mock the email backend
        result = method.send(user)
        
        # Check OTP was created
        from nova2fa.models import EmailOTP
        otp = EmailOTP.objects.filter(user=user).first()
        assert otp is not None
        assert len(otp.code) == 6
    
    def test_is_configured_with_email(self, user):
        """Test that user with email is considered configured."""
        method = EmailOTPMethod()
        assert method.is_configured(user)


@pytest.mark.django_db
class TestBackupCodesMethod:
    """Tests for Backup Codes authentication method."""
    
    def test_setup_generates_codes(self, user):
        """Test that setup generates backup codes."""
        method = BackupCodesMethod()
        setup_data = method.setup(user)
        
        assert 'codes' in setup_data
        assert 'hashed_codes' in setup_data
        assert len(setup_data['codes']) == 8
        assert len(setup_data['hashed_codes']) == 8
        
        # Codes should be 8 characters
        for code in setup_data['codes']:
            assert len(code) == 8
    
    def test_codes_are_hashed(self, user):
        """Test that hashed codes are actually hashed."""
        method = BackupCodesMethod()
        setup_data = method.setup(user)
        
        plain_code = setup_data['codes'][0]
        hashed_code = setup_data['hashed_codes'][0]
        
        # Hashed code should be different from plain
        assert plain_code != hashed_code
        
        # Should be verifiable with check_password
        assert check_password(plain_code, hashed_code)
    
    def test_verify_valid_code(self, user2, enabled_2fa_settings):
        """Test verifying a valid backup code."""
        method = BackupCodesMethod()
        setup_data = method.setup(user2)
        
        enabled_2fa_settings.backup_codes = setup_data['hashed_codes']
        enabled_2fa_settings.save()
        
        plain_code = setup_data['codes'][0]
        assert method.verify(user2, plain_code)
    
    def test_verify_invalid_code(self, user2, enabled_2fa_settings):
        """Test that invalid code fails verification."""
        method = BackupCodesMethod()
        setup_data = method.setup(user2)
        
        enabled_2fa_settings.backup_codes = setup_data['hashed_codes']
        enabled_2fa_settings.save()
        
        assert not method.verify(user2, 'INVALID1')
