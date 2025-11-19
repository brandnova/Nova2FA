from django.urls import path
from . import views

app_name = 'nova2fa'

urlpatterns = [
    # Main settings
    path('settings/', views.nova2fa_settings, name='settings'),
    
    # Setup flow
    path('setup/', views.setup_2fa, name='setup'),
    path('setup/totp/', views.setup_totp, name='setup_totp'),
    path('setup/qr-code/', views.qr_code, name='qr_code'),
    path('setup/email/verify/', views.verify_email_otp, name='verify_email_otp'),
    path('setup/email/request/', views.request_email_otp, name='request_email_otp'),
    
    # Verification flow
    path('verify/', views.verify_2fa, name='verify'),
    path('verify/email/request/', views.request_verification_otp, name='request_verification_otp'),
    
    # Management
    path('disable/', views.disable_2fa, name='disable'),
    path('backup-codes/', views.view_backup_codes, name='view_backup_codes'),
    path('backup-codes/regenerate/', views.regenerate_backup_codes, name='regenerate_backup_codes'),
    path('change-method/', views.change_2fa_method, name='change_method'),
]