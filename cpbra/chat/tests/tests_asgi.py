import asyncio
from asyncio import sleep
from typing import List

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from model_bakery import baker

from cpbra.auth.serializers import UserToken
from cpbra.models import Channel, Message
from cpbra_be import asgi, settings


@database_sync_to_async
def save_user(user_data: dict):
    return User.objects.create_user(**user_data)


@database_sync_to_async
def save_channel():
    return baker.make('Channel')


@database_sync_to_async
def get_user_token(user: User):
    return UserToken.get_token(user)


@database_sync_to_async
def create_messages_in_channel(user: User, channel: Channel):
    return baker.make('Message', channel=channel, author=user, _quantity=25)


class TestConsumer:

    @pytest.yield_fixture(scope='session')
    def event_loop(self):
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.django_db
    @pytest.fixture(autouse=True, scope='class')
    @pytest.mark.django_db_setup
    async def user(self, event_loop, django_db_blocker, django_db_setup):
        with django_db_blocker.unblock():
            self.user_data = {
                'email': 'some_email',
                'username': 'some_username1',
                'password': 'some_password'
            }
            self.user = await save_user(self.user_data)
        return self.user

    @pytest.mark.django_db
    @pytest.fixture(autouse=True, scope='class')
    @pytest.mark.django_db_setup
    async def channel(self, event_loop, django_db_blocker, django_db_setup):
        with django_db_blocker.unblock():
            self.channel = await save_channel()
        return self.channel

    @pytest.mark.django_db
    @pytest.fixture(autouse=True, scope='class')
    @pytest.mark.django_db_setup
    @pytest.mark.asyncio
    async def messages(self, event_loop, django_db_blocker, django_db_setup, user, channel):
        with django_db_blocker.unblock():
            self.messages = await create_messages_in_channel(user, channel)
        return self.messages

    @pytest.fixture(autouse=True, scope='function')
    async def setup_settings(self):
        settings.SECRET_KEY = 'secret'
        return settings

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_should_disconnect_when_not_authenticated(self, user: User, channel: Channel, setup_settings):
        token = await get_user_token(user)
        application = asgi.application
        setup_settings.SECRET_KEY = 'secret1'
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{channel.id}/?token={token}')
        connected, subprotocol = await communicator.connect()
        assert not connected
        print(connected)
        await communicator.disconnect()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_should_join_channel_when_authenticated(self, user: User, channel: Channel, setup_settings):
        token = await get_user_token(user)
        application = asgi.application
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{channel.id}/?token={token}')
        connected, subprotocol = await communicator.connect()
        assert connected
        print(connected)
        await communicator.disconnect()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_should_send_and_receive_message(self, user: User, channel: Channel):
        token = await get_user_token(user)
        application = asgi.application
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{channel.id}/?token={token}')
        connected, subprotocol = await communicator.connect()
        assert connected
        await communicator.send_json_to({"command": "new_message", "body": "some_body"})
        response = await communicator.receive_json_from()
        assert response['message']['message'] == 'some_body'
        assert response['message']['author'] == user.username
        await communicator.disconnect()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    @pytest.mark.skip("Async fetching goes wrong, when assertion is being checked, messages are still in saving process")
    async def test_should_fetch_last_10_messages(self, user: User, channel: Channel, messages: List[Message]) -> None:
        token = await get_user_token(user)
        application = asgi.application
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{channel.id}/?token={token}')
        connected, subprotocol = await communicator.connect()
        assert connected
        await communicator.send_json_to({"command": "fetch_messages"})
        response = await communicator.receive_json_from()
        assert len(response) == 10
        assert response[0][
                   'id'] == 25  # check if first and last element is arranged in order (the newer message the higher id)
        assert response[9]['id'] == 16
        await communicator.disconnect()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    @pytest.mark.skip("Async fetching goes wrong, when assertion is being checked, messages are still in saving process")
    async def test_should_fetch_last_10_messages_from_timestamp(self, user: User, channel: Channel,
                                                                messages: List[Message]) -> None:
        token = await get_user_token(user)
        application = asgi.application
        communicator = WebsocketCommunicator(application,
                                             f'/ws/chat/{channel.id}/?token={token}')
        connected, subprotocol = await communicator.connect()
        assert connected
        await communicator.send_json_to({"command": "fetch_messages", "timestamp": str(messages[10].timestamp)})
        response = await communicator.receive_json_from()
        assert len(response) == 10
        assert response[0][
                   'id'] == 10  # check if first and last element is arranged in order (the newer message the higher id)
        assert response[9]['id'] == 1
        await communicator.disconnect()
