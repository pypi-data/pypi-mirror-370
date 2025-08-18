# api/apikey_auth.py
import hashlib
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    """
    Accepts: Authorization: ApiKey <RAW_API_KEY>
    Resolves to the owning user and returns (user, APIKey).
    """
    keyword = "ApiKey"

    def authenticate(self, request):
        header = request.headers.get("Authorization") or ""
        if not header.startswith(f"{self.keyword} "):
            return None

        raw = header.split(None, 1)[1].strip()
        hashed = hashlib.sha256(raw.encode()).hexdigest()

        try:
            key_obj = APIKey.objects.select_related("user").get(hashed_key=hashed, revoked=False)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")

        return (key_obj.user, key_obj)
