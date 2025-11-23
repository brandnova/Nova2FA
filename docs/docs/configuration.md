# Configuration Reference

This page documents all available configuration options for Nova2FA.

## Overview

All Nova2FA configuration is done through Django's settings system. Add configuration variables to your project's `settings.py` file.

Example:

```python
# settings.py
NOVA2FA_ENABLED_METHODS = ['email', 'totp']
NOVA2FA_VERIFICATION_WINDOW_DAYS = 14
```

## Core Settings

### NOVA2FA_ENABLED_METHODS

**Type**: `list`  
**Default**: `['email', 'totp']`  
**Description**: List of enabled 2FA methods

```python
# Enable only email
NOVA2FA_ENABLED_METHODS = ['email']

# Enable only TOTP
NOVA2FA_ENABLED_METHODS = ['totp']

# Enable both (default)
NOVA2FA_ENABLED_METHODS = ['email', 'totp']

# Enable custom method (if you've created one)
NOVA2FA_ENABLED_METHODS = ['email', 'totp', 'sms']
```

Available built-in methods:

- `'email'` - Email OTP
- `'totp'` - Authenticator App (TOTP)

### NOVA2FA_VERIFICATION_WINDOW_DAYS

**Type**: `int`  
**Default**: `14`  
**Description**: Number of days a user remains verified before requiring re-verification

```python
# Verify once per week
NOVA2FA_VERIFICATION_WINDOW_DAYS = 7

# Verify once per month
NOVA2FA_VERIFICATION_WINDOW_DAYS = 30

# Require verification on every session (not recommended)
NOVA2FA_VERIFICATION_WINDOW_DAYS = 0
```

!!! note
This affects how often users need to enter their 2FA code. Balance security with user experience.

## Email OTP Settings

### NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES

**Type**: `int`  
**Default**: `10`  
**Description**: How long email OTP codes remain valid (in minutes)

```python
# 5 minute expiry (more secure, less convenient)
NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES = 5

# 15 minute expiry (less secure, more convenient)
NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES = 15
```

### NOVA2FA_EMAIL_SUBJECT

**Type**: `str`  
**Default**: `'Your One-Time Password'`  
**Description**: Subject line for OTP emails

```python
NOVA2FA_EMAIL_SUBJECT = 'Your MyApp Verification Code'
```

## TOTP Settings

### NOVA2FA_TOTP_ISSUER

**Type**: `str`  
**Default**: `'Nova2FA'`  
**Description**: Issuer name shown in authenticator apps

```python
NOVA2FA_TOTP_ISSUER = 'MyCompany'
```

This appears in authenticator apps like:

```
MyCompany (user@example.com)
123 456
```

!!! tip
Use your application or company name for easy identification by users.

## Backup Codes Settings

### NOVA2FA_BACKUP_CODE_COUNT

**Type**: `int`  
**Default**: `8`  
**Description**: Number of backup codes to generate

```python
# Generate 10 backup codes
NOVA2FA_BACKUP_CODE_COUNT = 10

# Generate 5 backup codes
NOVA2FA_BACKUP_CODE_COUNT = 5
```

## Security Settings

### NOVA2FA_SECRET_KEY (v1.1.0+)

**Type**: `str`  
**Default**: Falls back to `SECRET_KEY`  
**Description**: Encryption key for TOTP secrets  
**Required**: Recommended for v1.1.0+

```python
# Generate a unique key for Nova2FA
from django.core.management.utils import get_random_secret_key
NOVA2FA_SECRET_KEY = get_random_secret_key()
```

!!! warning "Security Best Practice"
Use a dedicated encryption key separate from Django's `SECRET_KEY`. Store in environment variables, never commit to version control.

### NOVA2FA_MAX_ATTEMPTS (v1.1.0+)

**Type**: `int`  
**Default**: `5`  
**Description**: Maximum failed verification attempts before account lockout

```python
# Stricter lockout (3 attempts)
NOVA2FA_MAX_ATTEMPTS = 3

# More lenient (10 attempts)
NOVA2FA_MAX_ATTEMPTS = 10
```

### NOVA2FA_LOCKOUT_DURATION_MINUTES (v1.1.0+)

**Type**: `int`  
**Default**: `15`  
**Description**: Account lockout duration in minutes after max failed attempts

```python
# 30 minute lockout
NOVA2FA_LOCKOUT_DURATION_MINUTES = 30

# 5 minute lockout (less secure)
NOVA2FA_LOCKOUT_DURATION_MINUTES = 5
```

!!! note "Brute Force Protection"
These settings work together to prevent brute force attacks. After `NOVA2FA_MAX_ATTEMPTS` failed verifications, the account is locked for `NOVA2FA_LOCKOUT_DURATION_MINUTES`.

### NOVA2FA_EXEMPT_SUPERUSERS

**Type**: `bool`  
**Default**: `False`  
**Description**: Exempt superusers from 2FA verification

```python
# Exempt superusers (useful for emergency access)
NOVA2FA_EXEMPT_SUPERUSERS = True

# Require 2FA for everyone (recommended)
NOVA2FA_EXEMPT_SUPERUSERS = False
```

!!! warning "Security Consideration"
Exempting superusers reduces security. Only enable this if you have other access controls in place.

### NOVA2FA_EXEMPT_PATHS

**Type**: `list`  
**Default**: `[]`  
**Description**: List of URL paths to exempt from 2FA verification

```python
# Exempt API endpoints and health checks
NOVA2FA_EXEMPT_PATHS = [
    '/api/public/',
    '/healthcheck/',
    '/status/',
]
```

!!! note "Default Exemptions"
These paths are always exempt and don't need to be added: - `/2fa/` - `/nova2fa/` - `/admin/`

### NOVA2FA_PROTECTED_PATHS

**Type**: `list`  
**Default**: `['*']`  
**Description**: List of URL paths that require 2FA verification

```python
# Protect all authenticated pages (default)
NOVA2FA_PROTECTED_PATHS = ['*']

# Protect only specific paths
NOVA2FA_PROTECTED_PATHS = [
    '/dashboard/',
    '/profile/',
    '/settings/',
    '/billing/',
]
```

!!! tip "Wildcard Behavior"
When `'*'` is in the list, all authenticated pages require 2FA unless explicitly exempted.

## Path Protection Examples

### Example 1: Protect Everything

```python
NOVA2FA_PROTECTED_PATHS = ['*']
NOVA2FA_EXEMPT_PATHS = []
```

All authenticated pages require 2FA.

### Example 2: Protect Sensitive Areas Only

```python
NOVA2FA_PROTECTED_PATHS = [
    '/dashboard/',
    '/admin/',
    '/settings/',
    '/billing/',
]
NOVA2FA_EXEMPT_PATHS = ['/api/']
```

Only listed paths require 2FA. Public APIs are accessible.

### Example 3: Protect Most, Exempt Some

```python
NOVA2FA_PROTECTED_PATHS = ['*']
NOVA2FA_EXEMPT_PATHS = [
    '/api/public/',
    '/help/',
    '/docs/',
]
```

All pages require 2FA except public APIs, help, and docs.

## Complete Configuration Example

```python
# settings.py
import os

# ===== Nova2FA Configuration =====

# Available methods
NOVA2FA_ENABLED_METHODS = ['email', 'totp']

# Verification settings
NOVA2FA_VERIFICATION_WINDOW_DAYS = 14

# Email OTP
NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES = 10
NOVA2FA_EMAIL_SUBJECT = 'Your MyApp Verification Code'

# TOTP
NOVA2FA_TOTP_ISSUER = 'MyApp'

# Backup codes
NOVA2FA_BACKUP_CODE_COUNT = 8

# Security (v1.1.0+)
NOVA2FA_SECRET_KEY = os.environ.get('NOVA2FA_SECRET_KEY')  # Required!
NOVA2FA_MAX_ATTEMPTS = 5
NOVA2FA_LOCKOUT_DURATION_MINUTES = 15
NOVA2FA_EXEMPT_SUPERUSERS = False

# Path protection
NOVA2FA_PROTECTED_PATHS = ['*']
NOVA2FA_EXEMPT_PATHS = [
    '/api/public/',
    '/healthcheck/',
]

# ===== End Nova2FA Configuration =====
```

## Environment Variables (Optional)

For better security, you can use environment variables:

```python
# settings.py
import os

NOVA2FA_EMAIL_SUBJECT = os.environ.get(
    'NOVA2FA_EMAIL_SUBJECT',
    'Your Verification Code'
)

NOVA2FA_TOTP_ISSUER = os.environ.get(
    'NOVA2FA_TOTP_ISSUER',
    'MyApp'
)
```

Then in your `.env` file:

```bash
NOVA2FA_EMAIL_SUBJECT="MyApp Security Code"
NOVA2FA_TOTP_ISSUER="MyCompany"
```

## Configuration Validation

Nova2FA validates configuration on startup. Invalid values will raise errors:

```python
# ❌ Invalid - not a list
NOVA2FA_ENABLED_METHODS = 'email'  # Error!

# ✅ Valid
NOVA2FA_ENABLED_METHODS = ['email']

# ❌ Invalid - not an integer
NOVA2FA_VERIFICATION_WINDOW_DAYS = "14"  # Error!

# ✅ Valid
NOVA2FA_VERIFICATION_WINDOW_DAYS = 14
```

## Next Steps

- Learn about [Template Customization](customization.md)
