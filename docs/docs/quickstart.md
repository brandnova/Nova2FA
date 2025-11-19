# Quick Start Tutorial

This tutorial will guide you through setting up Nova2FA in a Django project and enabling your first 2FA authentication.

## Prerequisites

Before starting, ensure you have:

- Completed the [Installation Guide](installation.md)
- A Django project with user authentication working
- At least one user account to test with

## Step 1: Create a Link to 2FA Settings

Add a link to the Nova2FA settings page in your base template or user profile:
```html
<!-- base.html or profile.html -->
{% if user.is_authenticated %}
<nav>
    <a href="{% url 'nova2fa:settings' %}">Security Settings</a>
</nav>
{% endif %}
```

## Step 2: Configure Nova2FA

Add configuration to your `settings.py`:
```python
# Nova2FA Configuration
NOVA2FA_ENABLED_METHODS = ['email', 'totp']  # Enable both methods
NOVA2FA_TOTP_ISSUER = 'MyApp'  # Your app name (shown in authenticator apps)
NOVA2FA_VERIFICATION_WINDOW_DAYS = 14  # User stays verified for 14 days
NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES = 10  # Email codes expire after 10 minutes
```

## Step 3: Test the Flow

### 3.1 Enable 2FA

1. Start your development server: `python manage.py runserver`
2. Log in to your Django application
3. Navigate to `/2fa/settings/`
4. Click "Enable Two-Factor Authentication"

### 3.2 Choose Authentication Method

**Option A: Email OTP**

1. Select "Email OTP"
2. Click "Continue"
3. Check your email (or console if using console backend)
4. Enter the 6-digit code
5. Click "Verify and Enable"
6. Save your backup codes!

**Option B: Authenticator App (TOTP)**

1. Select "Authenticator App"
2. Click "Continue"
3. Scan the QR code with Google Authenticator or similar app
   - Or manually enter the secret key shown
4. Enter the 6-digit code from your app
5. Click "Verify and Enable"
6. Save your backup codes!

### 3.3 Test Verification

1. Log out of your application
2. Log back in with your username and password
3. You'll be redirected to `/2fa/verify/`
4. Enter your 2FA code
5. You'll be redirected to your intended destination

## Step 4: Understand What Happened

When you enabled 2FA:
```python
# Nova2FA created a UserTwoFactorSettings record
user_settings = UserTwoFactorSettings.objects.get(user=request.user)
print(user_settings.is_enabled)  # True
print(user_settings.method)  # 'email' or 'totp'
print(user_settings.backup_codes)  # List of 8 backup codes
```

When you verified 2FA:
```python
# Nova2FA set a session variable
request.session['nova2fa_verified_at'] = '2025-01-15T10:30:00'

# And updated the database
user_settings.last_verified = timezone.now()
user_settings.save()
```

The middleware now checks this on every request:
```python
# Simplified middleware logic
if user.nova2fa_settings.is_enabled:
    if not is_verified_in_session(request):
        redirect_to_verification()
```

## Step 5: Customize the Experience

### 5.1 Override Templates

Create `templates/nova2fa/settings.html` in your project:
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Security Settings</h1>
    
    {% if two_factor_settings.is_enabled %}
        <div class="alert alert-success">
            Two-Factor Authentication is enabled
        </div>
        <p>Method: {{ two_factor_settings.get_method_display }}</p>
        
        <a href="{% url 'nova2fa:disable' %}" class="btn btn-danger">
            Disable 2FA
        </a>
    {% else %}
        <div class="alert alert-warning">
            Two-Factor Authentication is not enabled
        </div>
        
        <a href="{% url 'nova2fa:setup' %}" class="btn btn-primary">
            Enable 2FA
        </a>
    {% endif %}
</div>
{% endblock %}
```

### 5.2 Add Custom Styling

Create a custom base template at `templates/nova2fa/base_2fa.html`:
```html
{% extends "base.html" %}

{% block content %}
<div class="nova2fa-container">
    {% if messages %}
    <div class="messages">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% block nova2fa_content %}{% endblock %}
</div>
{% endblock %}
```

## Step 6: Configure Path Protection

By default, Nova2FA protects **all authenticated pages**. Customize this:
```python
# Protect specific paths only
NOVA2FA_PROTECTED_PATHS = [
    '/dashboard/',
    '/profile/',
    '/settings/',
]

# Exempt certain paths
NOVA2FA_EXEMPT_PATHS = [
    '/api/public/',
    '/healthcheck/',
]

# Exempt superusers (useful for emergency access)
NOVA2FA_EXEMPT_SUPERUSERS = True
```

## Step 7: Test Backup Codes

1. Enable 2FA (if not already enabled)
2. Go to `/2fa/settings/`
3. Click "View Backup Codes"
4. Save these codes somewhere safe
5. Log out and log back in
6. When prompted for 2FA, click "Use a backup code instead"
7. Enter one of your backup codes
8. You'll be logged in (and that code is now marked as used)

## Common Scenarios

### Scenario 1: User Lost Their Phone

1. User logs in with username/password
2. User clicks "Use a backup code instead"
3. User enters a backup code
4. User is logged in
5. User can go to settings and switch to Email OTP
6. User generates new backup codes

### Scenario 2: User Wants to Switch Methods

1. User goes to `/2fa/settings/`
2. User clicks "Change Method"
3. User selects new method
4. User completes setup for new method
5. Old method is replaced

### Scenario 3: User Wants to Disable 2FA

1. User goes to `/2fa/settings/`
2. User clicks "Disable 2FA"
3. User confirms by checking the box
4. 2FA is disabled (can be re-enabled anytime)

## Next Steps

- Read the [Configuration Reference](configuration.md) for all available options
- Check the [Customization Guide](customization.md) to style templates
- Learn about [Custom Methods](advanced/custom-methods.md) to add SMS, etc.
- Review [Security Best Practices](advanced/security.md)

## Troubleshooting

### 2FA Not Triggering

Check your middleware order:
```python
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'nova2fa.middleware.Nova2FAMiddleware',  # Must be after auth
    # ...
]
```

### Stuck in Verification Loop

Clear your session and try again:
```bash
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()
```

### QR Code Not Showing

Ensure Pillow is installed:
```bash
pip install Pillow
```

### Email Not Sending

Check Django's email configuration and test manually:
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```