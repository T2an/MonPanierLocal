"""Tests unitaires - Photos producteurs et produits (affichage, modification, acces public)."""
import io
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.auth.models import User
from apps.producers.models import ProducerProfile, ProducerPhoto
from apps.products.models import Product, ProductCategory, ProductPhoto


def make_image_file(name="test.jpg", size=(100, 100)):
    """Genere une image JPEG valide pour les tests."""
    img = Image.new("RGB", size, color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/jpeg")


@pytest.fixture
def producer_with_photo(db, producer_user):
    """Producteur avec une photo."""
    producer = ProducerProfile.objects.create(
        user=producer_user,
        name="Ferme Test Photo",
        description="Test",
        category="maraîchage",
        address="10 rue Test",
        latitude=Decimal("48.8566"),
        longitude=Decimal("2.3522"),
    )
    img = make_image_file("producer_1.jpg")
    ProducerPhoto.objects.create(producer=producer, image_file=img)
    return producer


@pytest.fixture
def product_with_photo(producer_with_photo, db):
    """Produit avec une photo."""
    cat, _ = ProductCategory.objects.get_or_create(
        name="legumes", defaults={"icon": "carrot", "display_name": "Legumes", "order": 0}
    )
    product = Product.objects.create(
        producer=producer_with_photo,
        category=cat,
        name="Tomates",
        description="Tomates bio",
        availability_type="all_year",
    )
    img = make_image_file("product_1.jpg")
    ProductPhoto.objects.create(product=product, image_file=img)
    return product


@pytest.fixture
def auth_producer_client(api_client, producer_user):
    """Client API authentifie producteur."""
    r = api_client.post(
        "/api/auth/login/",
        {"email": producer_user.email, "password": "ProducerPass123!"},
        format="json",
    )
    assert r.status_code == 200
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return api_client


@pytest.fixture
def other_user_client(api_client, db):
    """Client API authentifie avec un autre utilisateur (non producteur)."""
    user = User.objects.create_user(
        email="other@example.com",
        username="other",
        password="OtherPass123!",
        is_producer=False,
    )
    r = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "OtherPass123!"},
        format="json",
    )
    assert r.status_code == 200
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return api_client


@pytest.mark.django_db
class TestPhotosAccessibilitePublique:
    """Photos visibles sans authentification."""

    def test_photos_producteur_visibles_detail_public(
        self, api_client, producer_with_photo
    ):
        """Les photos d'un producteur sont incluses dans le detail (GET public)."""
        response = api_client.get(f"/api/producers/{producer_with_photo.id}/")
        assert response.status_code == 200
        assert "photos" in response.data
        assert len(response.data["photos"]) >= 1
        assert "image_file" in response.data["photos"][0]
        assert response.data["photo_count"] >= 1

    def test_photos_produit_visibles_detail_public(
        self, api_client, product_with_photo
    ):
        """Les photos d'un produit sont incluses dans le detail (GET public)."""
        pid = product_with_photo.producer_id
        response = api_client.get(
            f"/api/producers/{pid}/products/{product_with_photo.id}/"
        )
        assert response.status_code == 200
        assert "photos" in response.data
        assert len(response.data["photos"]) >= 1
        assert "image_file" in response.data["photos"][0]

    def test_liste_producteurs_inclut_photo_count(
        self, api_client, producer_with_photo
    ):
        """La liste des producteurs inclut photo_count."""
        response = api_client.get("/api/producers/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        producer = next((p for p in results if p["id"] == producer_with_photo.id), None)
        assert producer is not None
        assert "photo_count" in producer
        assert producer["photo_count"] >= 1


@pytest.mark.django_db
class TestPhotosProducteurModification:
    """Le producteur peut ajouter/supprimer ses photos."""

    def test_producteur_peut_ajouter_photo(
        self, auth_producer_client, producer_with_photo
    ):
        """POST /api/producers/{id}/photos/ ajoute une photo."""
        initial_count = producer_with_photo.photos.count()
        img = make_image_file("new_photo.jpg")
        response = auth_producer_client.post(
            f"/api/producers/{producer_with_photo.id}/photos/",
            {"image_file": img},
            format="multipart",
        )
        assert response.status_code == 201
        producer_with_photo.refresh_from_db()
        assert producer_with_photo.photos.count() == initial_count + 1

    def test_producteur_peut_supprimer_sa_photo(
        self, auth_producer_client, producer_with_photo
    ):
        """DELETE /api/photos/{id}/ supprime la photo (proprietaire)."""
        photo = producer_with_photo.photos.first()
        assert photo is not None
        response = auth_producer_client.delete(f"/api/photos/{photo.id}/")
        assert response.status_code == 204
        assert not ProducerPhoto.objects.filter(id=photo.id).exists()

    def test_autre_utilisateur_ne_peut_pas_supprimer_photo(
        self, other_user_client, producer_with_photo
    ):
        """Un utilisateur non proprietaire ne peut pas supprimer une photo."""
        photo = producer_with_photo.photos.first()
        assert photo is not None
        response = other_user_client.delete(f"/api/photos/{photo.id}/")
        assert response.status_code == 403
        assert ProducerPhoto.objects.filter(id=photo.id).exists()

    def test_non_authentifie_ne_peut_pas_ajouter_photo(
        self, api_client, producer_with_photo
    ):
        """POST photos sans auth -> 401."""
        img = make_image_file("test.jpg")
        response = api_client.post(
            f"/api/producers/{producer_with_photo.id}/photos/",
            {"image_file": img},
            format="multipart",
        )
        assert response.status_code == 401

    def test_non_authentifie_ne_peut_pas_supprimer_photo(
        self, api_client, producer_with_photo
    ):
        """DELETE photo sans auth -> 401."""
        photo = producer_with_photo.photos.first()
        response = api_client.delete(f"/api/photos/{photo.id}/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestPhotosProduitModification:
    """Le producteur peut ajouter des photos a ses produits."""

    def test_producteur_peut_ajouter_photo_produit(
        self, auth_producer_client, product_with_photo
    ):
        """POST /api/producers/{id}/products/{product_id}/photos/ ajoute une photo."""
        pid = product_with_photo.producer_id
        initial_count = product_with_photo.photos.count()
        img = make_image_file("product_new.jpg")
        response = auth_producer_client.post(
            f"/api/producers/{pid}/products/{product_with_photo.id}/photos/",
            {"image_file": img},
            format="multipart",
        )
        assert response.status_code == 201
        product_with_photo.refresh_from_db()
        assert product_with_photo.photos.count() == initial_count + 1

    def test_producteur_peut_supprimer_photo_produit(
        self, auth_producer_client, product_with_photo
    ):
        """DELETE /api/products/photos/{id}/ supprime la photo produit (proprietaire)."""
        photo = product_with_photo.photos.first()
        response = auth_producer_client.delete(
            f"/api/products/photos/{photo.id}/"
        )
        assert response.status_code == 204
        assert not ProductPhoto.objects.filter(id=photo.id).exists()
