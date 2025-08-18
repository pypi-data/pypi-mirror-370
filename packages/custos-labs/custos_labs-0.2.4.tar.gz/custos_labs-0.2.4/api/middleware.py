# alignment/api/middleware.py

from .tasks import log_token_usage
from django.utils.deprecation import MiddlewareMixin

from django.core.cache import cache
from django.contrib.auth.models import User

class RefreshTokenMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        refreshed_token = getattr(request, '_refreshed_token', None)
        if refreshed_token:
            response['X-Refreshed-Token'] = refreshed_token.key


        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Token "):
            token_key = auth_header.split()[1].strip()
            log_token_usage.delay(token_key, request.path)

        return response



def get_user_from_token(token):
    user_id = cache.get(f"session:{token}")
    if user_id:
        return User.objects.get(id=user_id)
    return None


class UsageLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Safely check for user and auth info
            user = getattr(request, "user", None)
            auth = getattr(request, "auth", None)

            if user and user.is_authenticated:
                print(f"[DEBUG] Authenticated user: {user.username}")
            elif auth:
                print(f"[DEBUG] Auth object present: {auth}")
            else:
                print("[DEBUG] Request is unauthenticated or no auth provided.")

        except Exception as e:
            print(f"[ERROR] Middleware failure: {e}")

        return self.get_response(request)

