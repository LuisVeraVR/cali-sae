"""
Authenticate User Use Case
"""
from typing import Optional, Tuple
from datetime import datetime
from ..entities.user import User
from ..repositories.user_repository import UserRepositoryInterface


class AuthenticateUser:
    """Use case for user authentication"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    def execute(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user with username and password

        Args:
            username: The username
            password: The plain text password

        Returns:
            Tuple of (success, user, message)
        """
        # Validate input
        if not username or not password:
            return False, None, "Usuario y contraseña son requeridos"

        # Get user from repository
        user = self.user_repository.get_by_username(username)

        if user is None:
            return False, None, "Usuario no encontrado"

        # Verify password
        if not user.verify_password(password):
            return False, None, "Contraseña incorrecta"

        # Update last login
        self.user_repository.update_last_login(username)

        return True, user, "Autenticación exitosa"


class ChangePassword:
    """Use case for changing user password"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    def execute(
        self,
        username: str,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password

        Args:
            username: The username
            current_password: The current password
            new_password: The new password

        Returns:
            Tuple of (success, message)
        """
        # Validate input
        if not username or not current_password or not new_password:
            return False, "Todos los campos son requeridos"

        if len(new_password) < 6:
            return False, "La nueva contraseña debe tener al menos 6 caracteres"

        # Get user
        user = self.user_repository.get_by_username(username)

        if user is None:
            return False, "Usuario no encontrado"

        # Verify current password
        if not user.verify_password(current_password):
            return False, "Contraseña actual incorrecta"

        # Hash and update new password
        new_password_hash = User.hash_password(new_password)
        success = self.user_repository.update_password(username, new_password_hash)

        if success:
            return True, "Contraseña actualizada exitosamente"
        else:
            return False, "Error al actualizar la contraseña"
