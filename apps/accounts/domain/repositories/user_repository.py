from abc import ABC, abstractmethod
from typing import Optional

from accounts.domain.entities.user import UserEntity as User


class UserRepository(ABC):
    def get_all_users(self) -> list[User]:
        pass
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass
    
    def save(self, user: User) -> User:
        existing_user = self.get_user_by_id(user.id)
        if existing_user:
            return self.update_user(user)
        else:
            return self.create_user(user)