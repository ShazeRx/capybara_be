"""
Urls for authentication
"""
from django.urls import path
from rest_framework_simplejwt import views as jwt_views


from auth.views import VerifyEmailView,RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(),name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='toke_refresh'),
    path('email-verify/', VerifyEmailView.as_view(), name='email-verify'),
]