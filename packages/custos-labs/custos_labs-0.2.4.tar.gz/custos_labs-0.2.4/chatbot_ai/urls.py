# alignment/chatbot_ai/urls.py
from django.urls import path
from .views import ChatBotAPIView

urlpatterns = [
    path("chat/", ChatBotAPIView.as_view(), name="chatbot-ai"),
]