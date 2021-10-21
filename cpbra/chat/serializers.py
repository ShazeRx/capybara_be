from django.contrib.auth.models import User
from rest_framework import serializers

from cpbra.auth.serializers import UserSerializer
from cpbra.models import Channel, Message


class ChannelSerializer(serializers.ModelSerializer):
    users_list = serializers.SerializerMethodField()
    users = serializers.PrimaryKeyRelatedField(write_only=True, many=True, queryset=User.objects.all())

    class Meta:
        model = Channel
        fields = "__all__"
        read_only_fields = ("id", "users_list")

    def get_users_list(self, channel: Channel):
        serializer = UserSerializer(channel.users, many=True)
        return serializer.data


class MessageSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField()
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "timestamp")
