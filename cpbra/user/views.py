from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cpbra.auth.serializers import UserSerializer


class UserView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        current_user = self.request.user
        users = User.objects.all().exclude(id=current_user.id)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
