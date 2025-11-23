# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-11-23

### Added

- **Security**: Backup codes are now hashed using Django's password hashers before storage
- **Security**: TOTP secrets are now encrypted at rest using Fernet symmetric encryption
- **Security**: Account lockout after 5 failed verification attempts (15-minute lockout)
- **Security**: Rate limiting on verification endpoints
- **Testing**: Comprehensive test suite with pytest (>80% coverage target)
- **Testing**: Test fixtures for users, 2FA settings, and OTPs
- New `encryption.py` module for secure secret management
- Failed attempt tracking and lockout fields in `UserTwoFactorSettings`
- One-time display of backup codes after generation (stored in session)

### Changed

- **BREAKING**: Backup codes are now stored as hashed values (existing codes must be regenerated)
- **BREAKING**: TOTP secrets are now encrypted (requires `cryptography` package)
- **BREAKING**: `totp_secret` field increased to 512 characters to accommodate encrypted values
- Package status upgraded from Beta to Production/Stable
- Removed deprecated `default_app_config` for Django 5.0 compatibility
- Backup code verification now includes account lockout logic
- TOTP setup now displays plain text secret separately from encrypted storage
- Views updated to handle hashed backup codes with one-time display

### Fixed

- QR code cleanup after TOTP setup
- Backup code display now shows availability count instead of actual codes (security)

### Dependencies

- Added `cryptography>=41.0.0` for encryption features

### Migration Notes

- Run `python manage.py migrate nova2fa` to add new fields
- Users will need to regenerate backup codes after upgrade
- Set `NOVA2FA_SECRET_KEY` in settings (optional, falls back to `SECRET_KEY`)

## [1.0.0] - 2024-11-17

### Added

- Initial release
- TOTP authentication via authenticator apps
- Email OTP authentication
- Backup codes for recovery
- Configurable middleware
- Django 4.2+ support
- Python 3.8+ support
