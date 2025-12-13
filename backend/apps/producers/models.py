from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from apps.auth.models import User
from .validators import validate_image_file, validate_coordinates


class ProducerProfile(models.Model):
    """Profil d'un producteur local."""
    CATEGORY_CHOICES = [
        ('maraîchage', 'Maraîchage'),
        ('élevage', 'Élevage'),
        ('apiculture', 'Apiculture'),
        ('arboriculture', 'Arboriculture'),
        ('céréaliculture', 'Céréaliculture'),
        ('pêche', 'Pêche'),
        ('brasserie', 'Brasserie'),
        ('distillerie', 'Distillerie'),
        ('fromagerie', 'Fromagerie'),
        ('boulangerie', 'Boulangerie'),
        ('viticulture', 'Viticulture'),
        ('charcuterie', 'Charcuterie'),
        ('autre', 'Autre'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='producer_profile',
        db_index=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'exploitation",
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(blank=True, verbose_name="Description", max_length=2000)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='autre',
        db_index=True
    )
    address = models.CharField(max_length=500, verbose_name="Adresse")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, db_index=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=7, db_index=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email_contact = models.EmailField(blank=True, verbose_name="Email de contact")
    website = models.URLField(blank=True, verbose_name="Site web")
    opening_hours = models.TextField(blank=True, max_length=500, verbose_name="Horaires d'ouverture")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def clean(self):
        """Validate coordinates."""
        validate_coordinates(self.latitude, self.longitude)
        super().clean()

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProducerPhoto(models.Model):
    """Photo d'une exploitation."""
    producer = models.ForeignKey(
        ProducerProfile,
        on_delete=models.CASCADE,
        related_name='photos',
        db_index=True
    )
    image_file = models.ImageField(
        upload_to='producers/%Y/%m/%d/',
        validators=[validate_image_file]
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['producer', 'created_at']),
        ]

    def __str__(self):
        return f"Photo de {self.producer.name}"


class SaleMode(models.Model):
    """Mode de vente d'un producteur."""
    TYPE_CHOICES = [
        ('on_site', 'Vente sur place / point de vente'),
        ('phone_order', 'Commande par téléphone'),
        ('vending_machine', 'Distributeur automatique'),
        ('delivery', 'Livraison'),
        ('market', 'Marchés'),
    ]

    DAYS_OF_WEEK = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    producer = models.ForeignKey(
        ProducerProfile,
        on_delete=models.CASCADE,
        related_name='sale_modes',
        db_index=True
    )
    mode_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name="Type de mode de vente"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titre",
        help_text="Ex: 'Vente à la ferme', 'Marché de Savenay'"
    )
    instructions = models.TextField(
        max_length=500,
        verbose_name="Consigne obligatoire",
        help_text="Ex: 'Merci d'appeler 1 jour à l'avance', 'Apportez vos contenants'"
    )
    
    # Champs spécifiques selon le type
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro de téléphone",
        help_text="Obligatoire pour 'Commande par téléphone'"
    )
    website_url = models.URLField(
        blank=True,
        verbose_name="Site web",
        help_text="Pour commandes en ligne (livraison)"
    )
    is_24_7 = models.BooleanField(
        default=False,
        verbose_name="Disponible 24/7",
        help_text="Pour distributeur automatique"
    )
    location_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Adresse du point de vente",
        help_text="Si différente de l'adresse principale"
    )
    location_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitude du point de vente"
    )
    location_longitude = models.DecimalField(
        max_digits=11,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitude du point de vente"
    )
    market_info = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name="Indications marché",
        help_text="Jours, horaires et lieux des marchés"
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Mode de vente"
        verbose_name_plural = "Modes de vente"
        indexes = [
            models.Index(fields=['producer', 'order']),
        ]

    def clean(self):
        """Validation selon le type de mode."""
        if self.mode_type == 'phone_order' and not self.phone_number:
            raise ValidationError({
                'phone_number': 'Le numéro de téléphone est obligatoire pour les commandes par téléphone.'
            })
        if self.location_latitude and self.location_longitude:
            validate_coordinates(self.location_latitude, self.location_longitude)
        super().clean()

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_mode_type_display()} - {self.title} ({self.producer.name})"


class OpeningHours(models.Model):
    """Horaires d'ouverture pour un mode de vente."""
    DAYS_OF_WEEK = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    sale_mode = models.ForeignKey(
        SaleMode,
        on_delete=models.CASCADE,
        related_name='opening_hours',
        db_index=True
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name="Jour de la semaine"
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name="Fermé ce jour"
    )
    opening_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure d'ouverture"
    )
    closing_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fermeture"
    )

    class Meta:
        ordering = ['day_of_week']
        verbose_name = "Horaire d'ouverture"
        verbose_name_plural = "Horaires d'ouverture"
        unique_together = [['sale_mode', 'day_of_week']]
        indexes = [
            models.Index(fields=['sale_mode', 'day_of_week']),
        ]

    def clean(self):
        """Validation des horaires."""
        if not self.is_closed:
            if not self.opening_time or not self.closing_time:
                raise ValidationError(
                    "Les heures d'ouverture et de fermeture sont requises si le jour n'est pas fermé."
                )
            if self.opening_time >= self.closing_time:
                raise ValidationError(
                    "L'heure d'ouverture doit être antérieure à l'heure de fermeture."
                )
        super().clean()

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_of_week_display()} - Fermé"
        return f"{self.get_day_of_week_display()} - {self.opening_time} à {self.closing_time}"

