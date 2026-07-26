# lambda-auth/src/domain/ports.py
from __future__ import annotations

from typing import Optional, Protocol

from .entities import User


class UserRepository(Protocol):
    def find_by_username(self, username: str) -> Optional[User]:
        """Devuelve el usuario o None si no existe."""
        ...

    def find_by_id(self, user_id: str) -> Optional[User]:
        """Devuelve el usuario o None si no existe."""
        ...
    def create(self, user: User) -> User:
        """Devuelve el usuario creado."""
        ...
