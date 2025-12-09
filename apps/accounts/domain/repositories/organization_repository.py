from abc import ABC, abstractmethod
from accounts.domain.entities.organization import Organization


class OrganizationRepository(ABC):
    @abstractmethod
    def get_organization_by_id(self, organization_id: int) -> Organization:
        pass
