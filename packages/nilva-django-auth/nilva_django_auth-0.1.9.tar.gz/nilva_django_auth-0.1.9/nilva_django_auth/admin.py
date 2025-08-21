from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'last_activity', 'is_active', 'os', 'browser')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('id', 'user', 'jti', 'user_agent', 'ip_address',
                      'exp', 'created_at', 'last_activity', 'os', 'browser', 
                      'device_brand', 'device_model', 'device_family', 'is_mobile', 'referer')
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user',)
        }),
        (_('Session Information'), {
            'fields': ('id', 'jti', 'exp', 'is_active', 'created_at', 'last_activity', 'referer')
        }),
        (_('Device Information'), {
            'fields': ('user_agent', 'os', 'browser', 'device_brand',
                      'device_model', 'device_family', 'is_mobile')
        }),
        (_('Location Information'), {
            'fields': ('ip_address',)
        }),
    )
    
    def has_add_permission(self, request):
        # Sessions should only be created through the API, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Only allow changing the is_active status
        return True
    
    def get_readonly_fields(self, request, obj=None):
        # All fields are readonly except is_active
        if obj:
            return [f.name for f in obj._meta.fields if f.name != 'is_active']
        return self.readonly_fields