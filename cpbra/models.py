from django.contrib.auth.models import User
from django.db import models


class ChannelManager(models.Manager):
    def get_or_create_channel(self, channel):
        pass


class MessageManager(models.Manager):
    def get_last_10_messages_from_now(self):
        pass

    def get_last_10_messages_from_message(self, message_id):
        pass


class Channel(models.Model):
    name = models.TextField(max_length=30, null=False, blank=False)
    users = models.ManyToManyField(User, null=False, blank=False)
    objects = ChannelManager()


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=False, blank=False)
    objects = MessageManager()
