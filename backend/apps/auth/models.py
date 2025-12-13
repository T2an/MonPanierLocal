from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modèle utilisateur personnalisé avec support producteur."""
    email = models.EmailField(unique=True)
    is_producer = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Éviter les conflits avec django.contrib.auth
    class Meta:
        db_table = 'custom_auth_user'

    def __str__(self):
        return self.email

