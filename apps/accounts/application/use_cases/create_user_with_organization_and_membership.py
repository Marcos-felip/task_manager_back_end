from accounts.domain.services.user_organization_membership_service import UserOrganizationMembershipService


class CreateUserWithOrganizationAndMembershipUseCase:
    def __init__(self, user_repo, org_repo):
        self.service = UserOrganizationMembershipService(user_repo, org_repo)

    def execute(self, user_data, organization_id, membership_data=None):
        return self.service.create_user_and_membership(user_data, organization_id, membership_data or {})
