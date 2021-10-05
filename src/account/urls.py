from django.urls import path, include
from rest_framework import routers
from .views import AuthRegister, AuthInfoGetView

urlpatterns = [
    path('register/', AuthRegister.as_view(), name='register'),
    path('mypage/', AuthInfoGetView.as_view(), name='mypage'),
]
