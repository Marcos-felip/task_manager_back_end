import uuid
from typing import Optional

from accounts.infrastructure.repositories.membership_repo_django import MembershipRepoDjango
from accounts.infrastructure.models.membership import Membership as MembershipModel


class MembershipRepository:
    def __init__(self, backend: Optional[MembershipRepoDjango] = None) -> None:
        self.backend = backend or MembershipRepoDjango()

    def create(self, *, user_id: uuid.UUID, organization_id: uuid.UUID, role: str) -> MembershipModel:
        return self.backend.create(user_id=user_id, organization_id=organization_id, role=role)
