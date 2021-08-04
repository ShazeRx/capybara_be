from django.contrib.auth.models import User
from django.db import models


class ChannelManager(models.Manager):
    def get_or_create_channel(self, channel):
        pass


class Channel(models.Model):
    name = models.TextField(max_length=30, null=False, blank=False)
    users = models.ManyToManyField(User, null=False, blank=False)
    objects = ChannelManager()

    def __str__(self):
        return f'ID: {self.id} NAME: {self.name}'


class MessageManager(models.Manager):
    def get_last_10_messages_from_now(self, channel: Channel):
        return super().filter(channel=channel).order_by('-timestamp')[:10]

    def get_last_10_messages_from_timestamp(self, timestamp, channel: Channel):
        return super().filter(channel=channel, timestamp__lt=timestamp).order_by('-timestamp')[:10]


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=False, blank=False)
    objects = MessageManager()

    def __str__(self):
        return f'ID: {self.id}, AUTHOR: {self.author}, BODY: {self.message}, TIME: {self.timestamp}'
