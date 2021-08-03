from rest_framework import routers

from cpbra.chat.views import ChannelView

channel_router = routers.SimpleRouter()
channel_router.register(r'', ChannelView)
urlpatterns = channel_router.urls
