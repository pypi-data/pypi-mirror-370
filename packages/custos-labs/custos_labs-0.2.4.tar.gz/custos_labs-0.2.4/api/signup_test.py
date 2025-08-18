# alignment/api/test_signup.py
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User

class SignupTest(APITestCase):
    def test_user_signup(self):
        url = reverse("signup")
        data = {
            "username": "testuser0",
            "password": "Password@123",
            "email": "testuser@example.com"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
