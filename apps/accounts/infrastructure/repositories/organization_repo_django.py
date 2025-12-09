from accounts.domain.entities.organization import Organization
from accounts.domain.repositories.organization_repository import OrganizationRepository
from accounts.infrastructure.models.organization import Organization as OrganizationModel


class OrganizationRepositoryDjango(OrganizationRepository):
    
    def get_organization_by_id(self, organization_id: int) -> Organization:
        return self.get_by_id(organization_id)

    def get_by_id(self, organization_id: int) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization_id)
        
        return Organization(
            organization_id=obj.organization_id,
            name=obj.name,
            email=obj.email,
            cpf_cnpj=obj.cpf_cnpj,
            is_active=obj.is_active,
        )
    
    def save(self, organization: Organization) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization.organization_id)
        obj.name = organization.name
        obj.email = organization.email
        obj.cpf_cnpj = organization.cpf_cnpj
        obj.is_active = organization.is_active
        obj.save()
        return organization
