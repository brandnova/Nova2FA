from django.contrib import admin
from .models import UserTwoFactorSettings, EmailOTP


@admin.register(UserTwoFactorSettings)
class UserTwoFactorSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_enabled', 'method', 'last_verified', 'created_at']
    list_filter = ['is_enabled', 'method', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'last_verified']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Settings', {
            'fields': ('is_enabled', 'method', 'totp_secret')
        }),
        ('Backup Codes', {
            'fields': ('backup_codes', 'used_backup_codes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_verified', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'user__username', 'code']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False