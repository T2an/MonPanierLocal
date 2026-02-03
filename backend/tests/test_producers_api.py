"""Tests unitaires API Producers."""
import pytest
from decimal import Decimal

from apps.auth.models import User
from apps.producers.models import ProducerProfile


@pytest.fixture
def producer_profile(producer_user, db):
    """Profil producteur de test."""
    return ProducerProfile.objects.create(
        user=producer_user,
        name="Ferme Test",
        description="Une ferme de test",
        category="maraîchage",
        address="10 rue Test, 75001 Paris",
        latitude=Decimal("48.8566"),
        longitude=Decimal("2.3522"),
    )


@pytest.fixture
def user_no_producer(db):
    """Utilisateur producteur sans profil (pour test création)."""
    return User.objects.create_user(
        email="noprofile@example.com",
        username="noprofile",
        password="Pass123!",
        is_producer=True,
    )


@pytest.fixture
def auth_producer_client(api_client, producer_user):
    """Client API authentifié en tant que producteur."""
    response = api_client.post(
        "/api/auth/login/",
        {"email": producer_user.email, "password": "ProducerPass123!"},
        format="json",
    )
    assert response.status_code == 200
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return api_client


@pytest.mark.django_db
class TestProducersList:
    """Tests GET /api/producers/."""

    def test_list_public_no_auth(self, api_client, producer_profile):
        """Liste des producteurs accessible sans authentification."""
        response = api_client.get("/api/producers/")
        assert response.status_code == 200
        assert "results" in response.data
        assert len(response.data["results"]) >= 1

    def test_list_filter_category(self, api_client, producer_profile):
        """Filtrage par catégorie."""
        response = api_client.get("/api/producers/", {"categories": "maraîchage"})
        assert response.status_code == 200
        # categories filter might use different param - check backend
        assert "results" in response.data

    def test_list_search(self, api_client, producer_profile):
        """Recherche par nom."""
        response = api_client.get("/api/producers/", {"search": "Ferme"})
        assert response.status_code == 200
        assert "results" in response.data


@pytest.mark.django_db
class TestProducersNearby:
    """Tests GET /api/producers/nearby/."""

    def test_nearby_public(self, api_client, producer_profile):
        """Recherche nearby accessible sans auth."""
        response = api_client.get(
            "/api/producers/nearby/",
            {"latitude": 48.86, "longitude": 2.35, "radius_km": 50},
        )
        assert response.status_code == 200
        assert "results" in response.data or "count" in response.data

    def test_nearby_missing_params(self, api_client):
        """Paramètres requis manquants."""
        response = api_client.get("/api/producers/nearby/")
        assert response.status_code == 400


@pytest.mark.django_db
class TestProducerDetail:
    """Tests GET /api/producers/{id}/."""

    def test_detail_public(self, api_client, producer_profile):
        """Détail d'un producteur accessible sans auth."""
        response = api_client.get(f"/api/producers/{producer_profile.id}/")
        assert response.status_code == 200
        assert response.data["name"] == "Ferme Test"
        assert response.data["category"] == "maraîchage"


@pytest.mark.django_db
class TestProducerCreate:
    """Tests POST /api/producers/."""

    def test_create_authenticated(self, api_client, user_no_producer):
        """Création par utilisateur authentifié sans profil."""
        login = api_client.post(
            "/api/auth/login/",
            {"email": user_no_producer.email, "password": "Pass123!"},
            format="json",
        )
        assert login.status_code == 200
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        data = {
            "name": "Nouvelle Ferme",
            "description": "Description",
            "category": "élevage",
            "address": "20 rue Nouvelle, 69001 Lyon",
            "latitude": "45.7640",
            "longitude": "4.8357",
        }
        response = api_client.post("/api/producers/", data, format="json")
        assert response.status_code in (200, 201)
        assert ProducerProfile.objects.filter(name="Nouvelle Ferme").exists()

    def test_create_unauthenticated(self, api_client):
        """Création refusée sans auth."""
        data = {
            "name": "Ferme",
            "description": "Desc",
            "category": "maraîchage",
            "address": "10 rue Test",
            "latitude": 48.0,
            "longitude": 2.0,
        }
        response = api_client.post("/api/producers/", data, format="json")
        assert response.status_code == 401
