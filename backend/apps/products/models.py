from django.db import models
from django.core.validators import MinLengthValidator
from apps.producers.models import ProducerProfile


class ProductCategory(models.Model):
    """Catégorie de produit avec icône."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom de la catégorie")
    icon = models.CharField(
        max_length=100,
        verbose_name="Icône",
        help_text="Nom de l'icône (ex: carrot, apple, wheat, etc.)"
    )
    display_name = models.CharField(max_length=100, verbose_name="Nom d'affichage")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name


class Product(models.Model):
    """Produit proposé par un producteur."""
    AVAILABILITY_ALL_YEAR = 'all_year'
    AVAILABILITY_CUSTOM = 'custom'
    
    AVAILABILITY_TYPE_CHOICES = [
        (AVAILABILITY_ALL_YEAR, 'Tout l\'année'),
        (AVAILABILITY_CUSTOM, 'Période personnalisée'),
    ]
    
    MONTH_CHOICES = [
        (1, 'Janvier'),
        (2, 'Février'),
        (3, 'Mars'),
        (4, 'Avril'),
        (5, 'Mai'),
        (6, 'Juin'),
        (7, 'Juillet'),
        (8, 'Août'),
        (9, 'Septembre'),
        (10, 'Octobre'),
        (11, 'Novembre'),
        (12, 'Décembre'),
    ]
    
    producer = models.ForeignKey(
        ProducerProfile,
        on_delete=models.CASCADE,
        related_name='products',
        db_index=True
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        db_index=True,
        verbose_name="Catégorie",
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du produit",
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(blank=True, verbose_name="Description", max_length=1000)
    availability_type = models.CharField(
        max_length=20,
        choices=AVAILABILITY_TYPE_CHOICES,
        default=AVAILABILITY_ALL_YEAR,
        verbose_name="Type de disponibilité"
    )
    availability_start_month = models.IntegerField(
        choices=MONTH_CHOICES,
        null=True,
        blank=True,
        verbose_name="Mois de début"
    )
    availability_end_month = models.IntegerField(
        choices=MONTH_CHOICES,
        null=True,
        blank=True,
        verbose_name="Mois de fin"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['producer', 'created_at']),
            models.Index(fields=['category', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.producer.name}"


class ProductPhoto(models.Model):
    """Photo d'un produit."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='photos',
        db_index=True
    )
    image_file = models.ImageField(
        upload_to='products/',
        verbose_name="Photo"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Photo de produit"
        verbose_name_plural = "Photos de produits"

    def __str__(self):
        return f"Photo de {self.product.name}"

