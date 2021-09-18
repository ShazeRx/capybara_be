import json
from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from django.forms import model_to_dict
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from cpbra.models import Channel


def model_to_json(model):
    model_dict = model_to_dict(model)
    return json.dumps(model_dict)


class TestsChannelView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.channel_list_url = reverse('channels-list')

    @pytest.mark.django_db
    def setUp(self) -> None:
        self.user = User.objects.create_user(**self.user_data)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @pytest.mark.django_db
    def test_should_create_channel(self):
        users = baker.make('User', _quantity=2)
        users_ids = [user.id for user in users]
        channel_data = {
            "name": "some_name",
            "users": users_ids
        }
        response = self.client.post(path=self.channel_list_url, data=channel_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Channel.objects.count(), 1)

    @pytest.mark.django_db
    def test_should_throw_500_when_trying_to_create_channel_with_users_less_1(self):
        user = baker.make('User')
        channel_data = {
            "name": "some_name",
            "users": ""
        }
        response = self.client.post(path=self.channel_list_url, data=channel_data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(Channel.objects.count(), 0)

    @pytest.mark.django_db
    def test_should_remove_channel(self):
        channel = baker.make('Channel', users=[self.user, ])
        url = reverse('channels-detail', args=[channel.id, ])
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Channel.objects.count(), 0)

    @pytest.mark.django_db
    def test_should_throw_401_when_trying_to_remove_channel_but_not_part_of(self):
        channel = baker.make('Channel')
        url = reverse('channels-detail', args=[channel.id, ])
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Channel.objects.count(), 1)

    @pytest.mark.django_db
    def test_should_list_channels(self):
        baker.make('Channel', _quantity=2, users=[self.user, ])
        response = self.client.get(path=self.channel_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    @pytest.mark.django_db
    def test_should_join_channel(self):
        channel = baker.make('Channel', users=[])
        url = reverse('channels-join', args=[channel.id, ])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(channel.users.first(), self.user)

    @pytest.mark.django_db
    def test_should_leave_channel(self):
        channel = baker.make('Channel', users=[self.user, ])
        url = reverse('channels-leave', args=[channel.id, ])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(channel.users.count(), 0)

    @pytest.mark.django_db
    def test_should_list_channels_for_in_which_user_is_part_of(self):
        baker.make('Channel', users=[self.user, ])
        baker.make('Channel')
        response = self.client.get(path=self.channel_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
