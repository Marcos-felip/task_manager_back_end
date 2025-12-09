from django.urls import path
from apps.authentication.presentation.views import (
    RegisterView,
    CreateOrganizationMembershipView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('create-org/', CreateOrganizationMembershipView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]