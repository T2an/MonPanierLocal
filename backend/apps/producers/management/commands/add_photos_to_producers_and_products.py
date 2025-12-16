"""
Command Django pour ajouter des photos aux exploitations et produits existants.
Usage: python manage.py add_photos_to_producers_and_products
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.producers.models import ProducerProfile, ProducerPhoto
from apps.products.models import Product, ProductPhoto
import requests
from io import BytesIO
from PIL import Image
from decimal import Decimal

# URLs d'images Unsplash pour différentes catégories
PRODUCER_PHOTOS_BY_CATEGORY = {
    'maraîchage': [
        'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1200',
        'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200',
        'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200',
        'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200',
    ],
    'fromagerie': [
        'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=1200',
        'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=1200',
        'https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=1200',
    ],
    'viticulture': [
        'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=1200',
        'https://images.unsplash.com/photo-1547595628-c61a29f496f0?w=1200',
        'https://images.unsplash.com/photo-1506377247307-5d4e725d6fd2?w=1200',
    ],
    'apiculture': [
        'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=1200',
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=1200',
        'https://images.unsplash.com/photo-1587049633312-d628ae50a8ae?w=1200',
    ],
    'boulangerie': [
        'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1200',
        'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=1200',
        'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1200',
    ],
    'élevage': [
        'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1200',
        'https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=1200',
        'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1200',
    ],
    'arboriculture': [
        'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=1200',
        'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=1200',
        'https://images.unsplash.com/photo-1517487881594-2787fef5ebf7?w=1200',
    ],
    'brasserie': [
        'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=1200',
        'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=1200',
        'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1200',
    ],
    'charcuterie': [
        'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=1200',
        'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=1200',
        'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=1200',
    ],
    'céréaliculture': [
        'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=1200',
        'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=1200',
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=1200',
    ],
    'pêche': [
        'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200',
        'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=1200',
    ],
    'default': [
        'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200',
        'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1200',
        'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200',
    ],
}

# URLs d'images pour différents types de produits
PRODUCT_PHOTOS_BY_NAME = {
    'pomme': ['https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=800', 'https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=800'],
    'tomate': ['https://images.unsplash.com/photo-1546470427-e26264be0b0e?w=800', 'https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=800'],
    'carotte': ['https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800', 'https://images.unsplash.com/photo-1598170845277-93ab61e37b7c?w=800'],
    'salade': ['https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=800', 'https://images.unsplash.com/photo-1610450949065-1bd846cc3ff7?w=800'],
    'pain': ['https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800', 'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=800'],
    'fromage': ['https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800', 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800'],
    'miel': ['https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800', 'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=800'],
    'vin': ['https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800', 'https://images.unsplash.com/photo-1547595628-c61a29f496f0?w=800'],
    'bière': ['https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800', 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800'],
    'légume': ['https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800', 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=800'],
    'fruits': ['https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=800', 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800'],
    'céréale': ['https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800', 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=800'],
    'default': ['https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800', 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800'],
}


def download_and_save_image(url, max_photos=3):
    """Télécharge une image depuis une URL et retourne les données."""
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Vérifier que c'est bien une image
        img = Image.open(BytesIO(response.content))
        
        # Convertir en RGB si nécessaire (pour JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Redimensionner si trop grand (max 1200px de largeur)
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        # Sauvegarder dans un BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85, optimize=True)
        img_io.seek(0)
        
        return img_io.read()
    except Exception as e:
        raise Exception(f"Erreur lors du téléchargement de {url}: {str(e)}")


class Command(BaseCommand):
    help = 'Ajoute des photos aux exploitations et produits existants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--producers-only',
            action='store_true',
            help='Ajouter des photos uniquement aux exploitations',
        )
        parser.add_argument(
            '--products-only',
            action='store_true',
            help='Ajouter des photos uniquement aux produits',
        )
        parser.add_argument(
            '--max-photos-producer',
            type=int,
            default=5,
            help='Nombre maximum de photos par exploitation (défaut: 5)',
        )
        parser.add_argument(
            '--max-photos-product',
            type=int,
            default=3,
            help='Nombre maximum de photos par produit (défaut: 3)',
        )

    def handle(self, *args, **options):
        producers_only = options.get('producers_only', False)
        products_only = options.get('products_only', False)
        max_photos_producer = options.get('max_photos_producer', 5)
        max_photos_product = options.get('max_photos_product', 3)
        
        # Ajouter des photos aux exploitations
        if not products_only:
            self.stdout.write('\n📸 Ajout de photos aux exploitations...')
            producers = ProducerProfile.objects.all()
            total_producers = producers.count()
            self.stdout.write(f'Trouvé {total_producers} exploitation(s)')
            
            for producer in producers:
                try:
                    current_photos = producer.photos.count()
                    if current_photos >= max_photos_producer:
                        self.stdout.write(
                            self.style.WARNING(f'  ⏭ {producer.name}: déjà {current_photos} photo(s) (max: {max_photos_producer})')
                        )
                        continue
                    
                    # Choisir les URLs de photos selon la catégorie
                    category = producer.category
                    photo_urls = PRODUCER_PHOTOS_BY_CATEGORY.get(category, PRODUCER_PHOTOS_BY_CATEGORY['default'])
                    
                    # Ajouter jusqu'à max_photos_producer photos
                    photos_to_add = max_photos_producer - current_photos
                    added_count = 0
                    
                    for i, photo_url in enumerate(photo_urls[:photos_to_add]):
                        try:
                            # Vérifier si la photo existe déjà (basé sur l'URL)
                            url_id = photo_url.split('/')[-2] if '/' in photo_url else str(i)
                            if ProducerPhoto.objects.filter(
                                producer=producer,
                                image_file__contains=url_id[:20]
                            ).exists():
                                continue
                            
                            # Télécharger et sauvegarder
                            img_data = download_and_save_image(photo_url)
                            filename = f"{producer.user.username}_photo_{current_photos + added_count + 1}.jpg"
                            
                            ProducerPhoto.objects.create(
                                producer=producer,
                                image_file=ContentFile(img_data, name=filename)
                            )
                            added_count += 1
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'    ⚠ Erreur photo {i+1}: {e}')
                            )
                    
                    if added_count > 0:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {producer.name}: {added_count} photo(s) ajoutée(s)')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ {producer.name}: aucune photo ajoutée')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Erreur pour {producer.name}: {e}')
                    )
        
        # Ajouter des photos aux produits
        if not producers_only:
            self.stdout.write('\n📸 Ajout de photos aux produits...')
            products = Product.objects.all()
            total_products = products.count()
            self.stdout.write(f'Trouvé {total_products} produit(s)')
            
            for product in products:
                try:
                    current_photos = product.photos.count()
                    if current_photos >= max_photos_product:
                        self.stdout.write(
                            self.style.WARNING(f'  ⏭ {product.name}: déjà {current_photos} photo(s) (max: {max_photos_product})')
                        )
                        continue
                    
                    # Chercher des URLs de photos selon le nom du produit
                    product_name_lower = product.name.lower()
                    photo_urls = None
                    
                    # Chercher une correspondance dans les mots-clés
                    for keyword, urls in PRODUCT_PHOTOS_BY_NAME.items():
                        if keyword in product_name_lower:
                            photo_urls = urls
                            break
                    
                    if not photo_urls:
                        photo_urls = PRODUCT_PHOTOS_BY_NAME['default']
                    
                    # Ajouter jusqu'à max_photos_product photos
                    photos_to_add = max_photos_product - current_photos
                    added_count = 0
                    
                    for i, photo_url in enumerate(photo_urls[:photos_to_add]):
                        try:
                            # Vérifier si la photo existe déjà
                            url_id = photo_url.split('/')[-2] if '/' in photo_url else str(i)
                            if ProductPhoto.objects.filter(
                                product=product,
                                image_file__contains=url_id[:20]
                            ).exists():
                                continue
                            
                            # Télécharger et sauvegarder
                            img_data = download_and_save_image(photo_url, max_photos_product)
                            filename = f"{product.producer.user.username}_{product.name.lower().replace(' ', '_')}_{current_photos + added_count + 1}.jpg"
                            # Nettoyer le filename des caractères spéciaux
                            filename = ''.join(c if c.isalnum() or c in '._-' else '_' for c in filename)[:100]
                            
                            ProductPhoto.objects.create(
                                product=product,
                                image_file=ContentFile(img_data, name=filename)
                            )
                            added_count += 1
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'    ⚠ Erreur photo {i+1} pour {product.name}: {e}')
                            )
                    
                    if added_count > 0:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {product.name}: {added_count} photo(s) ajoutée(s)')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ {product.name}: aucune photo ajoutée')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Erreur pour {product.name}: {e}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Terminé!'))





