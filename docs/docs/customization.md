# Customization Guide

Nova2FA is designed to be completely customizable. This guide shows you how to adapt it to your needs.

## Template Customization

### Understanding Template Structure

Nova2FA provides unstyled templates with minimal CSS. All templates extend from a base template that you can override.

**Template hierarchy:**
```
nova2fa/base_2fa.html (Base template)
    ├── nova2fa/settings.html (2FA settings page)
    ├── nova2fa/setup.html (Method selection)
    ├── nova2fa/setup_totp.html (TOTP setup)
    ├── nova2fa/verify.html (Verification page)
    ├── nova2fa/verify_email_otp.html (Email verification during setup)
    ├── nova2fa/disable.html (Disable 2FA)
    ├── nova2fa/backup_codes.html (View backup codes)
    └── nova2fa/change_method.html (Change method)
```

### Method 1: Override Base Template

The simplest way to customize is to override the base template with your own.

**Create `templates/nova2fa/base_2fa.html` in your project:**

```html
{% extends "base.html" %}

{% block content %}
<div class="container my-5">
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

Now all Nova2FA pages will use your base template and styling!

### Method 2: Override Individual Templates

You can override any specific template by creating it in your project's template directory.

**Example: Custom settings page**

Create `templates/nova2fa/settings.html`:

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Security Settings{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h1 class="mb-4">Two-Factor Authentication</h1>
            
            {% if two_factor_settings.is_enabled %}
            <div class="card border-success">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="bi bi-shield-check"></i> 2FA Enabled
                    </h5>
                    <p class="card-text">
                        <strong>Method:</strong> {{ two_factor_settings.get_method_display }}
                    </p>
                    <p class="card-text">
                        <strong>Last Verified:</strong> 
                        {{ two_factor_settings.last_verified|date:"F d, Y" }}
                    </p>
                    
                    <div class="btn-group" role="group">
                        <a href="{% url 'nova2fa:change_method' %}" 
                           class="btn btn-outline-primary">
                            Change Method
                        </a>
                        <a href="{% url 'nova2fa:view_backup_codes' %}" 
                           class="btn btn-outline-secondary">
                            Backup Codes
                        </a>
                        <a href="{% url 'nova2fa:disable' %}" 
                           class="btn btn-outline-danger">
                            Disable
                        </a>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="card border-warning">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="bi bi-shield-exclamation"></i> 2FA Not Enabled
                    </h5>
                    <p class="card-text">
                        Protect your account with two-factor authentication.
                    </p>
                    <a href="{% url 'nova2fa:setup' %}" 
                       class="btn btn-primary">
                        Enable Two-Factor Authentication
                    </a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

### Method 3: Add Custom CSS Classes

Nova2FA templates use prefixed CSS classes (`nova2fa-*`) that you can style:

```css
/* static/css/nova2fa-custom.css */

.nova2fa-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.nova2fa-button {
    background: #667eea;
    border: none;
    padding: 12px 30px;
    border-radius: 5px;
    transition: all 0.3s;
}

.nova2fa-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.nova2fa-input {
    border: 2px solid #e2e8f0;
    border-radius: 5px;
    padding: 10px;
    font-size: 16px;
}

.nova2fa-input:focus {
    border-color: #667eea;
    outline: none;
}
```

Include it in your base template:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/nova2fa-custom.css' %}">
```

## Framework Integration Examples

### Bootstrap 5

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-body">
                    {% if messages %}
                    {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}
                    {% endif %}
                    
                    {% block nova2fa_content %}{% endblock %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Tailwind CSS

```html
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
        <div class="bg-white rounded-lg shadow-lg p-6">
            {% if messages %}
            <div class="mb-4">
                {% for message in messages %}
                <div class="rounded-md p-4 mb-2 
                    {% if message.tags == 'success' %}bg-green-50 text-green-800{% endif %}
                    {% if message.tags == 'error' %}bg-red-50 text-red-800{% endif %}
                    {% if message.tags == 'warning' %}bg-yellow-50 text-yellow-800{% endif %}
                    {% if message.tags == 'info' %}bg-blue-50 text-blue-800{% endif %}">
                    {{ message }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% block nova2fa_content %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}
```

## Email Template Customization

Customize the OTP email by overriding the template:

**Create `templates/nova2fa/emails/otp_email.html`:**

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            text-align: center;
            color: white;
        }
        .content {
            padding: 40px;
        }
        .code {
            background: #f8f9fa;
            border: 2px dashed #667eea;
            padding: 20px;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 5px;
            margin: 30px 0;
            border-radius: 5px;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Verification Code</h1>
        </div>
        <div class="content">
            <p>Hello {{ user.get_full_name|default:user.username }},</p>
            <p>Your two-factor authentication code is:</p>
            
            <div class="code">{{ otp }}</div>
            
            <p>This code will expire in <strong>{{ expiry_minutes }} minutes</strong>.</p>
            
            <p style="margin-top: 30px;">
                <strong>Security Notice:</strong> If you didn't request this code, 
                please ignore this email and ensure your account is secure.
            </p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
```

## Form Customization

Override forms to add custom widgets or validation:

```python
# myapp/forms.py
from nova2fa.forms import TOTPVerificationForm

class CustomTOTPForm(TOTPVerificationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        self.fields['code'].widget.attrs.update({
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'autofocus': True,
        })
```

Then use it in your custom view or override the template to use it.

## URL Customization

You can change the URL prefix from `/2fa/` to anything:

```python
# urls.py
urlpatterns = [
    path('security/', include('nova2fa.urls')),  # Now it's /security/
    path('mfa/', include('nova2fa.urls')),       # Or /mfa/
]
```

## Adding Custom Pages

Add your own pages that integrate with Nova2FA:

```python
# myapp/views.py
from django.contrib.auth.decorators import login_required
from nova2fa.models import UserTwoFactorSettings

@login_required
def security_dashboard(request):
    try:
        two_factor = UserTwoFactorSettings.objects.get(user=request.user)
        has_2fa = two_factor.is_enabled
    except UserTwoFactorSettings.DoesNotExist:
        has_2fa = False
    
    context = {
        'has_2fa': has_2fa,
        # Add more security metrics
    }
    return render(request, 'myapp/security_dashboard.html', context)
```

## Translation/Internationalization

Nova2FA is translation-ready. Add translations in your project:

```python
# settings.py
LANGUAGE_CODE = 'es'  # Spanish

USE_I18N = True
```

Create translation files:
```bash
django-admin makemessages -l es
# Edit locale/es/LC_MESSAGES/django.po
django-admin compilemessages
```

## JavaScript Enhancement

Add JavaScript for better UX:

```html
<!-- templates/nova2fa/setup_totp.html -->
{% extends "nova2fa/base_2fa.html" %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const codeInput = document.querySelector('[name="code"]');
    
    // Auto-submit when 6 digits entered
    codeInput.addEventListener('input', function(e) {
        if (this.value.length === 6) {
            this.form.submit();
        }
    });
    
    // Auto-focus on page load
    codeInput.focus();
});
</script>
{% endblock %}
```

## Next Steps

- Check the [API Reference](api-reference.md) for programmatic usage
- Review the [Example Project](https://github.com/brandnova/Nova2FA/tree/main/example_project)