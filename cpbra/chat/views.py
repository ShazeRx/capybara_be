from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_204_NO_CONTENT, \
    HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet

from cpbra.chat.serializers import ChannelSerializer
from cpbra.models import Channel


class ChannelView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create channel with given users ids
        """
        user_ids = request.data['users']
        if len(user_ids) >= 2:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response({'message': 'users should be at least 2'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs) -> Response:
        """
        List all channels which contain user in it
        """
        user = self.request.user
        channel_list = Channel.objects.filter(users=user)
        serializer = self.get_serializer(channel_list, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def join(self, request: Request, *args, **kwargs) -> Response:
        """
        Join to channel
        """
        channel_pk = kwargs.get('pk')
        user = self.request.user
        channel = Channel.objects.get(id=channel_pk)
        if user not in channel.users.all():
            channel.users.add(user)
            channel.save()
        return Response(status=HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def leave(self, request: Request, *args, **kwargs) -> Response:
        """
        Leave channel
        """
        channel_pk = kwargs.get('pk')
        user = self.request.user
        channel = Channel.objects.get(id=channel_pk)
        if user in channel.users.all():
            channel.users.remove(user)
            channel.save()
        return Response(status=HTTP_200_OK)

    def destroy(self, request: Request, *args, **kwargs):
        """
        Remove channel
        """
        channel_pk = kwargs.get('pk')
        user = self.request.user
        channel = Channel.objects.get(id=channel_pk)
        if user in channel.users.all():
            channel.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_401_UNAUTHORIZED)
