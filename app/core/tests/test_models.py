"""
Test for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test Models."""
    def test_create_user_with_email_successful(self):
        """Test creating an user with email successful"""
        email = "test@example.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_with_blank_email_exception(self):
        """Test exception creating a new user with email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='sample123'
            )

    def test_new_user_create_super_user(self):
        """Test create super user functionality"""
        user = get_user_model().objects.create_superuser(
            email="test_super_user@emaple.com",
            password="sample123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
