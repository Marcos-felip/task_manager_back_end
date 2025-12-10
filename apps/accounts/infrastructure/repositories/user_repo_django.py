from accounts.domain.entities.user import UserEntity as User
from accounts.domain.repositories.user_repository import UserRepository
from accounts.infrastructure.models.user import User as UserModel


class UserRepositoryDjango(UserRepository):

    def get_all_users(self) -> list[User]:
        objs = UserModel.objects.all()
        users: list[User] = []
        for obj in objs:
            users.append(
                User(
                    id=obj.user_id,
                    email=obj.email,
                    org_active_id=getattr(obj, "org_active_id", None),
                    org_list_ids=getattr(obj, "org_list_ids", []),
                )
            )
        return users

    def get_user_by_id(self, user_id) -> User | None:
        try:
            obj = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return User(id=obj.user_id, email=obj.email, org_active_id=getattr(obj, "org_active_id", None), org_list_ids=getattr(obj, "org_list_ids", []))

    def create_user(self, user: User, password: str | None = None) -> User:
        obj = UserModel.objects.create(
            email=user.email,
            username=getattr(user, "username", None),
        )
        if password:
            obj.set_password(password)
            obj.save()
        return User(id=obj.user_id, email=obj.email, org_active_id=getattr(obj, "org_active_id", None), org_list_ids=getattr(obj, "org_list_ids", []))

    def update_user(self, user: User) -> User:
        obj = UserModel.objects.get(pk=user.id)
        obj.email = user.email
        obj.username = getattr(user, "username", None)
        if getattr(user, 'org_active_id', None):
            obj.org_active_id = user.org_active_id
        if getattr(user, 'org_list_ids', None) is not None:
            obj.org_list_ids = [str(x) for x in (user.org_list_ids or [])]
        obj.save()

        return User(
            id=obj.user_id,
            email=obj.email,
            org_active_id=getattr(obj, "org_active_id", None),
            org_list_ids=getattr(obj, "org_list_ids", [])
        )

    def delete_user(self, user_id: int) -> None:
        UserModel.objects.filter(pk=user_id).delete()
