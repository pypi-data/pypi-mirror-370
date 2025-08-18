# alignment/chatbot_ai/models.py
from django.db import models
from django.contrib.auth.models import User


class ChatInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Chat with {self.user.username} at {self.timestamp}"
