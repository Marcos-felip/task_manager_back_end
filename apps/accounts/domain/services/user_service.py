import logging
import uuid
from django.db import IntegrityError
from typing import Dict

from accounts.domain.interfaces.organization_interface import get_organization
from accounts.domain.repositories.user_repository import UserRepository
from accounts.infrastructure.repositories.user_repo_django import UserRepositoryDjango
from accounts.domain.entities.user import UserEntity
from accounts.domain.repositories.organization_repository import OrganizationRepository
from accounts.domain.repositories.membership_repository import MembershipRepository
from accounts.infrastructure.repositories.organization_repo_django import OrganizationRepositoryDjango
from accounts.infrastructure.repositories.membership_repo_django import MembershipRepoDjango
from accounts.domain.entities.role import Role

logger = logging.getLogger(__name__)


def create_user(
    *,
    user_name: str,
    user_email: str,
    password: str,
    user_repo: UserRepository | None = None,
) -> Dict:
    logger.info("Criando usuário")
    user_repo = user_repo or UserRepositoryDjango()
    user_entity = UserEntity(id=None, email=user_email, org_active_id=None, org_list_ids=[])
    try:
        user = user_repo.create_user(user_entity, password=password)
    except IntegrityError:
        raise ValueError("Email já cadastrado")
    return {"user": {"id": str(user.id), "name": user_name, "email": user.email}}


def create_organization_with_membership_and_link_user(
    *,
    organization_name: str,
    user_id: str,
    role: str,
    org_repo: OrganizationRepository | None = None,
    membership_repo: MembershipRepository | None = None,
    user_repo: UserRepository | None = None,
) -> Dict:
    logger.info("Criando organização e membership e vinculando ao usuário")
    org_repo = org_repo or OrganizationRepositoryDjango()
    membership_repo = membership_repo or MembershipRepoDjango()
    user_repo = user_repo or UserRepositoryDjango()

    organization = org_repo.create(name=organization_name)
    user = user_repo.get_user_by_id(user_id)

    org_id = getattr(organization, "organization_id", None)
    org_uuid = uuid.UUID(org_id) if isinstance(org_id, str) else org_id

    membership = membership_repo.create(user_id=user.id, organization_id=org_uuid, role=Role.MANAGER.value)

    user.org_active_id = org_uuid
    orgs = list(getattr(user, "org_list_ids", []) or [])

    if org_uuid not in orgs:
        orgs.append(org_uuid)

    user.org_list_ids = orgs
    user_repo.update_user(user)

    org_data = get_organization(id=org_uuid, repo=org_repo)

    return {
        "organization": org_data,
        "membership": {"id": str(getattr(membership, "member_id", membership)), "role": membership.role},
        "user": {
            "id": str(user.id),
            "name": getattr(user, "username", None),
            "email": user.email,
            "org_active_id": str(user.org_active_id) if user.org_active_id else None,
            "org_list_ids": [str(x) for x in (user.org_list_ids or [])],
        },
    }
