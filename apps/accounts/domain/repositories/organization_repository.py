from abc import ABC, abstractmethod
import uuid
from accounts.domain.entities.organization import Organization


class OrganizationRepository(ABC):
    @abstractmethod
    def get_by_id(self, organization_id: uuid.UUID) -> Organization:
        pass

    @abstractmethod
    def create(self, *, name: str) -> Organization:
        pass
