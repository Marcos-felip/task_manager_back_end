from accounts.domain.entities.organization import Organization
from accounts.domain.repositories.organization_repository import OrganizationRepository
from accounts.infrastructure.models.organization import Organization as OrganizationModel


class OrganizationRepositoryDjango(OrganizationRepository):
    
    def get_by_id(self, organization_id: int) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization_id)
        
        return Organization(
            organization_id=obj.organization_id,
            name=obj.name,
            domain=obj.domain,
        )
    
    def save(self, organization: Organization) -> Organization:
        obj = OrganizationModel.objects.get(pk=organization.organization_id)
        obj.name = organization.name
        obj.domain = organization.domain
        obj.save()
        return organization
