from smtplib import SMTPException

import jwt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from cpbra.auth.serializers import UserSerializer
from cpbra.auth.utils import MailSenderUtil
from cpbra_be import settings


class LoginView(APIView):
    def post(self, request, *args, **kwargs) -> Response:
        """
        Enpoint for authenticate and login user
        :param request: Pure http request
        :return: If user is authenticated and is active then returns pair of tokens (refresh,access),
         if not then 401 code will be returned
        """
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        serializer = UserSerializer(user)
        if user is not None:
            return Response(status=200, data=serializer.get_user_data_with_token(user))
        return Response(data={"message": "User not activated or does not exist"}, status=status.HTTP_403_FORBIDDEN)


class RegisterView(APIView):
    """
    View for registering user
    """
    model = User
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        tokens = serializer.get_token(User.objects.get(id=user_data['id']))
        try:
            MailSenderUtil.send_email(request=request, user_data=user_data, tokens=tokens)
        except SMTPException:
            user = User.objects.get(id=serializer.data['id'])
            user.delete()
            return Response(data={'message': 'Internal error occurred, your account has not been created'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'user': {**user_data}}, status=status.HTTP_201_CREATED)


class VerifyEmailView(GenericAPIView):
    """
    View for verifying an email
    """

    def post(self, request, *args, **kwargs):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'message': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
