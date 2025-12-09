from django.db import models
import uuid


class Organization(models.Model):
    class Meta:
        app_label = 'accounts'
        verbose_name = u"Organização"
        verbose_name_plural = u"Organizações"
        
    organization_id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name=u'Chave da Organização')
    is_active = models.BooleanField(verbose_name=u'ativo', default=True,help_text='Conta Ativa',db_index=True)
    name = models.CharField(max_length=50, verbose_name=u'nome da organização')
    email = models.EmailField(verbose_name=u'E-mail', null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=50, verbose_name=u'CNPJ/CPF')
    
    def __str__(self):
        return self.name