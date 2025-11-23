# API Reference

This page documents Nova2FA's Python API for programmatic usage.

## Models

### UserTwoFactorSettings

Stores user 2FA configuration and state.

```python
from nova2fa.models import UserTwoFactorSettings

# Get user's settings
settings = UserTwoFactorSettings.objects.get(user=user)
```

#### Fields

| Field               | Type          | Description                              |
| ------------------- | ------------- | ---------------------------------------- |
| `user`              | ForeignKey    | Reference to Django user                 |
| `is_enabled`        | BooleanField  | Whether 2FA is enabled                   |
| `method`            | CharField     | Active method ('email' or 'totp')        |
| `totp_secret`       | CharField     | TOTP secret key (encrypted in v1.1.0+)   |
| `backup_codes`      | JSONField     | List of backup codes (hashed in v1.1.0+) |
| `used_backup_codes` | JSONField     | List of used backup codes                |
| `failed_attempts`   | IntegerField  | Failed verification attempts (v1.1.0+)   |
| `locked_until`      | DateTimeField | Account lockout expiration (v1.1.0+)     |
| `last_verified`     | DateTimeField | Last verification timestamp              |
| `created_at`        | DateTimeField | When settings were created               |
| `updated_at`        | DateTimeField | Last update timestamp                    |

#### Methods

**`needs_verification()`**

Check if user needs to verify 2FA.

```python
if settings.needs_verification():
    # Redirect to verification
    redirect('nova2fa:verify')
```

**Returns:** `bool`

---

**`update_last_verified()`**

Update the last verified timestamp to now.

```python
settings.update_last_verified()
```

**Returns:** `None`

---

**`verify_backup_code(code)`**

Verify a backup code and mark it as used.

```python
if settings.verify_backup_code('ABCD1234'):
    print("Valid backup code!")
```

**Parameters:**

- `code` (str): The backup code to verify

**Returns:** `bool` - True if valid, False otherwise

---

**`get_available_backup_codes()`**

Get list of unused backup codes.

```python
codes = settings.get_available_backup_codes()
print(f"You have {len(codes)} codes remaining")
```

**Returns:** `list` of strings

---

**`has_available_backup_codes()`**

Check if user has any unused backup codes.

```python
if not settings.has_available_backup_codes():
    # Warn user to generate new codes
    pass
```

**Returns:** `bool`

---

### EmailOTP

Stores email one-time passwords.

```python
from nova2fa.models import EmailOTP

# Get latest OTP for user
otp = EmailOTP.objects.filter(user=user).latest('created_at')
```

#### Fields

| Field        | Type          | Description               |
| ------------ | ------------- | ------------------------- |
| `user`       | ForeignKey    | Reference to Django user  |
| `code`       | CharField     | The 6-digit OTP code      |
| `created_at` | DateTimeField | When OTP was created      |
| `expires_at` | DateTimeField | When OTP expires          |
| `is_used`    | BooleanField  | Whether OTP has been used |

#### Methods

**`is_valid()`**

Check if OTP is still valid (not used and not expired).

```python
if otp.is_valid():
    # OTP can be used
    pass
```

**Returns:** `bool`

---

**`mark_as_used()`**

Mark the OTP as used.

```python
otp.mark_as_used()
```

**Returns:** `None`

---

## Registry

### register_method()

Register a custom 2FA method.

```python
from nova2fa.registry import register_method
from myapp.methods import SMSMethod

register_method('sms', SMSMethod())
```

**Parameters:**

- `code` (str): Unique identifier for the method
- `handler` (Base2FAMethod): Instance of method handler

**Returns:** `None`

---

### get_method()

Get a registered 2FA method.

```python
from nova2fa.registry import get_method

method = get_method('email')
if method:
    method.send(user)
```

**Parameters:**

- `code` (str): Method identifier

**Returns:** `Base2FAMethod` instance or `None`

---

### get_enabled_methods()

Get all enabled methods based on settings.

```python
from nova2fa.registry import get_enabled_methods

methods = get_enabled_methods()
for code, handler in methods.items():
    print(f"{code}: {handler.verbose_name}")
```

**Returns:** `dict` of {code: handler}

---

## Methods

### Base2FAMethod

Base class for all 2FA methods.

```python
from nova2fa.methods.base import Base2FAMethod

class CustomMethod(Base2FAMethod):
    name = "custom"
    verbose_name = "Custom Method"

    def send(self, user):
        # Implementation
        return True

    def verify(self, user, token):
        # Implementation
        return True
```

#### Required Attributes

- `name` (str): Unique method identifier
- `verbose_name` (str): Human-readable name

#### Required Methods

**`send(user)`**

Send the 2FA token to the user.

**Parameters:**

- `user`: Django user instance

**Returns:** `bool` - True if sent successfully

---

**`verify(user, token)`**

Verify the provided token.

**Parameters:**

- `user`: Django user instance
- `token` (str): Token to verify

**Returns:** `bool` - True if valid

---

#### Optional Methods

**`setup(user)`**

Perform setup for this method (e.g., generate secret).

**Parameters:**

- `user`: Django user instance

**Returns:** `dict` - Setup data

---

**`is_configured(user)`**

Check if method is configured for user.

**Parameters:**

- `user`: Django user instance

**Returns:** `bool`

---

### EmailOTPMethod

Email-based OTP method.

```python
from nova2fa.methods import EmailOTPMethod

method = EmailOTPMethod()
method.send(user)  # Sends OTP via email
method.verify(user, '123456')  # Verifies code
```

---

### TOTPMethod

Time-based OTP method (authenticator apps).

```python
from nova2fa.methods import TOTPMethod

method = TOTPMethod()
setup_data = method.setup(user)  # Returns QR code path, secret
method.verify(user, '123456')  # Verifies TOTP code
```

---

### BackupCodesMethod

Backup codes method.

```python
from nova2fa.methods import BackupCodesMethod

method = BackupCodesMethod()
setup_data = method.setup(user)  # Generates new codes
method.verify(user, 'ABCD1234')  # Verifies backup code
```

---

## Utilities

### Checking 2FA Status

```python
from nova2fa.models import UserTwoFactorSettings

def user_has_2fa(user):
    """Check if user has 2FA enabled."""
    try:
        settings = UserTwoFactorSettings.objects.get(user=user)
        return settings.is_enabled
    except UserTwoFactorSettings.DoesNotExist:
        return False
```

### Programmatically Enabling 2FA

```python
from nova2fa.models import UserTwoFactorSettings
from nova2fa.methods import EmailOTPMethod, BackupCodesMethod

def enable_email_2fa(user):
    """Enable email 2FA for a user."""
    settings, created = UserTwoFactorSettings.objects.get_or_create(user=user)

    # Generate backup codes
    backup_method = BackupCodesMethod()
    backup_data = backup_method.setup(user)

    # Enable 2FA
    settings.is_enabled = True
    settings.method = 'email'
    settings.backup_codes = backup_data['codes']
    settings.save()

    return settings
```

### Getting 2FA Statistics

```python
from nova2fa.models import UserTwoFactorSettings
from django.db.models import Count

def get_2fa_stats():
    """Get 2FA adoption statistics."""
    total_users = UserTwoFactorSettings.objects.count()
    enabled = UserTwoFactorSettings.objects.filter(is_enabled=True).count()

    methods = UserTwoFactorSettings.objects.filter(
        is_enabled=True
    ).values('method').annotate(count=Count('method'))

    return {
        'total_users': total_users,
        'enabled': enabled,
        'adoption_rate': (enabled / total_users * 100) if total_users > 0 else 0,
        'methods': dict((m['method'], m['count']) for m in methods)
    }
```

### Session Management

```python
from django.utils import timezone

def mark_2fa_verified(request):
    """Mark session as 2FA verified."""
    request.session['nova2fa_verified_at'] = timezone.now().isoformat()
    request.session.save()

def clear_2fa_verification(request):
    """Clear 2FA verification from session."""
    if 'nova2fa_verified_at' in request.session:
        del request.session['nova2fa_verified_at']
    request.session.save()
```

## Middleware

### Nova2FAMiddleware

The middleware automatically enforces 2FA verification.

**Configuration:**

```python
# settings.py
MIDDLEWARE = [
    # ...
    'nova2fa.middleware.Nova2FAMiddleware',
]
```

**Behavior:**

1. Checks if user is authenticated
2. Checks if path is exempt
3. Checks if user has 2FA enabled
4. Checks if session is verified
5. Redirects to verification if needed

---

## Signals

Nova2FA creates `UserTwoFactorSettings` automatically when users are created:

```python
# In your app
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user('john', 'john@example.com', 'password')

# Nova2FA automatically creates settings
assert hasattr(user, 'nova2fa_settings')
```

---

## Example: Custom Dashboard

```python
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from nova2fa.models import UserTwoFactorSettings, EmailOTP
from django.utils import timezone
from datetime import timedelta

@login_required
def security_dashboard(request):
    """Custom security dashboard with 2FA info."""
    try:
        settings = UserTwoFactorSettings.objects.get(user=request.user)
        has_2fa = settings.is_enabled
        method = settings.get_method_display() if has_2fa else None

        # Get recent OTP attempts
        recent_otps = EmailOTP.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        # Check backup codes
        backup_codes_remaining = len(settings.get_available_backup_codes())

    except UserTwoFactorSettings.DoesNotExist:
        has_2fa = False
        method = None
        recent_otps = 0
        backup_codes_remaining = 0

    context = {
        'has_2fa': has_2fa,
        'method': method,
        'recent_otps': recent_otps,
        'backup_codes_remaining': backup_codes_remaining,
    }

    return render(request, 'dashboard.html', context)
```

## Next Steps

- Review [Customization Guide](customization.md) for template customization
- Check [GitHub Repository](https://github.com/brandnova/Nova2FA) for examples
