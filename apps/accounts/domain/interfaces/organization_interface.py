import uuid
from typing import Dict, Optional

from accounts.domain.repositories.organization_repository import OrganizationRepository
from accounts.infrastructure.repositories.organization_repo_django import OrganizationRepositoryDjango


def get_organization(*, id: uuid.UUID, repo: Optional[OrganizationRepository] = None) -> Dict:
    repository = repo or OrganizationRepositoryDjango()
    org = repository.get_by_id(id)
    return {
        "id": str(org.organization_id),
        "name": org.name,
    }
