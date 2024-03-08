"""
Test Recipe APIs.
"""

from core.models import Recipe

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.serializers import RecipeSerializer

from rest_framework import status
from rest_framework.test import APIClient


RECIPES_LIST = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """create and return a recipe object."""
    defaults = {
        'title': 'Sample Test Recipe',
        'time_minutes': 10,
        'description': 'Sample Test Recipe Desciption.',
        'price': Decimal('3.45'),
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    "Test Public API requests."

    def setUp(self):
        self.client = APIClient()

    def test_list_recipe_unauthorized_access(self):
        """test unauthorized access of the list recipes."""
        response = self.client.get(RECIPES_LIST)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test Authorizded access to Recipe API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser@example.com',
            'testuser123',
        )
        self.client.force_authenticate(self.user)

    def test_list_retrive_recipes(self):
        "test retrieving a list of recipes."
        create_recipe(self.user)
        create_recipe(self.user)

        response = self.client.get(RECIPES_LIST)
        recipes = Recipe.objects.all().order_by('-id')
        recipeSerailizer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipeSerailizer.data)

    def test_list_recipe_for_authorized_user(self):
        """Test list of recipes is limited to authencated user."""
        new_user = get_user_model().objects.create_user(
            'new_user@example.com',
            'new_user123'
        )
        create_recipe(new_user)
        create_recipe(self.user)

        response = self.client.get(RECIPES_LIST)
        recipes = Recipe.objects.filter(user=self.user)
        recipeSerializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipeSerializer.data)
