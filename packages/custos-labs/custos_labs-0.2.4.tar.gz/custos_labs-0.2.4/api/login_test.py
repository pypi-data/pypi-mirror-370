# alignment/api/test_login.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from api.models import ExpiringToken

class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password@123")
        ExpiringToken.objects.create(user=self.user)

    def test_login_success(self):
        url = reverse("login")
        data = {"username": "testuser", "password": "Password@123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
