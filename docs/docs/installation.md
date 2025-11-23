# Installation Guide

This guide will walk you through installing Nova2FA in your Django project.

## Requirements

Before installing Nova2FA, ensure you have:

- Python 3.8 or higher
- Django 4.2 or higher
- A working Django project with authentication

## Step 1: Install the Package

Install Nova2FA using pip:

```bash
pip install nova2fa
```

This will install Nova2FA and its dependencies:

- `pyotp` - For TOTP implementation
- `qrcode` - For QR code generation
- `Pillow` - For image processing
- `cryptography` - For encryption (v1.1.0+)

## Step 2: Add to INSTALLED_APPS

In your Django project's `settings.py`, add `nova2fa` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'myapp',

    # Third-party apps
    'nova2fa',  # Add this line
]
```

!!! warning "Order Matters"
Make sure `nova2fa` is added **after** Django's built-in apps, especially `django.contrib.auth` and `django.contrib.sessions`.

## Step 3: Add Middleware

Add Nova2FA middleware to your `MIDDLEWARE` setting, right after `AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'nova2fa.middleware.Nova2FAMiddleware',  # Add this line
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

!!! danger "Critical Placement"
The middleware **must** come after `AuthenticationMiddleware` and `SessionMiddleware` to function correctly.

## Step 4: Include URLs

Add Nova2FA URLs to your project's main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('2fa/', include('nova2fa.urls')),  # Add this line
    # ... your other URL patterns
]
```

You can use any URL prefix you prefer (e.g., `'security/'`, `'mfa/'`, etc.).

## Step 5: Security Configuration (v1.1.0+)

!!! important "Required for v1.1.0+"
Nova2FA v1.1.0 introduces encryption for TOTP secrets. Configure the encryption key in `settings.py`:

```python
# Optional: Dedicated encryption key for Nova2FA
# If not set, Django's SECRET_KEY will be used
NOVA2FA_SECRET_KEY = 'your-secret-encryption-key-here'

# Optional: Brute force protection settings
NOVA2FA_MAX_ATTEMPTS = 5  # Max failed verification attempts (default: 5)
NOVA2FA_LOCKOUT_DURATION_MINUTES = 15  # Account lockout duration (default: 15)
```

!!! warning "Security Best Practice"
Use a separate `NOVA2FA_SECRET_KEY` instead of reusing `SECRET_KEY`. Generate a strong key:
`python
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    `

## Step 6: Configure Email (for Email OTP)

If you plan to use Email OTP, configure your email backend in `settings.py`:

````python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
````

For development, you can use the console backend:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Step 7: Run Migrations

Create and apply database migrations:

```bash
python manage.py migrate nova2fa
```

This creates two tables:

- `nova2fa_usertwofactorsettings` - Stores user 2FA preferences
- `nova2fa_emailotp` - Stores email OTP codes

## Step 8: Basic Configuration

Add basic Nova2FA configuration to your `settings.py`:

```python
# Nova2FA Configuration
NOVA2FA_ENABLED_METHODS = ['email', 'totp']
NOVA2FA_TOTP_ISSUER = 'YourApp'
```

See [Configuration Reference](configuration.md) for all available options.

## Step 8: Verify Installation

Start your development server:

```bash
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/2fa/settings/` (after logging in) to verify Nova2FA is installed correctly.

## Next Steps

- Follow the [Quick Start Tutorial](quickstart.md) to set up your first 2FA flow
- Read the [Configuration Reference](configuration.md) to customize Nova2FA
- Check out the [Customization Guide](customization.md) to style the templates

## Troubleshooting

### ImportError: No module named 'nova2fa'

**Solution**: Ensure nova2fa is installed in your current Python environment:

```bash
pip list | grep nova2fa
```

### MiddlewareNotUsed Error

**Solution**: Make sure the middleware is placed **after** `AuthenticationMiddleware` in your `MIDDLEWARE` setting.

### Migration Errors

**Solution**: If you see migration errors, try:

```bash
python manage.py migrate nova2fa --fake-initial
```

### Email OTP Not Sending

**Solution**: Check your email configuration and ensure you can send emails:

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

---

## Migrating from v1.0.x to v1.1.0

!!! warning "Breaking Changes in v1.1.0"
Version 1.1.0 introduces security enhancements that require user action.

### What Changed

**Security Enhancements:**

- TOTP secrets are now encrypted at rest
- Backup codes are now hashed (like passwords)
- Account lockout after failed verification attempts
- Rate limiting on verification endpoints

### Migration Steps

#### 1. Update the Package

```bash
pip install --upgrade nova2fa
```

#### 2. Configure Encryption Key

Add to your `settings.py`:

```python
# Generate a new key with:
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())

NOVA2FA_SECRET_KEY = 'your-new-encryption-key-here'
```

#### 3. Run Migrations

```bash
python manage.py migrate nova2fa
```

This adds new fields:

- `failed_attempts` - Tracks failed verification attempts
- `locked_until` - Stores account lockout expiration
- `totp_secret` max_length increased to 512 (for encrypted values)

#### 4. Notify Users

!!! important "User Action Required"
**All users must regenerate their backup codes** after the upgrade.

Old backup codes (plain text) will no longer work. Users should:

1. Log in to their account
2. Navigate to 2FA settings
3. Click "Regenerate Backup Codes"
4. Save the new codes securely

**TOTP secrets:** Existing TOTP setups will continue to work (backward compatible), but new setups will use encryption.

#### 5. Update Templates (Optional)

If you've customized Nova2FA templates, review them for:

- New lockout messages
- One-time backup code display behavior
- Failed attempts counter display

### Rollback Plan

If you need to rollback to v1.0.x:

```bash
# 1. Downgrade package
pip install nova2fa==1.0.0

# 2. Revert migrations
python manage.py migrate nova2fa 0001

# 3. Remove new settings from settings.py
# Remove: NOVA2FA_SECRET_KEY, NOVA2FA_MAX_ATTEMPTS, NOVA2FA_LOCKOUT_DURATION_MINUTES
```

!!! caution
After rollback, users will need to regenerate backup codes again.

### Testing the Migration

After migrating, test these scenarios:

1. **TOTP Verification** - Existing TOTP should still work
2. **Backup Codes** - Old codes won't work (expected)
3. **New Setup** - New TOTP setups should use encryption
4. **Account Lockout** - Test 5 failed attempts triggers lockout
5. **Backup Code Regeneration** - Users can generate new hashed codes

### Need Help?

If you encounter issues during migration:

1. Check the [CHANGELOG](https://github.com/yourusername/nova2fa/blob/main/CHANGELOG.md)
2. Review the [Security Guide](security.md)
3. Open an issue on [GitHub](https://github.com/yourusername/nova2fa/issues)
