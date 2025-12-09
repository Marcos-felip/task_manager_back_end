from accounts.domain.entities.user import User
from accounts.domain.entities.organization import Organization
from accounts.domain.entities.membership import Membership


class UserOrganizationMembershipService:
    def __init__(self, user_repo, org_repo):
        self.user_repo = user_repo
        self.org_repo = org_repo
        
    def create_user_and_membership(self, user_data, organization_id, membership_data):
        user = None
        if user_data and user_data.get('user_id'):
            user = self.user_repo.get_user_by_id(int(user_data['user_id']))
        if not user:
            user = User(**{k: v for k, v in user_data.items() if k != 'user_id'})
            user = self.user_repo.create_user(user)
        
        organization = self.org_repo.get_organization_by_id(organization_id)
        
        membership = Membership(
            user=user,
            organization=organization,
            **membership_data
        )

        user.org_active = organization
        if hasattr(user, 'org_list'):
            if organization not in getattr(user, 'org_list'):
                user.org_list.append(organization)

        user = self.user_repo.update_user(user) if hasattr(self.user_repo, 'update_user') else self.user_repo.save(user)

        return user, organization, membership