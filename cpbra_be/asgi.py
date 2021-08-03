import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import cpbra.chat.routing
from cpbra import chat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpbra_be.settings')

application = ProtocolTypeRouter({"http": get_asgi_application(),
                                  "websocket": AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))})
