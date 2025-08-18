# alignment/api/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class AuthFlowTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.api_key_url = reverse('generate-api-key')
        self.protected_url = reverse('protected')
        self.token_validation_url = reverse('token-validate')

        self.user_data = {
            "username": "testuser",
            "password": "Test@1234",
            "email": "test@example.com"
        }

    def test_signup(self):
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_login(self):
        User.objects.create_user(username=self.user_data["username"],
                                 email=self.user_data["email"],
                                 password=self.user_data["password"])
        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.token = response.data["token"]

    def test_api_key_generation(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.post(self.api_key_url, {"name": "Test Key"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("api_key", response.data)

    def test_protected_view_access(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_token_validation(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.token_validation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
