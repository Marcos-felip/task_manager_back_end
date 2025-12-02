from django.urls import path
from .views import RegisterView, CreateOrganizationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('create-organization/', CreateOrganizationView.as_view(), name='create_organization'),
]