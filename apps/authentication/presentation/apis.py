import logging
from typing import Dict

from accounts.domain.services.user_service import (
    create_user,
    create_organization_with_membership_and_link_user,
)

logger = logging.getLogger(__name__)


class AuthAPI:
    @staticmethod
    def register_create_user(*, user_name: str, user_email: str, password: str) -> Dict:
        logger.info('API criar_usuario chamada')
        return create_user(user_name=user_name, user_email=user_email, password=password)

    @staticmethod
    def register_create_org_membership_link_user(
        *, organization_name: str, user_id: str, role: str
    ) -> Dict:
        logger.info('API criar_organizacao_e_membership_vincular_usuario chamada')
        return create_organization_with_membership_and_link_user(
            organization_name=organization_name,
            user_id=user_id,
            role=role,
        )
