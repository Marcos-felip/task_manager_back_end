from dataclasses import dataclass
from typing import Optional, List
from dataclasses import field

from accounts.infrastructure.models.organization import Organization


@dataclass
class User:
    user_id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    org_active: Optional[Organization] = None
    org_list: List[Organization] = field(default_factory=list)
