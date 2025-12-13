from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Product, ProductCategory, ProductPhoto
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    ProductCategorySerializer, ProductPhotoSerializer
)
from .permissions import IsProductOwner
from apps.producers.models import ProducerProfile
import logging

logger = logging.getLogger(__name__)


class ProductCategoryViewSet(ReadOnlyModelViewSet):
    """ViewSet pour les catégories de produits (lecture seule)."""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les produits."""
    queryset = Product.objects.all().select_related('producer', 'category').prefetch_related('photos')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'photos']:
            return [IsAuthenticated(), IsProductOwner()]
        return super().get_permissions()

    def get_queryset(self):
        """Filtrer par producteur si producer_id est dans les kwargs."""
        queryset = super().get_queryset()
        producer_id = self.kwargs.get('producer_id')
        if producer_id:
            queryset = queryset.filter(producer_id=producer_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Créer un produit pour un producteur."""
        producer_id = kwargs.get('producer_id')
        if not producer_id:
            return Response(
                {'error': 'producer_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        producer = get_object_or_404(ProducerProfile, id=producer_id)

        # Vérifier que l'utilisateur est propriétaire du producteur
        if producer.user != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à ajouter des produits à ce producteur.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductCreateSerializer(
            data=request.data,
            context={'producer_id': producer_id, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsProductOwner])
    def photos(self, request, pk=None):
        """Ajouter une photo à un produit (maximum 5 photos)."""
        product = self.get_object()
        
        # Vérifier la limite de 5 photos
        current_photo_count = product.photos.count()
        if current_photo_count >= 5:
            return Response(
                {'error': 'Le nombre maximum de photos (5) a été atteint pour ce produit.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProductPhotoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(product=product)
                logger.info(f"Photo uploaded for product {product.id} by user {request.user.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                logger.warning(f"Validation error uploading photo: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les photos de produits."""
    queryset = ProductPhoto.objects.all().select_related('product')
    serializer_class = ProductPhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        """Supprimer une photo."""
        photo = self.get_object()
        # Vérifier que l'utilisateur est propriétaire du produit
        if photo.product.producer.user != request.user:
            logger.warning(f"Unauthorized photo deletion attempt: user {request.user.id} tried to delete photo {photo.id}")
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à supprimer cette photo.'},
                status=status.HTTP_403_FORBIDDEN
            )
        logger.info(f"Photo {photo.id} deleted by user {request.user.id}")
        return super().destroy(request, *args, **kwargs)

