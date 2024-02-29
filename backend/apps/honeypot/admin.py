from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from honeypot.models import AccessLog


# Customize the admin interface for AccessLogs
class AccessLogModelAdmin(admin.ModelAdmin):
    # split into fieldsets
    fieldsets = [
        ("Access to", {"fields": ["path"]}),
        (
            "Request",
            {"fields": ["ip_address", "referrer", "method", "get", "post", "cookies"]},
        ),
        ("Meta", {"fields": ["session_key", "meta", "user"]}),
        ("Timestamp", {"fields": ["timestamp"]}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False  # NOTE this should be False in production

    def has_change_permission(self, request, obj=None):
        return False


# Register AccessLogModel with custom admin model
admin.site.register(AccessLog, AccessLogModelAdmin)

# Register all models
for model in apps.get_app_config("honeypot").get_models():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
