from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer JWT personnalisé avec informations utilisateur."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_producer'] = user.is_producer
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue pour obtenir les tokens JWT."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Endpoint d'inscription."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Inscription réussie'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """Endpoint pour obtenir ou modifier les informations de l'utilisateur connecté."""
    if request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Endpoint pour changer le mot de passe."""
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')

    if not old_password or not new_password or not new_password_confirm:
        return Response(
            {'error': 'Tous les champs sont requis.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != new_password_confirm:
        return Response(
            {'error': 'Les nouveaux mots de passe ne correspondent pas.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not request.user.check_password(old_password):
        return Response(
            {'error': 'Ancien mot de passe incorrect.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(new_password, request.user)
    except ValidationError as e:
        return Response(
            {'error': '; '.join(e.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)

    return Response({'message': 'Mot de passe modifié avec succès.'})

