from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_producer', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Le mot de passe doit contenir au moins 8 caractères'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'is_producer')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        """Valider que l'email n'existe pas déjà."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_username(self, value):
        """Valider que le username n'existe pas déjà."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Un utilisateur avec ce nom d'utilisateur existe déjà.")
        return value

    def validate_password(self, value):
        """Valider le mot de passe avec les validateurs Django."""
        try:
            validate_password(value)
        except Exception as e:
            # Convertir les erreurs de validation en message lisible
            if hasattr(e, 'messages'):
                raise serializers.ValidationError('; '.join(e.messages))
            raise serializers.ValidationError(str(e))
        return value

    def validate(self, attrs):
        """Valider que les mots de passe correspondent."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Les mots de passe ne correspondent pas."
            })
        return attrs

    def create(self, validated_data):
        """Créer un nouvel utilisateur."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password,
            is_producer=validated_data.get('is_producer', False)
        )
        return user

