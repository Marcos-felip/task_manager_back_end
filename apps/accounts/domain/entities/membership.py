from dataclasses import dataclass
from typing import Optional

from accounts.infrastructure.models.user import User
from accounts.infrastructure.models.organization import Organization

@dataclass
class Membership:
    user: User
    organization: Organization
    role: str
    is_active: bool = True
    membership_id: Optional[str] = None
