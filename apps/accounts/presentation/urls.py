from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.user_viewset import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
]