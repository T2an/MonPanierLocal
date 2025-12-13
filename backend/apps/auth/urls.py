from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register, me, change_password, CustomTokenObtainPairView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', me, name='me'),
    path('change-password/', change_password, name='change_password'),
]

