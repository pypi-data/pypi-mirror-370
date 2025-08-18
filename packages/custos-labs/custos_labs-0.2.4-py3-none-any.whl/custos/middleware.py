## custos/middleware.py

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from custos.models import AuditLog


logger = logging.getLogger("usage_logger")


class UsageLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, '_start_time', time.time())
        user = getattr(request, 'user', None)
        api_key = request.headers.get("Authorization", "").replace("Token ", "")
        path = request.path

        log_data = {
            "timestamp": str(now()),
            "path": path,
            "method": request.method,
            "user": user.username if user and user.is_authenticated else "Anonymous",
            "api_key_used": api_key[:8] + "..." if api_key else None,
            "duration_sec": round(duration, 4),
            "status": response.status_code,
        }

        logger.info(f"[API USAGE] {log_data}")
        return response



def log_logout(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            actor=request.user,
            action="logout",
            target_user=request.user,
            timestamp=now()
        )
