"""
SQLite implementation of User Repository
"""
import sqlite3
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepositoryInterface


class SQLiteUserRepository(UserRepositoryInterface):
    """SQLite implementation of user repository"""

    def __init__(self, db_path: str = "facturas_users.db"):
        """
        Initialize the repository

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            conn.commit()

            # Create default users if not exist
            self._create_default_users(cursor)
            conn.commit()

    def _create_default_users(self, cursor):
        """Create default admin and operator users"""
        default_users = [
            ('admin', User.hash_password('admin123'), 'admin'),
            ('operador', User.hash_password('FacturasElectronicas2024'), 'operator')
        ]

        for username, password_hash, user_type in default_users:
            cursor.execute(
                'SELECT COUNT(*) FROM users WHERE username = ?',
                (username,)
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    'INSERT INTO users (username, password_hash, user_type) VALUES (?, ?, ?)',
                    (username, password_hash, user_type)
                )

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()

            if row:
                return self._row_to_user(row)
            return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return self._row_to_user(row)
            return None

    def create(self, user: User) -> User:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, password_hash, user_type, created_at, last_login)
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    user.username,
                    user.password_hash,
                    user.user_type,
                    user.created_at,
                    user.last_login
                )
            )
            conn.commit()
            user.id = cursor.lastrowid
            return user

    def update(self, user: User) -> User:
        """Update an existing user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE users
                   SET username = ?, password_hash = ?, user_type = ?, last_login = ?
                   WHERE id = ?''',
                (
                    user.username,
                    user.password_hash,
                    user.user_type,
                    user.last_login,
                    user.id
                )
            )
            conn.commit()
            return user

    def update_password(self, username: str, new_password_hash: str) -> bool:
        """Update user password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET password_hash = ? WHERE username = ?',
                    (new_password_hash, username)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def update_last_login(self, username: str) -> bool:
        """Update last login timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET last_login = ? WHERE username = ?',
                    (datetime.now(), username)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def get_all(self) -> List[User]:
        """Get all users"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]

    def delete(self, user_id: int) -> bool:
        """Delete a user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def exists(self, username: str) -> bool:
        """Check if a user exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM users WHERE username = ?',
                (username,)
            )
            return cursor.fetchone()[0] > 0

    def _row_to_user(self, row) -> User:
        """Convert a database row to a User entity"""
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            user_type=row['user_type'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None
        )
