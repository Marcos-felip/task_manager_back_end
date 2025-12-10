from apps.accounts.domain.services.user_service import (
    create_user_with_organization_and_membership,
)


class CreateUserWithOrganizationAndMembershipUseCase:
    def execute(self, *, user_name: str, user_email: str, organization_name: str, role: str):
        return create_user_with_organization_and_membership(
            user_name=user_name,
            user_email=user_email,
            organization_name=organization_name,
            role=role,
        )
