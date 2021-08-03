from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.viewsets import ModelViewSet

from cpbra.chat.serializers import ChannelSerializer
from cpbra.models import Channel


class ChannelView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

    def create(self, request: Request, *args, **kwargs):
        """
        Create channel with given users ids
        """
        user_ids = request.data['users']
        if user_ids:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response({'message': 'user_ids should not be empty'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        List all channels which contain user in it
        """
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)
        channel_list = Channel.objects.filter(users=user)
        serializer = self.get_serializer(channel_list, many=True)
        return Response(serializer.data)
