from django.db import models
import uuid



class MembershipRole(models.TextChoices):
    ADMIN = "admin", "Administrador"
    MANAGER = "manager", "Gestor"
    MEMBER = "member", "Membro"

class Membership(models.Model):
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    organization_id = models.UUIDField()
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return f"Membership {str(self.member_id)[:8]} ({self.get_role_display()})"
