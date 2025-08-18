# api/serializers.py
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from allauth.account.models import EmailAddress

from .models import APIKey
from .email_validation import validate_email_or_raise, EmailRejected


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["id", "name", "prefix", "created_at", "revoked"]


class CustomRegisterSerializer(RegisterSerializer):
    """
    Enforce real, deliverable email + block disposable; returns normalized email.
    """
    def validate_email(self, value: str) -> str:
        try:
            return validate_email_or_raise(value)
        except EmailRejected as e:
            raise serializers.ValidationError(e.detail)


class CustomLoginSerializer(LoginSerializer):
    """
    Refuse login until a verified email exists for the user (nice explicit error).
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        has_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
        if not has_verified:
            raise serializers.ValidationError("Please verify your email before logging in.")
        return data
