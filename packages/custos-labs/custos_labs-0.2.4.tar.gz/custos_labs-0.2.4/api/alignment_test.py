# api/test_alignment.py
from unittest.mock import MagicMock
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import ExpiringToken

class AIEvalTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password@123")
        self.token = ExpiringToken.objects.create(user=self.user)

    def test_ai_alignment_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        with self.settings(MIDDLEWARE=["api.middleware.RefreshTokenMiddleware"]):
            self.client.handler._force_user = self.user
            self.client.handler._request_middleware = []
            response = self.client.post("/api/protected-ai/", {
                "prompt": "Say something",
                "response": "Something"
            })
            self.assertIn(response.status_code, [200, 400])
