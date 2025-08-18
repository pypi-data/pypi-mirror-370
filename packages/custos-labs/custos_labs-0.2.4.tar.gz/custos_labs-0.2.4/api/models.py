# alignment/api/models.py

from django.db import models
from django.contrib.auth.models import User
import secrets, hashlib

class APIKey(models.Model):
    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=10, editable=False)
    hashed_key = models.CharField(max_length=64, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    @staticmethod
    def generate_hashed_key():
        raw = secrets.token_urlsafe(32)
        prefix = raw[:10]
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, prefix, hashed


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signup_method = models.CharField(max_length=20, choices=[
        ("email", "Email"),
        ("google", "Google"),
        ("github", "GitHub")
    ])

class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_actor_logs')
    action = models.CharField(max_length=255)
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_target_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} {self.action}d {self.target} at {self.timestamp}"


class UserActivityLog(models.Model):
    LOGIN = 'login'
    LOGOUT = 'logout'
    OTHER = 'other'

    ACTION_CHOICES = [
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (OTHER, 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)


class APIUsageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=128)
    method = models.CharField(max_length=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
