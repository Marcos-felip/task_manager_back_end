from accounts.domain.entities.user import User
from accounts.domain.repositories.user_repository import UserRepository
from accounts.infrastructure.models.user import User as UserModel


class UserRepositoryDjango(UserRepository):

    def get_all_users(self) -> list[User]:
        objs = UserModel.objects.select_related("org_active").prefetch_related("org_list").all()
        users: list[User] = []
        for obj in objs:
            users.append(
                User(
                    user_id=int(obj.user_id),
                    email=obj.email,
                    username=obj.username,
                    org_active=obj.org_active,
                    org_list=list(obj.org_list.all()),
                )
            )
        return users

    def get_user_by_id(self, user_id: int) -> User | None:
        try:
            obj = UserModel.objects.select_related("org_active").get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return User(
            user_id=int(obj.user_id),
            email=obj.email,
            username=obj.username,
            org_active=obj.org_active,
            org_list=list(obj.org_list.all()),
        )

    def create_user(self, user: User) -> User:
        obj = UserModel.objects.create(
            email=user.email,
            username=user.username,
        )
        return User(
            user_id=int(obj.user_id),
            email=obj.email,
            username=obj.username,
            org_active=obj.org_active,
            org_list=list(obj.org_list.all()),
        )

    def update_user(self, user: User) -> User:
        obj = UserModel.objects.get(pk=user.user_id)
        obj.email = user.email
        obj.username = user.username
        if getattr(user, 'org_active', None):
            obj.org_active_id = user.org_active.organization_id
        obj.save()

        if getattr(user, 'org_list', None):
            obj.org_list.set([o.organization_id for o in user.org_list])

        return User(
            user_id=int(obj.user_id),
            email=obj.email,
            username=obj.username,
            org_active=obj.org_active,
            org_list=list(obj.org_list.all()),
        )

    def delete_user(self, user_id: int) -> None:
        UserModel.objects.filter(pk=user_id).delete()
