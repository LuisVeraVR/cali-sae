"""
User Repository Interface - Defines the contract for user persistence
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user import User


class UserRepositoryInterface(ABC):
    """Abstract interface for user repository"""

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    def update_password(self, username: str, new_password_hash: str) -> bool:
        """Update user password"""
        pass

    @abstractmethod
    def update_last_login(self, username: str) -> bool:
        """Update last login timestamp"""
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        """Get all users"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user by ID"""
        pass

    @abstractmethod
    def exists(self, username: str) -> bool:
        """Check if a user exists"""
        pass
