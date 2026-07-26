# lambda-auth/src/infrastructure/password_service.py
from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_ph = PasswordHasher()


class Argon2PasswordVerifier:
    """Verifica contraseñas usando Argon2id (argon2-cffi)."""

    def verify(self, hash_: str, password: str) -> bool:
        try:
            return _ph.verify(hash_, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

class Argon2PasswordHasher:
    def hash(self, password: str) -> str:
        return _ph.hash(password)


def hash_password(password: str) -> str:
    """Genera un hash Argon2id. Solo para uso en scripts administrativos."""
    return _ph.hash(password)
