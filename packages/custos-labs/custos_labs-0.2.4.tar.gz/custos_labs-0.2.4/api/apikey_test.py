# alignment/api/test_apikey.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import ExpiringToken

class APIKeyTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password@123")
        self.token = ExpiringToken.objects.create(user=self.user)

    def test_generate_api_key(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post("/api/generate/", {"name": "Test Key"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("api_key", response.data)
