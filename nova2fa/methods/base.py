"""
Base class for 2FA methods.
"""


class Base2FAMethod:
    """
    Base class for all 2FA authentication methods.
    """
    name = ""
    verbose_name = ""
    
    def send(self, user):
        """
        Send the 2FA token to the user.
        
        Args:
            user: Django user instance
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement send()")
    
    def verify(self, user, token):
        """
        Verify the provided token.
        
        Args:
            user: Django user instance
            token (str): Token to verify
            
        Returns:
            bool: True if valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement verify()")
    
    def setup(self, user):
        """
        Perform any setup required for this method.
        
        Args:
            user: Django user instance
            
        Returns:
            dict: Setup data (e.g., QR code URL, secret key)
        """
        return {}
    
    def is_configured(self, user):
        """
        Check if this method is configured for the user.
        
        Args:
            user: Django user instance
            
        Returns:
            bool: True if configured, False otherwise
        """
        return True