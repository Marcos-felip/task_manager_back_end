from dataclasses import dataclass, field
from typing import Optional, List

from accounts.infrastructure.models.organization import Organization


@dataclass
class User:
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    org_active: Optional[Organization] = None
    org_list: List[Organization] = field(default_factory=list)
    user_id: Optional[str] = None
