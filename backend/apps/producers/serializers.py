from rest_framework import serializers
from decimal import Decimal
from .models import ProducerProfile, ProducerPhoto, SaleMode, OpeningHours
from .validators import validate_coordinates
from apps.auth.serializers import UserSerializer
from apps.products.models import Product

class ProducerPhotoSerializer(serializers.ModelSerializer):
    """Serializer pour les photos de producteurs."""
    class Meta:
        model = ProducerPhoto
        fields = ('id', 'image_file', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_image_file(self, value):
        """Validate image file in serializer."""
        from .validators import validate_image_file
        return validate_image_file(value)


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour les produits (évite la récursion)."""
    category = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    photo_count = serializers.IntegerField(source='photos.count', read_only=True)
    availability_type = serializers.CharField(read_only=True, default='all_year')
    availability_start_month = serializers.IntegerField(read_only=True, allow_null=True, required=False)
    availability_end_month = serializers.IntegerField(read_only=True, allow_null=True, required=False)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'category', 'photos', 'photo_count',
            'availability_type', 'availability_start_month', 'availability_end_month',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to ensure availability fields are included."""
        ret = super().to_representation(instance)
        # Forcer l'inclusion des champs de disponibilité depuis l'instance
        # On accède directement aux attributs du modèle si ils existent
        ret['availability_type'] = getattr(instance, 'availability_type', 'all_year')
        ret['availability_start_month'] = getattr(instance, 'availability_start_month', None)
        ret['availability_end_month'] = getattr(instance, 'availability_end_month', None)
        return ret
    
    def get_category(self, obj):
        """Return category info."""
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'icon': obj.category.icon,
                'display_name': obj.category.display_name
            }
        return None
    
    def get_photos(self, obj):
        """Return photos list."""
        from apps.products.serializers import ProductPhotoSerializer
        # Photos are already prefetched in the viewset
        photos = obj.photos.all()
        return ProductPhotoSerializer(photos, many=True).data


class ProducerProfileSerializer(serializers.ModelSerializer):
    """Serializer pour les profils de producteurs."""
    user = UserSerializer(read_only=True)
    photos = ProducerPhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(source='photos.count', read_only=True)
    products = serializers.SerializerMethodField()
    sale_modes = serializers.SerializerMethodField()

    class Meta:
        model = ProducerProfile
        fields = (
            'id', 'user', 'name', 'description', 'category',
            'address', 'latitude', 'longitude', 'phone', 'email_contact', 'website', 'opening_hours',
            'photos', 'photo_count', 'products', 'sale_modes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_products(self, obj):
        """Return products list - safely handle missing availability fields."""
        try:
            products = obj.products.all()
            return ProductSimpleSerializer(products, many=True).data
        except Exception:
            # If products table has missing columns, return empty list
            return []

    def get_sale_modes(self, obj):
        """Return sale modes - safely handle missing table."""
        try:
            sale_modes = obj.sale_modes.all().prefetch_related('opening_hours')
            return SaleModeSerializer(sale_modes, many=True).data
        except Exception:
            # If sale_modes table doesn't exist, return empty list
            return []


class ProducerProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un profil producteur."""
    # Utiliser CharField pour arrondir avant la conversion en Decimal
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    
    class Meta:
        model = ProducerProfile
        fields = (
            'name', 'description', 'category', 'address', 'latitude', 'longitude',
            'phone', 'email_contact', 'website', 'opening_hours'
        )

    def validate_name(self, value):
        """Validate producer name."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Le nom de l'exploitation doit contenir au moins 2 caractères.")
        return value.strip()

    def validate_latitude(self, value):
        """Validate latitude and round to 7 decimal places."""
        try:
            lat_float = float(value)
            validate_coordinates(lat_float, 0)
            return Decimal(str(round(lat_float, 7)))
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(f"Latitude invalide: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_longitude(self, value):
        """Validate longitude and round to 7 decimal places."""
        try:
            lng_float = float(value)
            validate_coordinates(0, lng_float)
            return Decimal(str(round(lng_float, 7)))
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(f"Longitude invalide: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate(self, attrs):
        """Cross-field validation."""
        user = self.context['request'].user
        if not user.is_producer:
            raise serializers.ValidationError("L'utilisateur doit être un producteur.")
        if ProducerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Un profil producteur existe déjà pour cet utilisateur.")
        
        # Validate coordinates together
        if 'latitude' in attrs and 'longitude' in attrs:
            validate_coordinates(attrs['latitude'], attrs['longitude'])
        
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OpeningHoursSerializer(serializers.ModelSerializer):
    """Serializer pour les horaires d'ouverture."""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = OpeningHours
        fields = (
            'id', 'day_of_week', 'day_name', 'is_closed',
            'opening_time', 'closing_time'
        )
        read_only_fields = ('id',)

    def validate(self, data):
        """Validate opening hours."""
        if not data.get('is_closed'):
            if not data.get('opening_time') or not data.get('closing_time'):
                raise serializers.ValidationError(
                    "Les heures d'ouverture et de fermeture sont requises si le jour n'est pas fermé."
                )
            if data['opening_time'] >= data['closing_time']:
                raise serializers.ValidationError(
                    "L'heure d'ouverture doit être antérieure à l'heure de fermeture."
                )
        return data


class SaleModeSerializer(serializers.ModelSerializer):
    """Serializer pour les modes de vente."""
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    mode_type_display = serializers.CharField(source='get_mode_type_display', read_only=True)

    class Meta:
        model = SaleMode
        fields = (
            'id', 'mode_type', 'mode_type_display', 'title', 'instructions',
            'phone_number', 'website_url', 'is_24_7',
            'location_address', 'location_latitude', 'location_longitude',
            'market_info', 'order', 'opening_hours',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate according to mode type."""
        mode_type = data.get('mode_type', self.instance.mode_type if self.instance else None)
        
        if mode_type == 'phone_order':
            phone_number = data.get('phone_number', self.instance.phone_number if self.instance else '')
            if not phone_number:
                raise serializers.ValidationError({
                    'phone_number': 'Le numéro de téléphone est obligatoire pour les commandes par téléphone.'
                })
        
        # Validate coordinates if provided
        if data.get('location_latitude') and data.get('location_longitude'):
            try:
                validate_coordinates(
                    float(data['location_latitude']),
                    float(data['location_longitude'])
                )
            except Exception as e:
                raise serializers.ValidationError({
                    'location_latitude': str(e)
                })
        
        return data


class SaleModeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un mode de vente."""
    opening_hours = OpeningHoursSerializer(many=True, required=False)
    location_latitude = serializers.CharField(required=False, allow_blank=True)
    location_longitude = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = SaleMode
        fields = (
            'mode_type', 'title', 'instructions',
            'phone_number', 'website_url', 'is_24_7',
            'location_address', 'location_latitude', 'location_longitude',
            'market_info', 'order', 'opening_hours'
        )

    def validate_location_latitude(self, value):
        """Validate and convert latitude."""
        if not value:
            return None
        try:
            lat_float = float(value)
            return Decimal(str(round(lat_float, 7)))
        except (ValueError, TypeError):
            raise serializers.ValidationError("Latitude invalide.")

    def validate_location_longitude(self, value):
        """Validate and convert longitude."""
        if not value:
            return None
        try:
            lng_float = float(value)
            return Decimal(str(round(lng_float, 11)))
        except (ValueError, TypeError):
            raise serializers.ValidationError("Longitude invalide.")

    def validate(self, data):
        """Validate according to mode type."""
        mode_type = data.get('mode_type')
        
        if mode_type == 'phone_order' and not data.get('phone_number'):
            raise serializers.ValidationError({
                'phone_number': 'Le numéro de téléphone est obligatoire pour les commandes par téléphone.'
            })
        
        return data

    def create(self, validated_data):
        """Create sale mode with opening hours."""
        opening_hours_data = validated_data.pop('opening_hours', [])
        sale_mode = SaleMode.objects.create(**validated_data)
        
        # Create opening hours
        for hours_data in opening_hours_data:
            OpeningHours.objects.create(sale_mode=sale_mode, **hours_data)
        
        return sale_mode


class SaleModeUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour un mode de vente."""
    opening_hours = OpeningHoursSerializer(many=True, required=False)
    location_latitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location_longitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SaleMode
        fields = (
            'mode_type', 'title', 'instructions',
            'phone_number', 'website_url', 'is_24_7',
            'location_address', 'location_latitude', 'location_longitude',
            'market_info', 'order', 'opening_hours'
        )

    def validate_location_latitude(self, value):
        """Validate and convert latitude."""
        if not value or value == '':
            return None
        try:
            lat_float = float(value)
            return Decimal(str(round(lat_float, 7)))
        except (ValueError, TypeError):
            raise serializers.ValidationError("Latitude invalide.")

    def validate_location_longitude(self, value):
        """Validate and convert longitude."""
        if not value or value == '':
            return None
        try:
            lng_float = float(value)
            return Decimal(str(round(lng_float, 11)))
        except (ValueError, TypeError):
            raise serializers.ValidationError("Longitude invalide.")

    def validate(self, data):
        """Validate according to mode type."""
        mode_type = data.get('mode_type', self.instance.mode_type if self.instance else None)
        
        if mode_type == 'phone_order':
            phone_number = data.get('phone_number', self.instance.phone_number if self.instance else '')
            if not phone_number:
                raise serializers.ValidationError({
                    'phone_number': 'Le numéro de téléphone est obligatoire pour les commandes par téléphone.'
                })
        
        return data

    def update(self, instance, validated_data):
        """Update sale mode with opening hours."""
        opening_hours_data = validated_data.pop('opening_hours', None)
        
        # Update sale mode fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update opening hours if provided
        if opening_hours_data is not None:
            # Delete existing opening hours
            instance.opening_hours.all().delete()
            # Create new ones
            for hours_data in opening_hours_data:
                OpeningHours.objects.create(sale_mode=instance, **hours_data)
        
        return instance

