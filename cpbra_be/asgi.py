import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import cpbra.chat.routing
from cpbra import chat
from cpbra_be.channelsmiddleware import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpbra_be.settings')

application = ProtocolTypeRouter({"http": get_asgi_application(),
                                  "websocket": TokenAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns))})
