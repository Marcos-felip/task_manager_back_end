import uuid
from accounts.domain.entities.organization import Organization
from accounts.domain.repositories.organization_repository import OrganizationRepository
from accounts.infrastructure.models.organization import Organization as OrganizationModel


class OrganizationRepositoryDjango(OrganizationRepository):
    def get_by_id(self, organization_id: uuid.UUID) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization_id)
        return Organization(
            organization_id=str(obj.organization_id),
            name=obj.name,
            email=obj.email,
            cpf_cnpj=obj.cpf,
            is_active=obj.is_active,
        )

    def create(self, *, name: str) -> Organization:
        obj = OrganizationModel.objects.create(name=name)
        return Organization(
            organization_id=str(obj.organization_id),
            name=obj.name,
            email=obj.email,
            cpf_cnpj=obj.cpf,
            is_active=obj.is_active,
        )

    def save(self, organization: Organization) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization.organization_id)
        obj.name = organization.name
        obj.email = organization.email
        obj.cpf = organization.cpf_cnpj
        obj.is_active = organization.is_active
        obj.save()
        return organization
