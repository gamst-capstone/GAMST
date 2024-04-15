from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,

)
from . import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    # path('login/', TokenObtainPairView.as_view(), name='user_login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', views.UserList.as_view(), name='user_list'),
]