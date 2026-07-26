# lambda-auth/src/application/login_use_case.py
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Protocol

from ..domain.exceptions import InvalidCredentialsError, UserInactiveError, UserNotFoundError
from ..domain.ports import UserRepository

logger = logging.getLogger(__name__)

# Delay mínimo para mitigar timing attacks y fuerza bruta superficial.
# LIMITACIÓN: Function URL sin WAF no limita peticiones por IP a nivel de
# infraestructura. Para volúmenes de producción, migrar a API Gateway + WAF
# o Cognito.
_MIN_RESPONSE_SECONDS = 0.3


class PasswordVerifier(Protocol):
    def verify(self, hash_: str, password: str) -> bool: ...


class TokenService(Protocol):
    def generate(self, user_id: str) -> tuple[str, int]:
        """Devuelve (token, expires_in_seconds)."""
        ...


@dataclass
class LoginResult:
    access_token: str
    token_type: str
    expires_in: int


class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        password_verifier: PasswordVerifier,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._password_verifier = password_verifier
        self._token_service = token_service

    def execute(self, username: str, password: str) -> LoginResult:
        start = time.monotonic()
        try:
            return self._do_login(username, password)
        finally:
            elapsed = time.monotonic() - start
            remaining = _MIN_RESPONSE_SECONDS - elapsed
            if remaining > 0:
                time.sleep(remaining)

    def _do_login(self, username: str, password: str) -> LoginResult:
        user = self._user_repo.find_by_username(username.strip().lower())

        if user is None:
            # Ejecutar hash dummy para evitar timing oracle en usuarios inexistentes
            self._password_verifier.verify(
                "$argon2id$v=19$m=65536,t=3,p=4$dummysaltdummysalt$dummyhash", "x"
            )
            raise UserNotFoundError()

        if not self._password_verifier.verify(user.password_hash, password):
            raise InvalidCredentialsError()

        if not user.active:
            raise UserInactiveError()

        token, expires_in = self._token_service.generate(user.user_id)

        logger.info(
            "login_success",
            extra={"user_id": user.user_id[:8] + "...", "expires_in": expires_in},
        )

        return LoginResult(
            access_token=token,
            token_type="Bearer",
            expires_in=expires_in,
        )