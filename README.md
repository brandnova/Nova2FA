# Nova2FA

Flexible, pluggable two-factor authentication for Django.

## Features

- 🔐 Multiple 2FA methods (TOTP, Email OTP)
- 🔌 Pluggable architecture for custom methods
- 🎨 Tailwind UI included (optional)
- 📱 Mobile-friendly verification flows
- 💾 Backup codes for account recovery
- 🛠️ Easy to customize and extend
- 🔒 **NEW in v1.1.0**: Encrypted TOTP secrets and hashed backup codes
- 🛡️ **NEW in v1.1.0**: Brute force protection with account lockout
  - Account lockout after configurable failed attempts
  - Visual counter showing remaining attempts
  - Comprehensive enforcement (cannot be bypassed)
  - Automatic expiry with countdown display
- ✅ **NEW in v1.1.0**: Comprehensive test suite

## Quick Start

See [Installation Guide](https://brandnova.github.io/Nova2FA/installation/) for detailed setup instructions.

**Note**: v1.1.0 includes security enhancements. Existing users should regenerate backup codes after upgrading.
