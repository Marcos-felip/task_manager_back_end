from dataclasses import dataclass

from accounts.infrastructure.models.user import User
from accounts.infrastructure.models.organization import Organization

@dataclass
class Membership:
    membership_id: str
    user: User
    organization: Organization
    role: str
    is_active: bool = True
