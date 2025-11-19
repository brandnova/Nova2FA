from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import datetime
import logging

logger = logging.getLogger(__name__)


class Nova2FAMiddleware:
    """
    Middleware to enforce 2FA verification for authenticated users.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Default exempt paths (critical!)
        self.default_exempt_paths = [
            '/2fa/',
            '/nova2fa/',
            '/admin/',
        ]
        
        self.exempt_paths = self._get_exempt_paths()
        self.protected_paths = self._get_protected_paths()

    def __call__(self, request):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check if path is exempt FIRST
        path = request.path
        if self._is_path_exempt(path):
            return self.get_response(request)
        
        # Check if superuser is exempt
        if self._is_superuser_exempt(request):
            return self.get_response(request)
        
        # Check if path is protected
        if not self._is_path_protected(path):
            return self.get_response(request)
        
        # Check if user has 2FA enabled and needs verification
        try:
            from .models import UserTwoFactorSettings
            
            try:
                two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
                
                if not two_factor_settings.is_enabled:
                    return self.get_response(request)
                
                if self._is_2fa_verified(request):
                    return self.get_response(request)
                
                # Store the current URL for redirection after verification
                request.session['nova2fa_next_url'] = request.get_full_path()
                
                return redirect('nova2fa:verify')
                
            except UserTwoFactorSettings.DoesNotExist:
                pass
                
        except Exception as e:
            logger.error(f"Error in Nova2FA middleware: {str(e)}")
        
        return self.get_response(request)
    
    def _get_exempt_paths(self):
        """Get exempt paths from settings."""
        exempt_paths = self.default_exempt_paths.copy()
        
        custom_exempt_paths = getattr(settings, 'NOVA2FA_EXEMPT_PATHS', [])
        if custom_exempt_paths:
            exempt_paths.extend(custom_exempt_paths)
        
        return list(set(exempt_paths))
    
    def _get_protected_paths(self):
        """Get protected paths from settings."""
        return getattr(settings, 'NOVA2FA_PROTECTED_PATHS', ['*'])
    
    def _is_superuser_exempt(self, request):
        """Check if superuser is exempt."""
        exempt_superusers = getattr(settings, 'NOVA2FA_EXEMPT_SUPERUSERS', False)
        return exempt_superusers and request.user.is_superuser
    
    def _is_path_exempt(self, path):
        """Check if path is exempt."""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _is_path_protected(self, path):
        """Check if path is protected."""
        if '*' in self.protected_paths:
            return True
        
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        return False
    
    def _is_2fa_verified(self, request):
        """Check if 2FA has been verified in the current session."""
        verified_at = request.session.get('nova2fa_verified_at')
        if not verified_at:
            return False
        
        try:
            if isinstance(verified_at, str):
                verified_at = timezone.datetime.fromisoformat(verified_at)
            
            if timezone.is_naive(verified_at):
                verified_at = timezone.make_aware(verified_at)
            
            verification_window_hours = getattr(
                settings,
                'NOVA2FA_VERIFICATION_WINDOW_DAYS',
                14
            ) * 24
            now = timezone.now()
            verification_valid = (now - verified_at) < datetime.timedelta(
                hours=verification_window_hours
            )
            
            return verification_valid
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing 2FA verification timestamp: {str(e)}")
            return False