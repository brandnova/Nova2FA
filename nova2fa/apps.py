from django.apps import AppConfig


class Nova2FAConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nova2fa'
    verbose_name = 'Two-Factor Authentication'
    
    def ready(self):
        # Import signals
        import nova2fa.signals
        
        # Register default 2FA methods
        from nova2fa.methods.email_otp import EmailOTPMethod
        from nova2fa.methods.totp import TOTPMethod
        from nova2fa.methods.backup_codes import BackupCodesMethod
        from nova2fa.registry import register_method
        
        register_method('email', EmailOTPMethod())
        register_method('totp', TOTPMethod())
        register_method('backup', BackupCodesMethod())