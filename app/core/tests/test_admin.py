"""
Test Admin Functionalities.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.urls import reverse


class AdminFunctionalitiesTest(TestCase):
    """Testing Admin Functionalities"""
    def setUp(self):
        """setting up client and users"""
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            email="adminuser@example.com",
            password="password123"
        )
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password",
            name="user"
        )

    def test_admin_list_users_functionality(self):
        """test users are listed on a page"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(path=url)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)

    def test_admin_edit_user_page(self):
        """test working of the admin-side edit user page"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_create_user_page(self):
        """test working of the admin-side create user page"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
