# lambda-auth/src/domain/entities.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: str          # UUID
    username: str
    password: str    # Argon2id hash — nunca exponer
    active: bool
