"""
Test Tag APIs
"""

from core.models import Tag

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.serializers import TagSerializer

from rest_framework import status
from rest_framework.test import APIClient


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tagId):
    """return url to retrieve recipe_detail for a recipe id."""
    return reverse('recipe:tag-detail', args=[tagId])


def create_user(email='testuser@example.com', password='userpass123'):
    """create and return a user object"""
    return get_user_model().objects.create_user(email, password)


class PrivateTagAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicTagAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_list_retrieve_tags(self):
        """Test retrieve tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        tagSerializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagSerializer.data)

    def test_list_tags_for_authenticated_user(self):
        """Test list of Tags for authenticated user"""
        Tag.objects.create(user=self.user, name='Vegan')
        new_user = create_user(email='user1@example.com', password='testpass1')
        Tag.objects.create(user=new_user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)

        tagSerializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagSerializer.data)

    def test_update_tags(self):
        """Test update of tag object."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name': 'Dessert'}

        url = detail_url(tag.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(payload['name'], tag.name)
