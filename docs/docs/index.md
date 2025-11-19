# Nova2FA Documentation

Welcome to Nova2FA - a flexible, production-ready Two-Factor Authentication (2FA) package for Django applications.

## What is Nova2FA?

Nova2FA provides a complete 2FA solution for Django projects with:

- 🔐 Multiple authentication methods (TOTP, Email OTP, Backup Codes)
- 🎨 Completely customizable unstyled templates
- 🔌 Pluggable architecture for custom methods
- 🛡️ Production-ready security features
- 🚀 Easy integration with existing Django projects

## Quick Links

- [Installation Guide](installation.md)
- [Quick Start Tutorial](quickstart.md)
- [Configuration Reference](configuration.md)
- [Customization Guide](customization.md)
- [API Reference](api-reference.md)

## Why Nova2FA?

Unlike other 2FA packages, Nova2FA is designed from the ground up to be:

1. **Flexible**: Pluggable architecture lets you add custom authentication methods
2. **Unstyled**: Bring your own design system - no forced styling
3. **Simple**: Minimal configuration required to get started
4. **Powerful**: Advanced features for production use
5. **Maintained**: Active development and support

## Features at a Glance

### Authentication Methods

- **TOTP (Time-based OTP)**: Works with Google Authenticator, Authy, Microsoft Authenticator, etc.
- **Email OTP**: Receive codes via email
- **Backup Codes**: Recovery codes for emergency access
- **Extensible**: Add SMS, push notifications, hardware keys, etc.

### Security Features

- Configurable verification windows
- Built-in rate limiting
- Session-based verification
- Path-based access control
- Backup codes with usage tracking

### Developer Experience

- Zero-friction installation
- Comprehensive documentation
- Example project included
- Minimal dependencies
- Django 4.2+ compatible

## Community

- **GitHub**: [brandnova/Nova2FA](https://github.com/brandnova/Nova2FA)
- **Issues**: [Report bugs or request features](https://github.com/brandnova/Nova2FA/issues)
- **PyPI**: [nova2fa on PyPI](https://pypi.org/project/nova2fa/)

## License

Nova2FA is released under the BSD 3-Clause License.