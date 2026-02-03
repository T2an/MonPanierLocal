"""Tests unitaires API Auth."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAuthLogin:
    """Tests endpoint /api/auth/login/."""

    def test_login_success(self, api_client, user):
        """Connexion réussie avec email/password (USERNAME_FIELD=email)."""
        response = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, user):
        """Connexion échouée : mauvais mot de passe."""
        response = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "WrongPass123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_unknown_user(self, api_client):
        """Connexion échouée : utilisateur inconnu."""
        response = api_client.post(
            "/api/auth/login/",
            {"email": "unknown@example.com", "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, api_client):
        """Connexion échouée : champs manquants."""
        response = api_client.post("/api/auth/login/", {}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuthRegister:
    """Tests endpoint /api/auth/register/."""

    def test_register_success(self, api_client):
        """Inscription réussie."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPass123!",
            "password_confirm": "NewPass123!",
            "is_producer": False,
        }
        response = api_client.post("/api/auth/register/", data, format="json")
        assert response.status_code == 201
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_register_email_exists(self, api_client, user):
        """Inscription échouée : email déjà utilisé."""
        data = {
            "email": user.email,
            "username": "otheruser",
            "password": "Pass123!",
            "password_confirm": "Pass123!",
        }
        response = api_client.post("/api/auth/register/", data, format="json")
        assert response.status_code == 400
        assert "email" in response.data

    def test_register_password_mismatch(self, api_client):
        """Inscription échouée : mots de passe différents."""
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "Pass123!",
            "password_confirm": "DifferentPass123!",
        }
        response = api_client.post("/api/auth/register/", data, format="json")
        assert response.status_code == 400

    def test_register_short_password(self, api_client):
        """Inscription échouée : mot de passe trop court."""
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "Short1!",
            "password_confirm": "Short1!",
        }
        response = api_client.post("/api/auth/register/", data, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuthMe:
    """Tests endpoint /api/auth/me/."""

    def test_me_authenticated(self, auth_client, user):
        """Récupération du profil connecté."""
        response = auth_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_me_unauthenticated(self, api_client):
        """Accès refusé sans token."""
        response = api_client.get("/api/auth/me/")
        assert response.status_code == 401

    def test_me_patch(self, auth_client, user):
        """Modification du profil."""
        response = auth_client.patch(
            "/api/auth/me/",
            {"username": "updated_username"},
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.username == "updated_username"


@pytest.mark.django_db
class TestAuthChangePassword:
    """Tests endpoint /api/auth/change-password/."""

    def test_change_password_success(self, auth_client, user):
        """Changement de mot de passe réussi."""
        response = auth_client.post(
            "/api/auth/change-password/",
            {
                "old_password": "TestPass123!",
                "new_password": "NewPass456!",
                "new_password_confirm": "NewPass456!",
            },
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("NewPass456!")

    def test_change_password_wrong_old(self, auth_client):
        """Ancien mot de passe incorrect."""
        response = auth_client.post(
            "/api/auth/change-password/",
            {
                "old_password": "WrongPass!",
                "new_password": "NewPass456!",
                "new_password_confirm": "NewPass456!",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_change_password_unauthenticated(self, api_client):
        """Accès refusé sans token."""
        response = api_client.post(
            "/api/auth/change-password/",
            {
                "old_password": "TestPass123!",
                "new_password": "NewPass456!",
                "new_password_confirm": "NewPass456!",
            },
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestAuthDeleteAccount:
    """Tests endpoint /api/auth/delete-account/."""

    def test_delete_account_success(self, auth_client, user):
        """Suppression du compte reussie."""
        response = auth_client.post(
            "/api/auth/delete-account/",
            {"password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == 200
        from apps.auth.models import User
        assert not User.objects.filter(email=user.email).exists()

    def test_delete_account_wrong_password(self, auth_client):
        """Mot de passe incorrect."""
        response = auth_client.post(
            "/api/auth/delete-account/",
            {"password": "WrongPass!"},
            format="json",
        )
        assert response.status_code == 400

    def test_delete_account_unauthenticated(self, api_client):
        """Acces refuse sans token."""
        response = api_client.post(
            "/api/auth/delete-account/",
            {"password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_delete_account_missing_password(self, auth_client):
        """Mot de passe manquant."""
        response = auth_client.post(
            "/api/auth/delete-account/",
            {},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuthTokenRefresh:
    """Tests endpoint /api/auth/token/refresh/."""

    def test_token_refresh(self, api_client, user):
        """Rafraîchissement du token."""
        login_resp = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )
        refresh = login_resp.data["refresh"]
        response = api_client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data
