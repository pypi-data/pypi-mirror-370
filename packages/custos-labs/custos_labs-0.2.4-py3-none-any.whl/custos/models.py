# custos/models.py

from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custos_actor_logs')
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custos_target_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} {self.action}d {self.target_user} at {self.timestamp}"
