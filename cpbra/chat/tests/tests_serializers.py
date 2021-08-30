from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from model_bakery import baker

from cpbra.auth.serializers import UserSerializer
from cpbra.chat.serializers import ChannelSerializer


class ChannelSerializerTest(TestCase):

    @pytest.mark.django_db
    def setUp(cls) -> None:
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.user = User.objects.create_user(**cls.user_data)

    @pytest.mark.django_db
    def test_should_retrieve_user_list(self):
        channel = baker.make('Channel', users=[self.user])
        channel_serializer = ChannelSerializer()
        user_serializer = UserSerializer(self.user)
        self.assertEqual(len(channel_serializer.get_users_list(channel)), 1)
        self.assertEqual(channel_serializer.get_users_list(channel)[0], user_serializer.data)
