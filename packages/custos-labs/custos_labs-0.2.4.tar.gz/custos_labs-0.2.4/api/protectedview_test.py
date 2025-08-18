# alignment/api/test_protected.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import ExpiringToken

class ProtectedTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password@123")
        self.token = ExpiringToken.objects.create(user=self.user)

    def test_access_protected(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get("/api/protected/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
