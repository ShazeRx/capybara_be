import datetime
from unittest import TestCase

import jwt
import pytest
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from cpbra.auth.serializers import UserSerializer
from cpbra_be import settings


class TestLoginView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login_url = reverse("login")
        cls.client = APIClient()

    @pytest.mark.django_db
    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email"
        }
        self.user = User.objects.create_user(**self.data)

    @pytest.mark.django_db
    def test_can_login(self):
        # given
        body = {
            "username": self.data["username"],
            "password": self.data["password"]
        }
        # when
        response = self.client.post(self.login_url, data=body)
        # then
        self.assertEqual(response.status_code, 200)

    @pytest.mark.django_db
    def test_should_return_user_data_with_tokens(self):
        # given
        body = {
            "username": self.data["username"],
            "password": self.data["password"]
        }
        # when
        response = self.client.post(self.login_url, data=body)
        # then
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user'], serializer.data)
        self.assertNotEqual(response.json()['token']['access'], "" and response.json()['token']['refresh'], "")

    @pytest.mark.django_db
    def test_should_throw_403_when_user_not_exist(self):
        # given
        body = {
            "username": "some",
            "password": "body"
        }
        # when
        response = self.client.post(self.login_url, data=body)
        # then
        self.assertEqual(response.status_code, 403)

    @pytest.mark.django_db
    def test_should_throw_403_when_body_is_empty(self):
        # given
        body = {
            "username": "",
            "password": ""
        }
        # when
        response = self.client.post(self.login_url, data=body)
        # then
        self.assertEqual(response.status_code, 403)


class TestRegisterView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.register_url = reverse('register')
        cls.client = APIClient()

    @pytest.mark.django_db
    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email@email.com"
        }

    @pytest.mark.django_db
    def test_should_register_successfully(self):
        # when
        response = self.client.post(self.register_url, data=self.data)
        # then
        self.assertEqual(response.status_code, 201)

    @pytest.mark.django_db
    def test_user_should_be_inactive(self):
        # when
        response = self.client.post(self.register_url, data=self.data)
        # then
        self.assertEqual(response.status_code, 201)
        assert User.objects.all().first().is_active == False

    @pytest.mark.django_db
    def test_user_should_correct_response(self):
        # when
        response = self.client.post(self.register_url, data=self.data)
        # then
        user = User.objects.all().first()
        assert response.data == {'user': {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }}

    @pytest.mark.django_db
    def test_should_throw_400_when_empty_username(self):
        # given
        data = {
            "username": "",
            "password": "world",
            "email": "email@email.com"
        }
        # when
        response = self.client.post(self.register_url, data=data)
        # then
        self.assertEqual(response.status_code, 400)

    @pytest.mark.django_db
    def test_should_throw_400_when_empty_password(self):
        # given
        data = {
            "username": "hello1",
            "password": "",
            "email": "email@email.com"
        }
        # when
        response = self.client.post(self.register_url, data=data)
        # then
        self.assertEqual(response.status_code, 400)

    @pytest.mark.django_db
    def test_should_throw_400_when_email_is_not_valid(self):
        # given
        data = {
            "username": "hello1",
            "password": "world",
            "email": "emailemail.com"
        }
        # when
        response = self.client.post(self.register_url, data=data)
        # then
        self.assertEqual(response.status_code, 400)

    @pytest.mark.django_db
    def test_should_throw_400_when_email_is_empty(self):
        # given
        data = {
            "username": "hello1",
            "password": "world",
            "email": ""
        }
        # when
        response = self.client.post(self.register_url, data=data)
        # then
        self.assertEqual(response.status_code, 400)

    @pytest.mark.django_db
    def test_should_throw_400_when_email_exist(self):
        # given
        user1_data = {
            "username": "hello1",
            "password": "world",
            "email": "email@email.com"
        }
        user2_data = {
            "username": "hello2",
            "password": "world",
            "email": "email@email.com"
        }
        # when
        self.client.post(self.register_url, data=user1_data)
        # and
        response = self.client.post(self.register_url, data=user2_data)
        # then
        self.assertEqual(response.status_code, 400)

    @pytest.mark.django_db
    @pytest.mark.skip("Skipped due to removed feature - CPBRA-41")
    def test_should_return_token_set(self):
        # when
        response = self.client.post(self.register_url, data=self.data)
        # then
        self.assertEqual(len(response.data), 2)

    @pytest.mark.django_db
    @pytest.mark.skip("Skipped due to removed feature - CPBRA-41")
    def test_should_return_valid_tokens_pairs(self):
        # when
        response = self.client.post(self.register_url, data=self.data)
        # then
        self.assertNotEqual(response.json()['access'], "" and response.json()['refresh'], "")


class TestVerifyEmailView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.email_verify_url = reverse('email-verify')
        cls.client = APIClient()

    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email",
            "is_active": False
        }
        self.user = User.objects.create_user(**self.data)
        self.serializer = UserSerializer()
        self.token = self.serializer.get_token(self.user)['access']

    @pytest.mark.django_db
    def test_should_activate_user(self):
        # when
        response = self.client.post(f'{self.email_verify_url}?token={self.token}')
        # then
        self.user.refresh_from_db()
        self.assertEqual({'message': 'Successfully activated'}, response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.is_active, True)

    @pytest.mark.django_db
    def test_should_throw_invalid_token_error_when_bad_sign(self):
        # when
        settings.SECRET_KEY = 'secret1'
        response = self.client.post(f'{self.email_verify_url}?token={self.token}')
        # then
        self.user.refresh_from_db()
        self.assertEqual({'error': "Invalid token"}, response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.user.is_active, False)

    @pytest.mark.django_db
    def test_should_throw_activation_expired_when_jwt_expired(self):
        # given
        token = self.token
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')
        # when
        response = self.client.post(f'{self.email_verify_url}?token={token}')
        # then
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, False)
        self.assertEqual({'error': 'Activation Expired'}, response.data)
        self.assertEqual(response.status_code, 400)
