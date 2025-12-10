from django.db import models
import uuid


class Organization(models.Model):
    organization_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    cpf = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'accounts'
