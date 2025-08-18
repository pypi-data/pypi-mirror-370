# alignment/api/authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from .models import ExpiringToken
from .utils import get_cached_token
from .tasks import log_token_usage

from custos.guardian import CustosGuardian


class ExpiringTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        print(f"[DEBUG] Raw Authorization header: {auth_header}")

        if not auth_header or not auth_header.startswith(self.keyword):
            print("[DEBUG] Missing or invalid Authorization header format.")
            return None

        try:
            key = auth_header.split()[1].strip()
        except IndexError:
            print("[DEBUG] Malformed Authorization header.")
            raise AuthenticationFailed(_('Invalid token format.'))

        # First check in cache (if available)
        token = get_cached_token(key)

        if not token:
            try:
                token = ExpiringToken.objects.get(key=key)
            except ExpiringToken.DoesNotExist:
                print("[DEBUG] Token not found.")
                raise AuthenticationFailed(_('Invalid token.'))

        if token.is_expired():
            print("[DEBUG] Token expired. Auto-refreshing...")
            token.refresh()
            raise AuthenticationFailed({
                'detail': 'Token expired and was refreshed.',
                'new_token': token.key,
            })

        # Attach CustosGuardian to request
        request.custos_guardian = CustosGuardian(api_key=token.key)

        # Log usage asynchronously
        log_token_usage.delay(token.key, request.path)

        print(f"[DEBUG] Authenticated user: {token.user.username}")
        return (token.user, token)
