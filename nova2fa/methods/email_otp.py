"""
Email OTP method implementation.
"""
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .base import Base2FAMethod


class EmailOTPMethod(Base2FAMethod):
    """
    Email-based One-Time Password method.
    """
    name = "email"
    verbose_name = "Email OTP"
    
    def send(self, user):
        """
        Generate and send an OTP to the user's email.
        """
        from nova2fa.models import EmailOTP
        
        # Get expiry minutes from settings
        expiry_minutes = getattr(settings, 'NOVA2FA_EMAIL_OTP_EXPIRY_MINUTES', 10)
        
        # Generate a 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Calculate expiry time
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Create and save the OTP
        otp = EmailOTP.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        
        # Send email
        try:
            self._send_email(user, otp, expiry_minutes)
            return True
        except Exception:
            return False
    
    def verify(self, user, token):
        """
        Verify an email OTP token.
        """
        from nova2fa.models import EmailOTP
        
        try:
            # Get the latest unused OTP for the user
            otp = EmailOTP.objects.filter(
                user=user,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            if otp.code == token:
                otp.mark_as_used()
                return True
            return False
        except EmailOTP.DoesNotExist:
            return False
    
    def _send_email(self, user, otp, expiry_minutes):
        """
        Send the OTP email to the user.
        """
        subject = getattr(settings, 'NOVA2FA_EMAIL_SUBJECT', 'Your One-Time Password')
        
        # Render the email template
        message = render_to_string('nova2fa/emails/otp_email.html', {
            'user': user,
            'otp': otp.code,
            'expiry_minutes': expiry_minutes
        })
        
        email = EmailMessage(subject, message, to=[user.email])
        email.content_subtype = 'html'
        email.send()
    
    def is_configured(self, user):
        """
        Email OTP doesn't require configuration.
        """
        return bool(user.email)