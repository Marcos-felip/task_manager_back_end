from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from hashid_field import HashidAutoField
import uuid


class Organization(models.Model):
    class Meta:
        verbose_name = u"Organização"
        verbose_name_plural = u"Organizações"

    is_active = models.BooleanField(verbose_name=u'ativo', default=True,help_text='Conta Ativa',db_index=True)
    name = models.CharField(max_length=50, verbose_name=u'nome da organização')
    email = models.EmailField(verbose_name=u'E-mail', null=True, blank=True)
    organization_id = models.CharField(max_length=50, verbose_name=u'CNPJ/CPF')
    key = models.CharField(max_length=100, unique=True, verbose_name=u'Chave da Organização', blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())
        super().save(*args, **kwargs)

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name=u'E-mail')
    username = models.CharField(blank=True, null=True,max_length=100, verbose_name=u'Nome de Usuário')
    org_active = models.ForeignKey(Organization, verbose_name=u'organização ativa', blank=True, null=True, on_delete=models.CASCADE, related_name="organization")
    org_list = models.ManyToManyField(Organization, verbose_name=u'organização', blank=True, through='Membership')
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    user_id = models.CharField(max_length=100, unique=True, verbose_name=u'Chave de Usuário', blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def user_display_name(self):
        return f'{self.first_name} {self.last_name}'


class Membership(models.Model):

    class Roles(models.TextChoices):
        MANAGER = 'manager', 'Administrador do Sistema'
        OWNER = 'owner', 'Conta Principal'
        MEMBER = 'member', 'Membro'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.MEMBER)
    is_active = models.BooleanField(verbose_name=u'É um mebro ativo', default=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    key = models.CharField(max_length=100, unique=True, verbose_name=u'Chave de Associação', blank=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f'{self.user.email} - {self.organization.name}'
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())
        super().save(*args, **kwargs)