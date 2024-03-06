"""
Test user api functionalities
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public functionalities of User API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successfull(self):
        """Test successfull creation of a user."""
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(payload['password']))

    def test_user_wit_email_exists_error(self):
        """Test user creatiom with e-mail exists error"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'testuser@example.com',
            'password': 'pass',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)