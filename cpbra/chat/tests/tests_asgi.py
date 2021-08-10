from unittest import TestCase

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf.urls import url
from django.contrib.auth.models import User
from model_bakery import baker

from cpbra.chat.consumers import ChatConsumer


class TestConsumer(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        self.user = User.objects.create_user(**user_data)
        self.channel = baker.make('Channel')

    @pytest.mark.django_db
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="unable to debug due to async nature of this tests")
    async def test_should_disconnect_when_not_authenticated(self):
        application = URLRouter([url(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{self.channel.id}/?token=some')
        connected, subprotocol = await communicator.connect()
        assert connected
        print(connected)
        await communicator.disconnect()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="unable to debug due to async nature of this tests")
    async def test_should_join_channel_when_authenticated(self):
        pass

    @pytest.mark.skip(reason="unable to debug due to async nature of this tests")
    async def test_should_send_and_receive_message(self):
        pass
