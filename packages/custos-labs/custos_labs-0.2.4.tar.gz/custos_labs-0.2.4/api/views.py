# alignment/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import APIKey
from .serializers import APIKeySerializer

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username and password required."}, status=400)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials."}, status=401)
        if not user.emailaddress_set.filter(verified=True).exists():
            return Response({"error": "Please verify your email before logging in."}, status=401)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
        })

class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"error": "Key name required."}, status=400)
        if APIKey.objects.filter(user=request.user).exists():
            return Response(
                {"error": "API key already exists for this user. Please delete it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        raw_key, prefix, hashed = APIKey.generate_hashed_key()
        apikey = APIKey.objects.create(
            name=name,
            prefix=prefix,
            hashed_key=hashed,
            user=request.user
        )
        return Response({
            "api_key": raw_key,
            "key_id": apikey.id,
            "prefix": prefix,
            "note": "This is the only time the full API key will be shown. Please store it securely.",
        }, status=status.HTTP_201_CREATED)







class DeleteAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, key_id):
        try:
            apikey = APIKey.objects.get(id=key_id, user=request.user)
            apikey.delete()
            return Response({"success": "API key deleted."}, status=status.HTTP_204_NO_CONTENT)
        except APIKey.DoesNotExist:
            return Response({"error": "API key not found."}, status=status.HTTP_404_NOT_FOUND)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class TokenValidateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"valid": True, "user": request.user.username})
    


class ListUserAPIKeysView(APIView):
    """
    GET /api/my-api-keys/
    Returns only unrevoked keys for the current authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch API keys for this user that aren't revoked
        keys = APIKey.objects.filter(user=request.user, revoked=False)
        # Serialize them and return
        return Response(APIKeySerializer(keys, many=True).data)


class ListAPIKeysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keys = APIKey.objects.filter(user=request.user)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)