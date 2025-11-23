"""
Django settings for example_project.
"""

from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-example-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'accounts',
    
    # Third-party apps
    'nova2fa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'nova2fa.middleware.Nova2FAMiddleware',  # Nova2FA middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'example_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'example_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Email Configuration (Console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, use SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# ============================================================================
# Nova2FA Configuration
# ============================================================================
# Complete configuration reference for Nova2FA v1.1.0+
# Uncomment and modify settings as needed for your project

# --- Core Settings ---

# Enabled authentication methods
# Options: 'email', 'totp', or custom methods
NOVA2FA_ENABLED_METHODS = ['email', 'totp']

# Verification window (days user stays verified before re-verification required)
# Default: 14 days
NOVA2FA_VERIFICATION_WINDOW_DAYS = 2 / (24 * 60)  # 3 minutes for quick testing

# --- Security Settings (v1.1.0+) ---

# Encryption key for TOTP secrets (REQUIRED for v1.1.0+)
# Generate with: from django.core.management.utils import get_random_secret_key
# IMPORTANT: Store in environment variables in production!
# NOVA2FA_SECRET_KEY = 'your-secret-encryption-key-here'
# If not set, falls back to SECRET_KEY (not recommended for production)

# Maximum failed verification attempts before account lockout
# Default: 5
NOVA2FA_MAX_ATTEMPTS = 5

# Account lockout duration in minutes after max failed attempts
# Default: 15 minutes
NOVA2FA_LOCKOUT_DURATION_MINUTES = 0.5

# --- Email OTP Settings ---

# Email OTP code expiry time in minutes
# Default: 10 minutes
NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES = 10

# Email subject line for OTP emails
# Default: 'Your One-Time Password'
# NOVA2FA_EMAIL_SUBJECT = 'Your Verification Code'

# --- TOTP Settings ---

# Issuer name shown in authenticator apps
# This appears as: "Nova2FA Example (user@example.com)"
NOVA2FA_TOTP_ISSUER = 'Nova2FA Example'

# --- Backup Codes Settings ---

# Number of backup codes to generate
# Default: 8
NOVA2FA_BACKUP_CODE_COUNT = 6

# --- Access Control Settings ---

# Exempt superusers from 2FA verification
# Default: False (recommended for security)
# WARNING: Setting to True reduces security
NOVA2FA_EXEMPT_SUPERUSERS = False

# URL paths that require 2FA verification
# Default: ['*'] (all authenticated pages)
# Use '*' to protect all pages, or list specific paths
# NOVA2FA_PROTECTED_PATHS = ['*']
# NOVA2FA_PROTECTED_PATHS = ['/dashboard/', '/settings/', '/billing/']

# URL paths exempt from 2FA verification
# Default: [] (no exemptions)
# Note: /2fa/, /nova2fa/, and /admin/ are always exempt
# NOVA2FA_EXEMPT_PATHS = ['/']  # Exempt all for testing
# NOVA2FA_EXEMPT_PATHS = ['/api/public/', '/healthcheck/']

# For production, protect everything:
# NOVA2FA_PROTECTED_PATHS = ['*']
# NOVA2FA_EXEMPT_PATHS = ['/api/public/']

# ============================================================================
# End Nova2FA Configuration
# ============================================================================

# Example production configuration:
"""
# Production Nova2FA Settings
NOVA2FA_ENABLED_METHODS = ['totp']  # TOTP only for better security
NOVA2FA_SECRET_KEY = os.environ.get('NOVA2FA_SECRET_KEY')  # From environment
NOVA2FA_MAX_ATTEMPTS = 3  # Stricter lockout
NOVA2FA_LOCKOUT_DURATION_MINUTES = 30  # Longer lockout
NOVA2FA_VERIFICATION_WINDOW_DAYS = 7  # Weekly verification
NOVA2FA_TOTP_ISSUER = 'YourCompany'
NOVA2FA_BACKUP_CODE_COUNT = 10
NOVA2FA_EXEMPT_SUPERUSERS = False  # Always require 2FA
NOVA2FA_PROTECTED_PATHS = ['*']  # Protect everything
NOVA2FA_EXEMPT_PATHS = ['/api/public/', '/healthcheck/']  # Only public APIs
"""