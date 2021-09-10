from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from cpbra.auth.serializers import UserSerializer


class TestUsers(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.user_list_url = reverse('users-list')

    @pytest.mark.django_db
    def setUp(self) -> None:
        self.user = User.objects.create_user(**self.user_data)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @pytest.mark.django_db
    def test_should_list_users_beside_current_user(self):
        baker.make('User', _quantity=2)
        response = self.client.get(path=self.user_list_url)
        self.assertEqual(len(response.data), 2)
        self.assertNotIn(self.user, response.data)

    @pytest.mark.django_db
    def test_should_return_user(self):
        response = self.client.get(path=reverse('users-detail', args=[self.user.id]))
        expected_json = UserSerializer(instance=self.user).data
        self.assertEqual(response.data, expected_json)
