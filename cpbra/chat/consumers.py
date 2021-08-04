from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from cpbra.chat.serializers import MessageSerializer
from cpbra.models import Channel, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        channel = await self.get_channel(self.room_name)
        if channel is None:
            await self.accept()
            await self.send_json({"type": "error", "message": "Channel does not exist."})
            await self.close()
        self.room_group_name = 'chat_%s' % self.room_name
        if self.scope["user"].is_anonymous:
            await self.close()
        else:

            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def fetch_messages(self, event):
        timestamp = event.get('timestamp', None)
        messages_list = await self.fetch_messages_from_db(self.room_name, timestamp)
        serializer = MessageSerializer(messages_list, many=True)
        await self.send_json(serializer.data)

    async def new_message(self, event):
        message_body = event['body']
        message = await self.save_message_to_db(message_body)
        content = {
            'command': 'new_message',
            'message': await self.message_to_json(message)
        }
        await self.send_to_channel(content)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    async def receive_json(self, content, **kwargs):
        """
        Called when received a message (assume other user in channel)
        """
        await self.commands[content.get('command')](self, content)

    async def send_to_channel(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        """
        Called when someone has messaged
        """
        message = event['message']
        await self.send_json({
            'message': message
        })

    async def message_to_json(self, message: Message):
        return {
            "id": message.id,
            'author': message.author.username,
            'message': message.message,
            'timestamp': str(message.timestamp)
        }

    @database_sync_to_async
    def get_channel(self, channel_id):
        try:
            return Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message_to_db(self, message_body):
        return Message.objects.create(author=self.scope['user'], message=message_body, channel_id=self.room_name)

    @database_sync_to_async
    def fetch_messages_from_db(self, channel_id: int, timestamp: str):
        channel = Channel.objects.get(id=channel_id)
        if timestamp:
            return list(Message.objects.get_last_10_messages_from_timestamp(timestamp, channel))
        return list(Message.objects.get_last_10_messages_from_now(channel))
