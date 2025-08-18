# # api/custos_adminsite.py

# from django.contrib.admin import AdminSite, ModelAdmin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth import get_user_model
# from .models import APIKey, Profile, AuditLog, UserActivityLog, APIUsageLog

# User = get_user_model()

# class CustosAdminSite(AdminSite):
#     site_header = "Custos Labs Admin Dashboard"
#     site_title = "Custos Labs Admin Panel"
#     index_title = "Welcome to Custos Labs Analytics"

# admin_site = CustosAdminSite(name='custos_admin')

# class APIKeyAdmin(ModelAdmin):
#     list_display = ('user', 'name', 'prefix', 'created_at', 'revoked')
#     list_filter = ('revoked', 'created_at')
#     search_fields = ('user__username', 'prefix', 'name')
#     date_hierarchy = 'created_at'
#     readonly_fields = ('prefix', 'hashed_key')
# admin_site.register(APIKey, APIKeyAdmin)

# class ProfileAdmin(ModelAdmin):
#     list_display = ('user', 'signup_method')
#     list_filter = ('signup_method',)
#     search_fields = ('user__username',)
# admin_site.register(Profile, ProfileAdmin)

# class AuditLogAdmin(ModelAdmin):
#     list_display = ('actor', 'action', 'target', 'timestamp')
#     list_filter = ('action', 'timestamp')
#     search_fields = ('actor__username', 'target__username', 'action')
#     date_hierarchy = 'timestamp'
# admin_site.register(AuditLog, AuditLogAdmin)

# class UserActivityLogAdmin(ModelAdmin):
#     list_display = ('user', 'action', 'timestamp', 'ip_address')
#     list_filter = ('action', 'timestamp', 'user')
#     date_hierarchy = 'timestamp'
#     search_fields = ('user__username', 'ip_address', 'user_agent')
# admin_site.register(UserActivityLog, UserActivityLogAdmin)

# class APIUsageLogAdmin(ModelAdmin):
#     list_display = ('user', 'endpoint', 'method', 'tokens_used', 'timestamp', 'ip_address')
#     list_filter = ('method', 'endpoint', 'timestamp')
#     search_fields = ('user__username', 'endpoint', 'ip_address')
#     date_hierarchy = 'timestamp'
# admin_site.register(APIUsageLog, APIUsageLogAdmin)

# class CustomUserAdmin(UserAdmin):
#     pass
# admin_site.register(User, CustomUserAdmin)
