from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserEntity:
    id: UUID
    email: str
    org_active_id: UUID | None
    org_list_ids: list[UUID]
