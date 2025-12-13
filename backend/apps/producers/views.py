import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import ProducerProfile, ProducerPhoto, SaleMode
from .serializers import (
    ProducerProfileSerializer,
    ProducerProfileCreateSerializer,
    ProducerPhotoSerializer,
    SaleModeSerializer,
    SaleModeCreateSerializer,
    SaleModeUpdateSerializer
)
from .permissions import IsProducerOwner
from .utils import get_producers_near_location

logger = logging.getLogger(__name__)


class ProducerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les profils de producteurs."""
    queryset = ProducerProfile.objects.all().select_related('user').prefetch_related(
        'photos',
        'products__category',
        'products__photos',
        'sale_modes__opening_hours'
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProducerProfileCreateSerializer
        return ProducerProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProducerOwner()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Créer un profil producteur."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"Producer profile created: {serializer.instance.id} by user {request.user.id}")
            return Response(
                ProducerProfileSerializer(serializer.instance).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            logger.warning(f"Validation error creating producer profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating producer profile: {e}", exc_info=True)
            raise

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsProducerOwner])
    def photos(self, request, pk=None):
        """Ajouter une photo à un producteur."""
        producer = self.get_object()
        serializer = ProducerPhotoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(producer=producer)
                logger.info(f"Photo uploaded for producer {producer.id} by user {request.user.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                logger.warning(f"Validation error uploading photo: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Note: L'action 'search' a été supprimée car redondante.
    # La recherche est gérée par les filtres DRF (search_fields) dans getProducers()
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Récupérer les producteurs proches d'une position avec distances."""
        from .utils import haversine_distance
        
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius_km', '50')  # 50km par défaut

        if not latitude or not longitude:
            return Response(
                {'error': 'Les paramètres latitude et longitude sont requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(latitude)
            lng = float(longitude)
            radius = float(radius_km)
            
            queryset = get_producers_near_location(lat, lng, radius)
            queryset = queryset.select_related('user').prefetch_related(
                'photos',
                'products__category',
                'products__photos',
                'sale_modes__opening_hours'
            )
            
            # Calculer les distances et trier par distance
            producers_with_distance = []
            for producer in queryset:
                distance = haversine_distance(
                    lat, lng,
                    float(producer.latitude), float(producer.longitude)
                )
                producers_with_distance.append((producer, distance))
            
            # Trier par distance
            producers_with_distance.sort(key=lambda x: x[1])
            
            # Extraire les producteurs triés
            sorted_producers = [p[0] for p in producers_with_distance]
            
            page = self.paginate_queryset(sorted_producers)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                # Ajouter les distances aux résultats
                distances = [p[1] for p in producers_with_distance[:len(page)]]
                response.data['distances'] = distances
                return response

            serializer = self.get_serializer(sorted_producers, many=True)
            distances = [p[1] for p in producers_with_distance]
            return Response({
                'results': serializer.data,
                'distances': distances,
                'count': len(sorted_producers)
            })
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Paramètres invalides: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProducerPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les photos de producteurs."""
    queryset = ProducerPhoto.objects.all().select_related('producer')
    serializer_class = ProducerPhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        """Supprimer une photo."""
        photo = self.get_object()
        # Vérifier que l'utilisateur est propriétaire du producteur
        if photo.producer.user != request.user:
            logger.warning(f"Unauthorized photo deletion attempt: user {request.user.id} tried to delete photo {photo.id}")
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à supprimer cette photo.'},
                status=status.HTTP_403_FORBIDDEN
            )
        logger.info(f"Photo {photo.id} deleted by user {request.user.id}")
        return super().destroy(request, *args, **kwargs)


class SaleModeViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les modes de vente."""
    queryset = SaleMode.objects.all().select_related('producer').prefetch_related('opening_hours')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return SaleModeCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SaleModeUpdateSerializer
        return SaleModeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """Filtrer par producteur si producer_id est dans les kwargs."""
        queryset = super().get_queryset()
        producer_id = self.kwargs.get('producer_id')
        if producer_id:
            queryset = queryset.filter(producer_id=producer_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Créer un mode de vente pour un producteur."""
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
                {'error': 'Vous n\'êtes pas autorisé à ajouter des modes de vente à ce producteur.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SaleModeCreateSerializer(
            data=request.data,
            context={'producer_id': producer_id, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        sale_mode = serializer.save(producer=producer)
        return Response(
            SaleModeSerializer(sale_mode).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Mettre à jour un mode de vente."""
        sale_mode = self.get_object()
        # Vérifier que l'utilisateur est propriétaire du producteur
        if sale_mode.producer.user != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à modifier ce mode de vente.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un mode de vente."""
        sale_mode = self.get_object()
        # Vérifier que l'utilisateur est propriétaire du producteur
        if sale_mode.producer.user != request.user:
            logger.warning(f"Unauthorized sale mode deletion attempt: user {request.user.id} tried to delete sale mode {sale_mode.id}")
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à supprimer ce mode de vente.'},
                status=status.HTTP_403_FORBIDDEN
            )
        logger.info(f"Sale mode {sale_mode.id} deleted by user {request.user.id}")
        return super().destroy(request, *args, **kwargs)
