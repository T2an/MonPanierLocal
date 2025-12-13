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
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'is_producer')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            is_producer=validated_data.get('is_producer', False)
        )
        return user

