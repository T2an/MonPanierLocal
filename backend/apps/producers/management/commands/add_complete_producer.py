"""
Command Django pour créer une exploitation complète avec produits, calendrier, modes de vente et photos.
Usage: python manage.py add_complete_producer
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from decimal import Decimal
from datetime import time
import requests
from io import BytesIO
from PIL import Image

from apps.producers.models import ProducerProfile, ProducerPhoto, SaleMode, OpeningHours
from apps.products.models import Product, ProductCategory, ProductPhoto

User = get_user_model()


# Données d'une exploitation complète
COMPLETE_PRODUCER = {
    'name': 'Ferme Bio des Jardins de Bretagne',
    'category': 'maraîchage',
    'description': '''Exploitation maraîchère biologique certifiée AB depuis 2018, située au cœur de la Bretagne.
    
Nous cultivons une large gamme de légumes de saison sur 5 hectares, en respectant les cycles naturels et la biodiversité. Notre production est certifiée Agriculture Biologique et nous privilégions les variétés anciennes et locales.

Notre ferme propose :
- Des légumes de saison frais et locaux
- Des paniers hebdomadaires sur abonnement
- La vente directe à la ferme
- Des visites pédagogiques sur rendez-vous
- Des ateliers de jardinage bio

Nous sommes engagés dans une démarche éco-responsable : compostage, rotation des cultures, lutte biologique, et réduction des emballages. Rejoignez-nous pour découvrir le goût authentique des légumes cultivés avec passion !''',
    'address': 'Route de la Ferme, 22300 Lannion, Bretagne, France',
    'latitude': 48.7318,
    'longitude': -3.4590,
    'phone': '02 96 45 78 90',
    'email_contact': 'contact@jardins-bretagne-bio.fr',
    'website': 'https://www.jardins-bretagne-bio.fr',
    'opening_hours': 'Mardi au Samedi: 9h-12h30 / 14h-18h30. Dimanche: 10h-13h. Fermé le lundi.',
    'username': 'jardins_bretagne_bio',
    'email': 'jardins.bretagne.bio@example.com',
    
    # Photos de l'exploitation (Unsplash - URLs valides)
    'producer_photos': [
        'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1200&q=80',
        'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80',
        'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=1200&q=80',
        'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=1200&q=80',
        'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80',
    ],
    
    # Produits avec leurs périodes de disponibilité
    'products': [
        {
            'name': 'Tomates',
            'description': 'Tomates anciennes et variétés modernes, cultivées sous serre et en plein champ. Goût authentique et saveurs variées.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 6,  # Juin
            'availability_end_month': 10,   # Octobre
            'photos': [
                'https://images.unsplash.com/photo-1592841200221-0a5c8b5e5b5e?w=800&q=80',
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
        {
            'name': 'Salades',
            'description': 'Salades variées (laitue, roquette, mâche, mesclun) cultivées toute l\'année sous serre et en plein champ.',
            'category': 'legumes',
            'availability_type': 'all_year',
            'availability_start_month': None,
            'availability_end_month': None,
            'photos': [
                'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=800&q=80',
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
        {
            'name': 'Carottes',
            'description': 'Carottes primeurs et de conservation, sucrées et croquantes. Variétés colorées (orange, jaune, violette).',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 5,  # Mai
            'availability_end_month': 3,    # Mars (année suivante)
            'photos': [
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
                'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=800&q=80',
            ],
        },
        {
            'name': 'Courgettes',
            'description': 'Courgettes fraîches, récoltées quotidiennement en saison. Idéales pour ratatouille, gratins et légumes farcis.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 6,  # Juin
            'availability_end_month': 9,    # Septembre
            'photos': [
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
        {
            'name': 'Pommes de terre',
            'description': 'Pommes de terre de variétés anciennes et modernes. Primeurs en juin, de conservation jusqu\'au printemps.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 6,  # Juin
            'availability_end_month': 4,    # Avril (année suivante)
            'photos': [
                'https://images.unsplash.com/photo-1518977822534-7049a61ee0c2?w=800&q=80',
            ],
        },
        {
            'name': 'Haricots verts',
            'description': 'Haricots verts extra-fins, récoltés à la main. Frais et croquants, parfaits pour vos plats d\'été.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 7,  # Juillet
            'availability_end_month': 9,    # Septembre
            'photos': [
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
        {
            'name': 'Choux',
            'description': 'Choux variés (chou-fleur, brocoli, chou vert, chou rouge) selon les saisons. Riches en vitamines.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 9,  # Septembre
            'availability_end_month': 4,    # Avril (année suivante)
            'photos': [
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
        {
            'name': 'Épinards',
            'description': 'Épinards frais, tendres et savoureux. Récoltés jeunes pour une saveur délicate.',
            'category': 'legumes',
            'availability_type': 'custom',
            'availability_start_month': 3,  # Mars
            'availability_end_month': 6,    # Juin
            'photos': [
                'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=800&q=80',
            ],
        },
    ],
    
    # Modes de vente avec horaires
    'sale_modes': [
        {
            'mode_type': 'on_site',
            'title': 'Vente à la ferme',
            'instructions': 'Bienvenue à la ferme ! Merci de respecter les horaires d\'ouverture. Paiement en espèces ou carte bancaire accepté.',
            'opening_hours': [
                {'day': 0, 'is_closed': True},  # Lundi fermé
                {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '18:30'},  # Mardi
                {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '18:30'},  # Mercredi
                {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '18:30'},  # Jeudi
                {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '18:30'},  # Vendredi
                {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:30'},  # Samedi
                {'day': 6, 'is_closed': False, 'opening': '10:00', 'closing': '13:00'},  # Dimanche
            ],
            'order': 0,
        },
        {
            'mode_type': 'phone_order',
            'title': 'Commande par téléphone',
            'instructions': 'Appelez-nous au moins 24h à l\'avance pour passer votre commande. Retrait à la ferme aux horaires d\'ouverture.',
            'phone_number': '02 96 45 78 90',
            'opening_hours': [
                {'day': 0, 'is_closed': True},  # Lundi
                {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Mardi
                {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Mercredi
                {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Jeudi
                {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Vendredi
                {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Samedi
                {'day': 6, 'is_closed': False, 'opening': '10:00', 'closing': '13:00'},  # Dimanche
            ],
            'order': 1,
        },
        {
            'mode_type': 'market',
            'title': 'Marché de Lannion',
            'instructions': 'Retrouvez-nous chaque samedi matin au marché de Lannion, place du Centre. Stand n°12.',
            'market_info': 'Samedi: 8h-13h, Place du Centre, Lannion',
            'opening_hours': [
                {'day': 0, 'is_closed': True},  # Lundi
                {'day': 1, 'is_closed': True},  # Mardi
                {'day': 2, 'is_closed': True},  # Mercredi
                {'day': 3, 'is_closed': True},  # Jeudi
                {'day': 4, 'is_closed': True},  # Vendredi
                {'day': 5, 'is_closed': False, 'opening': '08:00', 'closing': '13:00'},  # Samedi
                {'day': 6, 'is_closed': True},  # Dimanche
            ],
            'order': 2,
        },
        {
            'mode_type': 'delivery',
            'title': 'Livraison à domicile',
            'instructions': 'Livraison gratuite pour les commandes de plus de 30€ dans un rayon de 15km. Commandes par email ou téléphone.',
            'website_url': 'https://www.jardins-bretagne-bio.fr/commandes',
            'opening_hours': [
                {'day': 0, 'is_closed': True},  # Lundi
                {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Mardi
                {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Mercredi
                {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Jeudi
                {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Vendredi
                {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'},  # Samedi
                {'day': 6, 'is_closed': True},  # Dimanche
            ],
            'order': 3,
        },
    ],
}


def download_image(url, timeout=15):
    """Télécharge une image depuis une URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        response.raise_for_status()
        
        # Vérifier que c'est bien une image
        img = Image.open(BytesIO(response.content))
        
        # Convertir en RGB si nécessaire
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        
        # Sauvegarder dans un BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85, optimize=True)
        img_io.seek(0)
        
        return img_io
    except Exception as e:
        raise Exception(f"Erreur lors du téléchargement de l'image {url}: {e}")


class Command(BaseCommand):
    help = 'Crée une exploitation complète avec produits, calendrier, modes de vente et photos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Met à jour l\'exploitation si elle existe déjà',
        )

    def handle(self, *args, **options):
        data = COMPLETE_PRODUCER
        
        self.stdout.write(self.style.SUCCESS('\n🌾 Création d\'une exploitation complète 🌾\n'))
        
        try:
            with transaction.atomic():
                # 1. Créer ou récupérer l'utilisateur
                self.stdout.write('👤 Création de l\'utilisateur...')
                user, user_created = User.objects.get_or_create(
                    email=data['email'],
                    defaults={
                        'username': data['username'],
                        'is_producer': True,
                        'is_active': True,
                    }
                )
                
                if not user_created and not options['update']:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Utilisateur {data["email"]} existe déjà. Utilisez --update pour mettre à jour.')
                    )
                    return
                
                if user_created:
                    user.set_password('demo123456')  # Mot de passe par défaut pour la démo
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Utilisateur créé: {data["email"]}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Utilisateur existant: {data["email"]}'))
                
                # 2. Créer ou mettre à jour le profil producteur
                self.stdout.write('\n🏡 Création du profil producteur...')
                latitude = round(Decimal(str(data['latitude'])), 7)
                longitude = round(Decimal(str(data['longitude'])), 7)
                
                producer, producer_created = ProducerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': data['name'],
                        'category': data['category'],
                        'description': data['description'],
                        'address': data['address'],
                        'latitude': latitude,
                        'longitude': longitude,
                        'phone': data['phone'],
                        'email_contact': data['email_contact'],
                        'website': data['website'],
                        'opening_hours': data['opening_hours'],
                    }
                )
                
                if not producer_created:
                    if options['update']:
                        producer.name = data['name']
                        producer.category = data['category']
                        producer.description = data['description']
                        producer.address = data['address']
                        producer.latitude = latitude
                        producer.longitude = longitude
                        producer.phone = data['phone']
                        producer.email_contact = data['email_contact']
                        producer.website = data['website']
                        producer.opening_hours = data['opening_hours']
                        producer.save()
                        self.stdout.write(self.style.SUCCESS(f'✅ Profil mis à jour: {data["name"]}'))
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Profil {data["name"]} existe déjà. Utilisez --update pour mettre à jour.')
                        )
                        return
                else:
                    self.stdout.write(self.style.SUCCESS(f'✅ Profil créé: {data["name"]}'))
                
                # 3. Ajouter les photos de l'exploitation
                self.stdout.write('\n📸 Téléchargement des photos de l\'exploitation...')
                photo_count = 0
                for i, photo_url in enumerate(data['producer_photos'], 1):
                    try:
                        # Vérifier si la photo existe déjà
                        if ProducerPhoto.objects.filter(
                            producer=producer,
                            image_file__icontains=f'{data["username"]}_{i}'
                        ).exists():
                            self.stdout.write(f'  ⏭️  Photo {i} existe déjà, ignorée')
                            continue
                        
                        img_io = download_image(photo_url)
                        filename = f'{data["username"]}_photo_{i}.jpg'
                        
                        photo = ProducerPhoto.objects.create(
                            producer=producer,
                            image_file=ContentFile(img_io.read(), name=filename)
                        )
                        photo_count += 1
                        self.stdout.write(f'  ✅ Photo {i} téléchargée')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  Erreur photo {i}: {e}')
                        )
                
                self.stdout.write(self.style.SUCCESS(f'✅ {photo_count} photo(s) de l\'exploitation ajoutée(s)'))
                
                # 4. Créer les produits avec leurs périodes de disponibilité
                self.stdout.write('\n🥕 Création des produits...')
                
                # Récupérer ou créer les catégories de produits
                category_map = {}
                for cat in ProductCategory.objects.all():
                    category_map[cat.name] = cat
                
                product_count = 0
                for product_data in data['products']:
                    try:
                        category = category_map.get(product_data['category'])
                        
                        product, created = Product.objects.get_or_create(
                            producer=producer,
                            name=product_data['name'],
                            defaults={
                                'description': product_data['description'],
                                'category': category,
                                'availability_type': product_data['availability_type'],
                                'availability_start_month': product_data.get('availability_start_month'),
                                'availability_end_month': product_data.get('availability_end_month'),
                            }
                        )
                        
                        if not created and options['update']:
                            product.description = product_data['description']
                            product.category = category
                            product.availability_type = product_data['availability_type']
                            product.availability_start_month = product_data.get('availability_start_month')
                            product.availability_end_month = product_data.get('availability_end_month')
                            product.save()
                        
                        # Ajouter les photos du produit
                        for j, photo_url in enumerate(product_data.get('photos', []), 1):
                            try:
                                if ProductPhoto.objects.filter(
                                    product=product,
                                    image_file__icontains=f'{product.name.lower().replace(" ", "_")}_{j}'
                                ).exists():
                                    continue
                                
                                img_io = download_image(photo_url)
                                filename = f'{product.name.lower().replace(" ", "_")}_{j}.jpg'
                                
                                ProductPhoto.objects.create(
                                    product=product,
                                    image_file=ContentFile(img_io.read(), name=filename)
                                )
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(f'    ⚠️  Erreur photo produit {product.name}: {e}')
                                )
                        
                        product_count += 1
                        period = 'Toute l\'année' if product_data['availability_type'] == 'all_year' else \
                                 f"{self._get_month_name(product_data.get('availability_start_month'))} à {self._get_month_name(product_data.get('availability_end_month'))}"
                        self.stdout.write(f'  ✅ {product.name} - {period}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Erreur produit {product_data["name"]}: {e}')
                        )
                
                self.stdout.write(self.style.SUCCESS(f'✅ {product_count} produit(s) créé(s)'))
                
                # 5. Créer les modes de vente avec horaires
                self.stdout.write('\n🏪 Création des modes de vente...')
                
                # Supprimer les anciens modes de vente si update
                if options['update']:
                    SaleMode.objects.filter(producer=producer).delete()
                
                sale_mode_count = 0
                for sale_mode_data in data['sale_modes']:
                    try:
                        sale_mode = SaleMode.objects.create(
                            producer=producer,
                            mode_type=sale_mode_data['mode_type'],
                            title=sale_mode_data['title'],
                            instructions=sale_mode_data['instructions'],
                            phone_number=sale_mode_data.get('phone_number', ''),
                            website_url=sale_mode_data.get('website_url', ''),
                            is_24_7=sale_mode_data.get('is_24_7', False),
                            market_info=sale_mode_data.get('market_info', ''),
                            order=sale_mode_data.get('order', 0),
                        )
                        
                        # Créer les horaires d'ouverture
                        for hour_data in sale_mode_data.get('opening_hours', []):
                            OpeningHours.objects.create(
                                sale_mode=sale_mode,
                                day_of_week=hour_data['day'],
                                is_closed=hour_data.get('is_closed', False),
                                opening_time=time.fromisoformat(hour_data['opening']) if not hour_data.get('is_closed') and 'opening' in hour_data else None,
                                closing_time=time.fromisoformat(hour_data['closing']) if not hour_data.get('is_closed') and 'closing' in hour_data else None,
                            )
                        
                        sale_mode_count += 1
                        self.stdout.write(f'  ✅ {sale_mode.title} ({sale_mode.get_mode_type_display()})')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Erreur mode de vente {sale_mode_data["title"]}: {e}')
                        )
                        import traceback
                        traceback.print_exc()
                
                self.stdout.write(self.style.SUCCESS(f'✅ {sale_mode_count} mode(s) de vente créé(s)'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Erreur lors de la création: {e}')
            )
            import traceback
            traceback.print_exc()
            raise
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ EXPLOITATION COMPLÈTE CRÉÉE AVEC SUCCÈS !'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📧 Email: {data["email"]}')
        self.stdout.write(f'🔑 Mot de passe: demo123456')
        self.stdout.write(f'🌐 URL: http://localhost:3500/producers/{producer.id}/')
        self.stdout.write(f'\n📊 Résumé:')
        self.stdout.write(f'   - {photo_count} photo(s) de l\'exploitation')
        self.stdout.write(f'   - {product_count} produit(s) avec calendrier de production')
        self.stdout.write(f'   - {sale_mode_count} mode(s) de vente avec horaires')
        self.stdout.write('\n')

    def _get_month_name(self, month_num):
        """Retourne le nom du mois."""
        months = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        return months.get(month_num, '') if month_num else ''

