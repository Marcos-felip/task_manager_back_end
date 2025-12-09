from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from accounts.infrastructure.models.organization import Organization


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name=u'Chave de Usuário')
    email = models.EmailField(unique=True, verbose_name=u'E-mail')
    username = models.CharField(blank=True, null=True,max_length=100, verbose_name=u'Nome de Usuário')
    org_active = models.ForeignKey(Organization, verbose_name=u'organização ativa', blank=True, null=True, on_delete=models.CASCADE, related_name="organization")
    org_list = models.ManyToManyField(Organization, verbose_name=u'organização', blank=True, through='Membership')
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        app_label = 'accounts'
    
    
class Membership(models.Model):

    class Roles(models.TextChoices):
        MANAGER = 'manager', 'Administrador do Sistema'
        OWNER = 'owner', 'Conta Principal'
        MEMBER = 'member', 'Membro'
    
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name=u'Chave de Associação')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.MEMBER)
    is_active = models.BooleanField(verbose_name=u'É um mebro ativo', default=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        app_label = 'accounts'
