from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationMemberViewSet

router = DefaultRouter()
router.register(r'members', OrganizationMemberViewSet, basename='organization-members')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
]