# lambda-auth/src/application/register_use_case.py
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Protocol

from ..domain.entities import User
from ..domain.exceptions import UserAlreadyExistsError
from ..domain.ports import UserRepository

logger = logging.getLogger(__name__)


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


@dataclass
class RegisterResult:
    user_id: str
    username: str


class RegisterUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, username: str, password: str) -> RegisterResult:
        username = username.strip().lower()

        # Verificar que no exista
        existing = self._user_repo.find_by_username(username)
        if existing is not None:
            raise UserAlreadyExistsError(f"El usuario '{username}' ya existe")

        password_hash = self._password_hasher.hash(password)

        user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            password_hash=password_hash,
            active=True,
        )

        created = self._user_repo.create(user)

        logger.info(
            "register_success",
            extra={"user_id": created.user_id[:8] + "..."},
        )

        return RegisterResult(
            user_id=created.user_id,
            username=created.username,
        )
