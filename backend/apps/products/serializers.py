from rest_framework import serializers
from .models import Product, ProductCategory, ProductPhoto


class ProducerSimpleSerializer(serializers.Serializer):
    """Serializer simple pour le producteur (évite la récursion)."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de produits."""
    class Meta:
        model = ProductCategory
        fields = ('id', 'name', 'icon', 'display_name', 'order')
        read_only_fields = ('id',)


class ProductPhotoSerializer(serializers.ModelSerializer):
    """Serializer pour les photos de produits."""
    class Meta:
        model = ProductPhoto
        fields = ('id', 'image_file', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_image_file(self, value):
        """Validate image file in serializer."""
        from apps.producers.validators import validate_image_file
        return validate_image_file(value)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer pour les produits."""
    producer = ProducerSimpleSerializer(read_only=True)
    category = ProductCategorySerializer(read_only=True)
    photos = ProductPhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(source='photos.count', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'producer', 'category', 'name', 'description',
            'availability_type', 'availability_start_month', 'availability_end_month',
            'photos', 'photo_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un produit."""
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = (
            'name', 'description', 'category_id',
            'availability_type', 'availability_start_month', 'availability_end_month'
        )

    def validate_category_id(self, value):
        """Validate that the category exists."""
        if value is not None and not ProductCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("Catégorie invalide.")
        return value

    def validate(self, data):
        """Validate availability fields."""
        availability_type = data.get('availability_type', Product.AVAILABILITY_ALL_YEAR)
        if availability_type == Product.AVAILABILITY_CUSTOM:
            start_month = data.get('availability_start_month')
            end_month = data.get('availability_end_month')
            if not start_month or not end_month:
                raise serializers.ValidationError(
                    "Les mois de début et de fin sont requis pour une période personnalisée."
                )
            if start_month > end_month:
                raise serializers.ValidationError(
                    "Le mois de début doit être antérieur ou égal au mois de fin."
                )
        return data

    def create(self, validated_data):
        producer_id = self.context['producer_id']
        category_id = validated_data.pop('category_id', None)
        validated_data['producer_id'] = producer_id
        if category_id:
            validated_data['category_id'] = category_id
        return super().create(validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour un produit."""
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = (
            'name', 'description', 'category_id',
            'availability_type', 'availability_start_month', 'availability_end_month'
        )

    def validate_category_id(self, value):
        """Validate that the category exists."""
        if value is not None and not ProductCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("Catégorie invalide.")
        return value

    def validate(self, data):
        """Validate availability fields."""
        availability_type = data.get('availability_type', self.instance.availability_type if self.instance else Product.AVAILABILITY_ALL_YEAR)
        if availability_type == Product.AVAILABILITY_CUSTOM:
            start_month = data.get('availability_start_month', self.instance.availability_start_month if self.instance else None)
            end_month = data.get('availability_end_month', self.instance.availability_end_month if self.instance else None)
            if not start_month or not end_month:
                raise serializers.ValidationError(
                    "Les mois de début et de fin sont requis pour une période personnalisée."
                )
            if start_month > end_month:
                raise serializers.ValidationError(
                    "Le mois de début doit être antérieur ou égal au mois de fin."
                )
        elif availability_type == Product.AVAILABILITY_ALL_YEAR:
            # Si on passe à "tout l'année", mettre les mois à None
            data['availability_start_month'] = None
            data['availability_end_month'] = None
        return data

    def update(self, instance, validated_data):
        # Gérer category_id : le retirer de validated_data pour le traiter séparément
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            # Une catégorie a été sélectionnée
            validated_data['category_id'] = category_id
        elif 'category_id' in validated_data or category_id is None:
            # category_id est explicitement None ou présent dans validated_data, supprimer la catégorie
            validated_data['category_id'] = None
        # Si category_id n'est pas dans validated_data, ne pas le modifier
        return super().update(instance, validated_data)

