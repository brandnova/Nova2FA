"""
Registry for 2FA methods.
"""
from django.conf import settings

# Global registry for 2FA methods
_METHODS = {}


def register_method(code, handler):
    """
    Register a 2FA method.
    
    Args:
        code (str): Unique identifier for the method (e.g., 'email', 'totp')
        handler: Instance of a Base2FAMethod subclass
    """
    _METHODS[code] = handler


def get_method(code):
    """
    Get a registered 2FA method by code.
    
    Args:
        code (str): Method identifier
        
    Returns:
        Base2FAMethod instance or None
    """
    return _METHODS.get(code)


def get_enabled_methods():
    """
    Get all enabled 2FA methods based on settings.
    
    Returns:
        dict: Dictionary of enabled methods {code: handler}
    """
    enabled = getattr(settings, 'NOVA2FA_ENABLED_METHODS', ['email', 'totp'])
    return {code: handler for code, handler in _METHODS.items() if code in enabled}


def get_method_choices():
    """
    Get choices for form fields.
    
    Returns:
        list: List of tuples [(code, verbose_name), ...]
    """
    enabled = get_enabled_methods()
    return [(code, handler.verbose_name) for code, handler in enabled.items()]