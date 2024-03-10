"""
Test for models.
"""

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model


def create_user(email="test_user@example.com", password="testpass123"):
    """create and return a user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test Models."""
    def test_create_user_with_email_successful(self):
        """Test creating an user with email successful"""
        email = "test@example.com"
        password = "test123"
        user = create_user(
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
            user = create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_with_blank_email_exception(self):
        """Test exception creating a new user with email"""
        with self.assertRaises(ValueError):
            create_user(
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

    def test_create_new_recipe_successful(self):
        """Test create new recipe by user."""
        user = create_user(
            email="testuser@example.com",
            password="testpass123"
        )

        recipe = Recipe.objects.create(
            user=user,
            title='Sample Recipe',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample Recipe Description.'
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create new tag"""
        user = create_user()
        tag = Tag.objects.create(
            user=user,
            name='Tag1'
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test create a new ingredient."""
        user = create_user()
        ingredient = Ingredient.objects.create(
            user=user,
            name='Sample Ingredient',
        )

        self.assertEqual(str(ingredient), ingredient.name)