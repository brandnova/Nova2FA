"""
Nova2FA - Flexible Two-Factor Authentication for Django
"""

__version__ = "1.0.0"
__author__ = "Ijeoma Jahsway"
__email__ = "brandnova89@gmail.com"

default_app_config = 'nova2fa.apps.Nova2FAConfig'

# Import registry for easy access
from .registry import register_method, get_method, get_enabled_methods

__all__ = ['register_method', 'get_method', 'get_enabled_methods']