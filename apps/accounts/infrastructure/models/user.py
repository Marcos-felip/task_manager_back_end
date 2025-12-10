from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)

    org_active_id = models.UUIDField(null=True, blank=True)
    org_list_ids = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        app_label = 'accounts'

    @property
    def full_name(self) -> str:
        first = self.first_name or ""
        last = self.last_name or ""
        return (first + " " + last).strip()
    
