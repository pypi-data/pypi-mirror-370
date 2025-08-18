# custos/decorators.py
import logging
from functools import wraps
from django.utils.timezone import now
from custos.models import AuditLog

def log_promotion(action):
    def decorator(func):
        @wraps(func)
        def wrapper(modeladmin, request, queryset):
            response = func(modeladmin, request, queryset)
            for user in queryset:
                AuditLog.objects.create(
                    actor=request.user,
                    action=action,
                    target_user=user,
                    timestamp=now()
                )
            return response
        return wrapper
    return decorator
