"""
Test Recipe APIs.
"""

from core.models import Recipe, Tag

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

from rest_framework import status
from rest_framework.test import APIClient


RECIPES_URL = reverse('recipe:recipe-list')


def create_user(**payload):
    """create and return a user"""
    return get_user_model().objects.create_user(**payload)


def detail_url(recipe_id):
    """return url to retrieve recipe detail for a recipe_id"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


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
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test Authorizded access to Recipe API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )
        self.client.force_authenticate(self.user)

    def test_list_retrive_recipes(self):
        "test retrieving a list of recipes."
        create_recipe(self.user)
        create_recipe(self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        recipeSerailizer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipeSerailizer.data)

    def test_list_recipe_for_authenticated_user(self):
        """Test list of recipes is limited to authenticated user."""
        new_user = create_user(
            email='new_user@example.com',
            password='new_user123'
        )
        create_recipe(new_user)
        create_recipe(self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        recipeSerializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipeSerializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)

        response = self.client.get(url)
        detailSerializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, detailSerializer.data)

    def test_create_recipe(self):
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 10,
            'price': Decimal('12.0')
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])

        for k, v in payload.items():
            self.assertEqual(v, getattr(recipe, k))

    def test_partial_update_recipe(self):
        """test partial update of the recipe object"""
        original_link = 'http://example.com/test_recipe.pdf'
        data = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'link': original_link
        }

        recipe = create_recipe(self.user, **data)

        payload = {
            'title': 'Test Recipe 1'
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.title, payload['title'])

    def test_full_update(self):
        """test full update of the recipe object."""
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=10,
            price=Decimal('15.0'),
            description='Sample Recipe Description.',
            link='http://example.com/sample_recipe.pdf'
        )

        payload = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'price': Decimal('12.0'),
            'description': 'Test Recipe Description',
            'link': 'http://example.com/test_recipe.pdf'
        }

        url = detail_url(recipe.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(v, getattr(recipe, k))

    def test_update_user_returns_error(self):
        """Test changing the user of the recipe returns error."""
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=10,
            price=Decimal('15.0'),
            description='Sample Recipe Description.',
            link='http://example.com/sample_recipe.pdf'
        )

        new_user = create_user(
            email='test_user1@example.com',
            password='testpassword123'
        )

        url = detail_url(recipe.id)

        payload = {'user': new_user}
        _ = self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(self.user, recipe.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=10,
            price=Decimal('15.0'),
            description='Sample Recipe Description.',
            link='http://example.com/sample_recipe.pdf'
        )

        url = detail_url(recipe.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(
            email='test_user1@example.com',
            password='testpassword123'
        )
        recipe = create_recipe(
            user=new_user,
            title='Sample Recipe',
            time_minutes=10,
            price=Decimal('15.0'),
            description='Sample Recipe Description.',
            link='http://example.com/sample_recipe.pdf'
        )

        url = detail_url(recipe.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Fish Fingers',
            'time_minutes': 15,
            'price': Decimal('5.0'),
            'tags': [
                {
                    'name': 'Seafood',
                }, {
                    'name': 'Starters',
                }
            ]
        }

        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """test creating a recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Biryani',
            'time_minutes': 25,
            'price': Decimal('5.0'),
            'tags': [
                {
                    'name': 'Indian'
                }, {
                    'name': 'Main-Course'
                }
            ]
        }

        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)
