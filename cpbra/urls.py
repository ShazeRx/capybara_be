from django.urls import include, path

urlpatterns = [
    path('auth/', include('cpbra.auth.urls')),
    path('channels/', include('cpbra.chat.urls')),

]