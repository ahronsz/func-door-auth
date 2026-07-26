# lambda-auth/src/domain/exceptions.py
from __future__ import annotations


class DomainException(Exception):
    """Base para excepciones de dominio."""


class InvalidCredentialsError(DomainException):
    """Credenciales inválidas. Mensaje genérico intencional."""


class UserInactiveError(DomainException):
    """El usuario existe pero está desactivado."""


class UserNotFoundError(DomainException):
    """El usuario no existe. Se mapea igual que InvalidCredentials."""

class UserAlreadyExistsError(DomainException):
    """El usuario ya existe."""
