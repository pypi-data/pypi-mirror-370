# alignment/api/utils.py

import secrets
import hashlib
from django.core.cache import cache
from .models import ExpiringToken

def generate_api_key():
    raw_key = secrets.token_urlsafe(32)
    prefix = raw_key[:10]
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, prefix, hashed






def get_cached_token(key):
    token = cache.get(key)
    if token:
        return token
    try:
        token = ExpiringToken.objects.get(key=key)
        cache.set(key, token, timeout=60 * 60)
        return token
    except ExpiringToken.DoesNotExist:
        return None