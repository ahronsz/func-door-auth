# lambda-auth/src/infrastructure/jwt_service.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import jwt as pyjwt

from ..config.settings import Settings

# Algoritmo fijo — no se acepta ningún otro, incluyendo "none"
_ALLOWED_ALGORITHM = "HS256"


class JWTService:
    def __init__(self, settings: Settings) -> None:
        if settings.jwt_algorithm != _ALLOWED_ALGORITHM:
            raise ValueError(
                f"Algoritmo JWT no permitido: {settings.jwt_algorithm}. "
                f"Solo se acepta {_ALLOWED_ALGORITHM}."
            )
        self._secret = settings.jwt_secret
        self._algorithm = _ALLOWED_ALGORITHM
        self._issuer = settings.jwt_issuer
        self._expiry = settings.jwt_expiry_seconds

    def generate(self, user_id: str) -> tuple[str, int]:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": user_id,
            "iss": self._issuer,
            "iat": now,
            "exp": now.timestamp() + self._expiry,
            "jti": str(uuid.uuid4()),
        }
        token: str = pyjwt.encode(payload, self._secret, algorithm=self._algorithm)
        return token, self._expiry