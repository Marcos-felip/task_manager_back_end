import uuid
from typing import Optional

from accounts.infrastructure.models.membership import Membership as MembershipModel


class MembershipRepoDjango:
    def create(self, *, user_id: uuid.UUID, organization_id: uuid.UUID, role: str) -> MembershipModel:
        return MembershipModel.objects.create(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )
