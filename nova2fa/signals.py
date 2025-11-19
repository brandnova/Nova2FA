from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_two_factor_settings(sender, instance, created, **kwargs):
    """
    Create UserTwoFactorSettings for newly created users.
    """
    if created:
        from .models import UserTwoFactorSettings
        UserTwoFactorSettings.objects.create(user=instance)