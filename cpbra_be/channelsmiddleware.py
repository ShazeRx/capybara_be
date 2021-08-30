import os

import jwt
from channels.db import database_sync_to_async
from django.contrib.auth.models import User, AnonymousUser
from django.db import close_old_connections


@database_sync_to_async
def get_user(token):
    try:
        payload = jwt.decode(jwt=token, key=os.environ.get('SECRET_KEY'), algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return user
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return AnonymousUser()


class TokenAuthMiddleware:
    """Custom auth for JWT authentication"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query = dict(x.split('=') for x in scope['query_string'].decode().split('&'))
        token = query.get('token')
        scope['user'] = await get_user(token)
        return await self.app(scope, receive, send)
