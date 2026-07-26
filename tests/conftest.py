# lambda-auth/tests/conftest.py
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from src.domain.entities import User


@pytest.fixture
def active_user() -> User:
    return User(
        user_id=str(uuid.uuid4()),
        username="testuser",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$fakesalt$fakehash",
        active=True,
    )


@pytest.fixture
def inactive_user(active_user: User) -> User:
    return User(
        user_id=active_user.user_id,
        username=active_user.username,
        password_hash=active_user.password_hash,
        active=False,
    )


@pytest.fixture
def mock_user_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_password_verifier() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_token_service() -> MagicMock:
    svc = MagicMock()
    svc.generate.return_value = ("test.jwt.token", 900)
    return svc