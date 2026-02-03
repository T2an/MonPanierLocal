"""Tests unitaires API Products."""
import pytest
from decimal import Decimal

from apps.auth.models import User
from apps.producers.models import ProducerProfile
from apps.products.models import ProductCategory, Product


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
def product_category(db):
    """Catégorie de produit."""
    cat, _ = ProductCategory.objects.get_or_create(
        name="legumes",
        defaults={
            "icon": "carrot",
            "display_name": "Légumes",
            "order": 0,
        },
    )
    return cat


@pytest.fixture
def product(producer_profile, product_category, db):
    """Produit de test."""
    return Product.objects.create(
        producer=producer_profile,
        category=product_category,
        name="Tomates bio",
        description="Belles tomates",
        availability_type="all_year",
    )


@pytest.fixture
def auth_producer_client(api_client, producer_user):
    """Client API authentifié producteur."""
    response = api_client.post(
        "/api/auth/login/",
        {"email": producer_user.email, "password": "ProducerPass123!"},
        format="json",
    )
    assert response.status_code == 200
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return api_client


@pytest.mark.django_db
class TestProductCategories:
    """Tests GET /api/products/categories/."""

    def test_categories_list_public(self, api_client, product_category):
        """Liste des catégories accessible sans auth."""
        response = api_client.get("/api/products/categories/")
        assert response.status_code == 200
        assert isinstance(response.data, list) or "results" in response.data


@pytest.mark.django_db
class TestProductsList:
    """Tests GET /api/products/."""

    def test_products_list_public(self, api_client, product):
        """Liste des produits accessible sans auth."""
        response = api_client.get("/api/products/")
        assert response.status_code == 200
        data = response.data
        if isinstance(data, dict) and "results" in data:
            assert len(data["results"]) >= 1
        else:
            assert len(data) >= 1


@pytest.mark.django_db
class TestProductsByProducer:
    """Tests GET /api/producers/{id}/products/."""

    def test_producer_products_public(self, api_client, producer_profile, product):
        """Produits d'un producteur accessibles sans auth."""
        response = api_client.get(
            f"/api/producers/{producer_profile.id}/products/"
        )
        assert response.status_code == 200
        data = response.data
        if isinstance(data, dict) and "results" in data:
            assert len(data["results"]) >= 1
        else:
            assert len(data) >= 1


@pytest.mark.django_db
class TestProductCreate:
    """Tests POST /api/producers/{id}/products/."""

    def test_create_product_authenticated_owner(
        self, auth_producer_client, producer_profile, product_category
    ):
        """Création d'un produit par le propriétaire."""
        data = {
            "name": "Carottes",
            "description": "Carottes bio",
            "category_id": product_category.id,
            "availability_type": "all_year",
        }
        response = auth_producer_client.post(
            f"/api/producers/{producer_profile.id}/products/",
            data,
            format="json",
        )
        assert response.status_code in (200, 201)
        assert Product.objects.filter(name="Carottes").exists()

    def test_create_product_unauthenticated(
        self, api_client, producer_profile, product_category
    ):
        """Création refusée sans auth."""
        data = {
            "name": "Carottes",
            "description": "Carottes bio",
            "category_id": product_category.id,
        }
        response = api_client.post(
            f"/api/producers/{producer_profile.id}/products/",
            data,
            format="json",
        )
        assert response.status_code == 401
