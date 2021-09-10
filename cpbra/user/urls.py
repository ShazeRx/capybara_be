from rest_framework import routers

from cpbra.user.views import UserView

channel_router = routers.SimpleRouter()
channel_router.register(r'', UserView, basename='users')
urlpatterns = channel_router.urls
