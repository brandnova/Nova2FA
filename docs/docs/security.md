# Security Guide

Nova2FA v1.1.0 implements enterprise-grade security features to protect user accounts. This guide explains the security architecture and best practices.

## Security Features

### 🔐 Encryption at Rest

**TOTP Secrets** are encrypted before storage using Fernet symmetric encryption (AES-128).

**How it works:**

1. User sets up TOTP with authenticator app
2. Secret is generated and encrypted with `NOVA2FA_SECRET_KEY`
3. Encrypted value stored in database (max 512 characters)
4. Decrypted only during verification

**Configuration:**

```python
# settings.py
NOVA2FA_SECRET_KEY = 'your-secret-encryption-key'  # Required for v1.1.0+
```

!!! tip "Best Practice"
Use a dedicated encryption key separate from Django's `SECRET_KEY`. If `NOVA2FA_SECRET_KEY` is not set, it falls back to `SECRET_KEY`.

### 🔒 Password Hashing

**Backup Codes** are hashed using Django's password hashers (PBKDF2 by default).

**How it works:**

1. 8 backup codes generated during setup
2. Each code hashed with `make_password()`
3. Only hashed values stored in database
4. Verification uses `check_password()`
5. Used codes tracked separately

**Why this matters:**

- Database breach doesn't expose usable codes
- Codes cannot be reversed or recovered
- Same security level as user passwords

### 🛡️ Brute Force Protection

**Account Lockout** prevents unlimited verification attempts.

**Default Settings:**

```python
NOVA2FA_MAX_ATTEMPTS = 5  # Failed attempts before lockout
NOVA2FA_LOCKOUT_DURATION_MINUTES = 15  # Lockout duration
```

**How it works:**

1. Failed verification increments `failed_attempts` counter
2. After 5 failures, account locked for 15 minutes
3. `locked_until` timestamp set
4. Successful verification resets counter
5. Lockout applies to all verification methods

**Lockout applies to:**

- TOTP verification
- Email OTP verification
- Backup code verification

### ⏱️ Rate Limiting

**Verification endpoints** are rate-limited to prevent abuse.

**Implementation:**

- Uses Django's cache framework
- Default: 10 attempts per 15 minutes per user
- Applied via `@rate_limit` decorator
- Works with account lockout for defense-in-depth

### 🔑 One-Time Backup Code Display

**Backup codes** shown only once after generation.

**Security benefits:**

- Codes displayed immediately after generation
- Stored in session temporarily
- Removed after first view
- Forces users to save codes securely
- Prevents casual browsing of codes

**User flow:**

1. User enables 2FA or regenerates codes
2. Codes displayed once with save prompt
3. Codes removed from session
4. Only count of available codes shown afterward

## Security Architecture

### Data Flow Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  TOTP Setup                         │
│  1. Generate secret (plain)         │
│  2. Encrypt with NOVA2FA_SECRET_KEY │
│  3. Store encrypted in DB           │
│  4. Show QR code (plain for scan)   │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  TOTP Verification                  │
│  1. Retrieve encrypted secret       │
│  2. Decrypt with key                │
│  3. Verify token                    │
│  4. Reset/increment failed attempts │
└─────────────────────────────────────┘
```

### Database Security

**Encrypted Fields:**

- `totp_secret` (512 chars) - Fernet encrypted

**Hashed Fields:**

- `backup_codes` (JSON array) - Django password hashes

**Tracking Fields:**

- `failed_attempts` (integer) - Brute force counter
- `locked_until` (datetime) - Lockout expiration
- `used_backup_codes` (JSON array) - Hashed used codes

**Indexes:**

- `user_id` - Unique constraint
- `locked_until` - Query optimization for lockout checks

## Threat Model

### Threats Mitigated

✅ **Database Breach**

- TOTP secrets encrypted (unusable without key)
- Backup codes hashed (cannot be reversed)
- Email OTP codes expire quickly

✅ **Brute Force Attacks**

- Account lockout after 5 attempts
- Rate limiting on endpoints
- Lockout duration prevents automated attacks

✅ **Credential Stuffing**

- 2FA required even with valid password
- Multiple verification methods available
- Backup codes for account recovery

✅ **Session Hijacking**

- Verification window limits session validity
- Re-verification required after timeout
- Middleware enforces verification

### Threats NOT Mitigated

⚠️ **Phishing**

- Users can be tricked into providing TOTP codes
- Mitigation: User education, WebAuthn (future)

⚠️ **Malware on User Device**

- Authenticator app can be compromised
- Mitigation: Device security, biometric locks

⚠️ **SIM Swapping** (Email OTP)

- Email account takeover bypasses 2FA
- Mitigation: Use TOTP instead of Email OTP

⚠️ **Social Engineering**

- Attackers may trick support into disabling 2FA
- Mitigation: Strict verification procedures

## Best Practices

### For Developers

1. **Use Dedicated Encryption Key**

   ```python
   # Generate with:
   from django.core.management.utils import get_random_secret_key
   NOVA2FA_SECRET_KEY = get_random_secret_key()
   print(NOVA2FA_SECRET_KEY)
   # Store securely
   ```

2. **Secure Key Storage**

   - Use environment variables
   - Never commit keys to version control
   - Rotate keys periodically
   - Use secrets management (AWS Secrets Manager, etc.)

3. **Configure HTTPS**

   ```python
   # settings.py (production)
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Monitor Failed Attempts**

   ```python
   # Log lockouts for security monitoring
   from nova2fa.models import UserTwoFactorSettings

   locked_users = UserTwoFactorSettings.objects.filter(
       locked_until__gt=timezone.now()
   )
   ```

5. **Customize Lockout Settings**
   ```python
   # Stricter for high-security apps
   NOVA2FA_MAX_ATTEMPTS = 3
   NOVA2FA_LOCKOUT_DURATION_MINUTES = 30
   ```

### For End Users

1. **Save Backup Codes Securely**

   - Print and store in safe place
   - Use password manager
   - Never share codes
   - Regenerate if compromised

2. **Use Authenticator Apps**

   - Prefer TOTP over Email OTP
   - Use apps like Google Authenticator, Authy
   - Enable app lock/biometrics

3. **Protect Recovery Email**

   - Use strong password
   - Enable 2FA on email account
   - Monitor for suspicious activity

4. **Report Suspicious Activity**
   - Unexpected lockouts
   - Unrecognized verification attempts
   - Lost/stolen devices

## Compliance Considerations

### GDPR

- **Data Minimization**: Only stores necessary 2FA data
- **Right to Erasure**: Disable 2FA to remove data
- **Data Portability**: Export backup codes on generation
- **Encryption**: Personal data encrypted at rest

### SOC 2

- **Access Control**: 2FA enforces authentication
- **Audit Logging**: Track verification attempts
- **Encryption**: Data encrypted in transit and at rest
- **Availability**: Backup codes ensure account access

### PCI DSS

- **Multi-Factor Authentication**: Requirement 8.3
- **Encryption**: Requirement 3.4 (data at rest)
- **Access Logging**: Requirement 10.2
- **Account Lockout**: Requirement 8.1.6

## Security Checklist

Before deploying to production:

- [ ] Set `NOVA2FA_SECRET_KEY` in environment variables
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure secure cookie settings
- [ ] Set up monitoring for failed attempts
- [ ] Document backup code recovery process
- [ ] Train support staff on 2FA procedures
- [ ] Test account lockout behavior
- [ ] Verify encryption is working (check DB values)
- [ ] Set up backup/recovery procedures
- [ ] Review and customize lockout settings

## Incident Response

### Compromised Encryption Key

1. Generate new `NOVA2FA_SECRET_KEY`
2. Update environment variables
3. Restart application
4. Force all users to re-setup TOTP
5. Notify users of security incident

### Mass Account Lockouts

1. Check for DDoS/attack patterns
2. Temporarily increase `NOVA2FA_LOCKOUT_DURATION_MINUTES`
3. Implement IP-based rate limiting
4. Consider temporary 2FA bypass for verified users
5. Investigate root cause

### Database Breach

1. Rotate `NOVA2FA_SECRET_KEY` immediately
2. Force password resets for all users
3. Force 2FA re-setup for all users
4. Audit access logs
5. Notify affected users
6. Review and enhance security measures

## Future Enhancements

Planned security features:

- **SMS OTP** as additional method
- **Trusted devices** (remember device)
- **Admin notifications** (suspicious activity alerts)
- **IP whitelisting** (restrict verification by location)

## References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Fernet Specification](https://github.com/fernet/spec/)

---

**Questions or concerns?** Open an issue on [GitHub](https://github.com/brandnova/Nova2FA/issues) or review the [CHANGELOG](https://github.com/brandnova/Nova2FA/blob/main/CHANGELOG.md).
