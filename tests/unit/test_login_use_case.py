# lambda-auth/tests/unit/test_login_use_case.py
from __future__ import annotations

import pytest

from src.application.login_use_case import LoginUseCase
from src.domain.exceptions import InvalidCredentialsError, UserInactiveError, UserNotFoundError


def make_use_case(user_repo, password_verifier, token_service):
    return LoginUseCase(user_repo, password_verifier, token_service)


class TestLoginCorrecto:
    def test_devuelve_token_con_bearer_type(self, active_user, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = active_user
        mock_password_verifier.verify.return_value = True
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        result = uc.execute("testuser", "correcta")

        assert result.access_token == "test.jwt.token"
        assert result.token_type == "Bearer"
        assert result.expires_in == 900

    def test_normaliza_username_a_minusculas(self, active_user, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = active_user
        mock_password_verifier.verify.return_value = True
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        uc.execute("TestUser", "correcta")

        mock_user_repo.find_by_username.assert_called_once_with("testuser")


class TestUsuarioInexistente:
    def test_lanza_user_not_found(self, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = None
        mock_password_verifier.verify.return_value = False  # dummy hash
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        with pytest.raises(UserNotFoundError):
            uc.execute("noexiste", "cualquiera")

    def test_ejecuta_hash_dummy_para_evitar_timing_oracle(self, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = None
        mock_password_verifier.verify.return_value = False
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        try:
            uc.execute("noexiste", "x")
        except UserNotFoundError:
            pass

        # Debe ejecutar verify aunque el usuario no exista
        mock_password_verifier.verify.assert_called_once()


class TestContraseñaInvalida:
    def test_lanza_invalid_credentials(self, active_user, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = active_user
        mock_password_verifier.verify.return_value = False
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        with pytest.raises(InvalidCredentialsError):
            uc.execute("testuser", "incorrecta")


class TestUsuarioInactivo:
    def test_lanza_user_inactive_despues_de_verificar_hash(self, inactive_user, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = inactive_user
        mock_password_verifier.verify.return_value = True
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        with pytest.raises(UserInactiveError):
            uc.execute("testuser", "correcta")


class TestRespuestasNoPermiteEnumeracion:
    """UserNotFoundError e InvalidCredentialsError se mapean igual en HTTP (401)."""

    def test_usuario_inexistente_no_revela_informacion(self, mock_user_repo, mock_password_verifier, mock_token_service):
        mock_user_repo.find_by_username.return_value = None
        mock_password_verifier.verify.return_value = False
        uc = make_use_case(mock_user_repo, mock_password_verifier, mock_token_service)

        with pytest.raises((UserNotFoundError, InvalidCredentialsError)):
            uc.execute("noexiste", "pwd")