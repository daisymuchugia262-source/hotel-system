from __future__ import annotations
import hashlib
import hmac
import os
from typing import Optional
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, DuplicateError
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: Optional[UserRepository] = None) -> None:
        self.user_repo = user_repo or UserRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return f"{salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        try:
            salt_hex, digest_hex = stored.split("$")
        except ValueError:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return hmac.compare_digest(actual, expected)

    def register(self, username: str, email: str, password: str,
                 role: UserRole = UserRole.WAITER) -> User:
        if self.user_repo.find_by_username(username):
            raise DuplicateError(f"Username '{username}' is taken")
        if self.user_repo.find_by_email(email):
            raise DuplicateError(f"Email '{email}' is already registered")
        user = User(username=username, email=email,
                    password_hash=self.hash_password(password), role=role)
        return self.user_repo.create(user)

    def login(self, username: str, password: str) -> User:
        user = self.user_repo.find_by_username(username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid credentials")
        if not self.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        return user
