"""
Authentication Controller - Coordinates authentication between UI and use cases
"""
from typing import Tuple, Optional
from ...domain.use_cases.authenticate_user import AuthenticateUser, ChangePassword
from ...domain.entities.user import User


class AuthController:
    """Controller for authentication operations"""

    def __init__(
        self,
        authenticate_use_case: AuthenticateUser,
        change_password_use_case: ChangePassword
    ):
        """
        Initialize authentication controller

        Args:
            authenticate_use_case: Use case for authentication
            change_password_use_case: Use case for changing password
        """
        self.authenticate_use_case = authenticate_use_case
        self.change_password_use_case = change_password_use_case

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Password

        Returns:
            Tuple of (success, user, message)
        """
        return self.authenticate_use_case.execute(username, password)

    def change_password(
        self,
        username: str,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password

        Args:
            username: Username
            current_password: Current password
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        return self.change_password_use_case.execute(
            username,
            current_password,
            new_password
        )
