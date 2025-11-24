"""
User entity - Represents a user in the system
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class User:
    """User entity with authentication and authorization"""

    id: Optional[int]
    username: str
    password_hash: str
    user_type: str  # 'admin' or 'operator'
    created_at: datetime
    last_login: Optional[datetime] = None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash"""
        return self.password_hash == self.hash_password(password)

    def is_admin(self) -> bool:
        """Check if the user has admin privileges"""
        return self.user_type == 'admin'

    def is_operator(self) -> bool:
        """Check if the user is an operator"""
        return self.user_type == 'operator'

    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', type='{self.user_type}')"
