"""
Pytest configuration and fixtures for Nova2FA tests.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from datetime import timedelta

from nova2fa.models import UserTwoFactorSettings, EmailOTP
from nova2fa.methods.backup_codes import BackupCodesMethod

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def user2(db):
    """Create a second test user for tests that need multiple users."""
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(user):
    """Create a client with authenticated user."""
    client = Client()
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def two_factor_settings(user):
    """
    Create disabled UserTwoFactorSettings for test user.
    Note: Don't use this with enabled_2fa_settings for the same user.
    """
    # Check if settings already exist (from another fixture)
    existing = UserTwoFactorSettings.objects.filter(user=user).first()
    if existing:
        return existing
    
    return UserTwoFactorSettings.objects.create(
        user=user,
        is_enabled=False,
        method='totp'
    )


@pytest.fixture
def enabled_2fa_settings(user2):
    """
    Create enabled UserTwoFactorSettings with backup codes.
    Uses user2 to avoid conflicts with two_factor_settings fixture.
    """
    # Check if settings already exist for user2
    existing = UserTwoFactorSettings.objects.filter(user=user2).first()
    if existing:
        return existing
    
    backup_method = BackupCodesMethod()
    backup_data = backup_method.setup(user2)
    
    return UserTwoFactorSettings.objects.create(
        user=user2,
        is_enabled=True,
        method='totp',
        backup_codes=backup_data['hashed_codes'],
        last_verified=timezone.now()
    )


@pytest.fixture
def email_otp(user):
    """Create a valid EmailOTP."""
    return EmailOTP.objects.create(
        user=user,
        code='123456',
        expires_at=timezone.now() + timedelta(minutes=10),
        is_used=False
    )


@pytest.fixture
def expired_email_otp(user):
    """Create an expired EmailOTP."""
    return EmailOTP.objects.create(
        user=user,
        code='654321',
        expires_at=timezone.now() - timedelta(minutes=1),
        is_used=False
    )
