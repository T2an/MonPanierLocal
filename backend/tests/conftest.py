"""Configuration pytest pour les tests backend."""
import os

# Forcer SQLite + DummyCache pour les tests (avant import Django)
os.environ.setdefault("USE_LOCAL_DEV", "True")
os.environ.setdefault("DEBUG", "True")
os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,testserver"

import pytest
from rest_framework.test import APIClient

from apps.auth.models import User


@pytest.fixture
def api_client():
    """Client API REST Framework."""
    return APIClient()


@pytest.fixture
def user(db):
    """Utilisateur de test."""
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="TestPass123!",
        is_producer=False,
    )


@pytest.fixture
def producer_user(db):
    """Utilisateur producteur de test."""
    return User.objects.create_user(
        email="producer@example.com",
        username="producer",
        password="ProducerPass123!",
        is_producer=True,
    )


@pytest.fixture
def auth_client(api_client, user):
    """Client API authentifié (User.USERNAME_FIELD=email)."""
    response = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "TestPass123!"},
        format="json",
    )
    assert response.status_code == 200
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
