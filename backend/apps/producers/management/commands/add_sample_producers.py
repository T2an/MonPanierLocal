"""
Command Django pour ajouter des exploitations d'exemple avec photos.
Usage: python manage.py add_sample_producers
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from apps.producers.models import ProducerProfile, ProducerPhoto
import requests
from io import BytesIO
from PIL import Image
import random

User = get_user_model()


# Données des exploitations fictives
EXPLOITATIONS = [
    {
        'name': 'Ferme Bio des Vallons',
        'category': 'maraîchage',
        'description': 'Exploitation maraîchère biologique certifiée depuis 2015. Nous produisons une large gamme de légumes de saison dans le respect de l\'environnement. Visite de la ferme possible sur rendez-vous.',
        'address': '12 Route de la Vallée, 35320 Crevin, France',
        'latitude': 47.9450,
        'longitude': -1.6744,
        'phone': '02 99 45 67 89',
        'email_contact': 'contact@ferme-vallons-bio.fr',
        'website': 'https://www.ferme-vallons-bio.fr',
        'opening_hours': 'Mardi au Samedi: 9h-12h / 14h-18h. Dimanche matin: 9h-12h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800',
            'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800',
        ],
        'username': 'ferme_vallons_bio',
        'email': 'ferme.vallons.bio@example.com',
    },
    {
        'name': 'Fromagerie du Mont Blanc',
        'category': 'fromagerie',
        'description': 'Artisan fromager spécialisé dans les fromages de chèvre et de brebis. Élevage en plein air, transformation à la ferme. Dégustation et vente directe.',
        'address': '45 Chemin des Alpages, 74400 Chamonix-Mont-Blanc, France',
        'latitude': 45.9237,
        'longitude': 6.8694,
        'phone': '04 50 53 00 45',
        'email_contact': 'bonjour@fromagerie-montblanc.fr',
        'website': 'https://www.fromagerie-montblanc.fr',
        'opening_hours': 'Lundi au Vendredi: 10h-18h. Samedi: 9h-19h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800',
            'https://images.unsplash.com/photo-1618164436268-8c72e7390280?w=800',
        ],
        'username': 'fromagerie_montblanc',
        'email': 'fromagerie.montblanc@example.com',
    },
    {
        'name': 'Vignoble de Provence',
        'category': 'viticulture',
        'description': 'Domaine viticole familial produisant des vins bio depuis 3 générations. Rosé, rouge et blanc. Dégustation sur place et commande en ligne.',
        'address': 'Route de Gordes, 84220 Gordes, France',
        'latitude': 43.9117,
        'longitude': 5.2006,
        'phone': '04 90 72 02 75',
        'email_contact': 'accueil@vignoble-provence.fr',
        'website': 'https://www.vignoble-provence.fr',
        'opening_hours': 'Tous les jours: 10h-18h (sauf dimanche matin)',
        'photo_urls': [
            'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800',
            'https://images.unsplash.com/photo-1537640538966-79f369143a8f?w=800',
        ],
        'username': 'vignoble_provence',
        'email': 'vignoble.provence@example.com',
    },
    {
        'name': 'Ruchers de la Forêt',
        'category': 'apiculture',
        'description': 'Apiculteur passionné depuis 20 ans. Production de miels variés (acacia, tilleul, châtaignier, forêt). Vente directe et livraison possible.',
        'address': 'Hameau des Ruches, 59190 Hazebrouck, France',
        'latitude': 50.7250,
        'longitude': 2.5378,
        'phone': '03 28 49 12 34',
        'email_contact': 'contact@ruchers-foret.fr',
        'website': '',
        'opening_hours': 'Mercredi et Samedi: 14h-18h. Sur rendez-vous les autres jours',
        'photo_urls': [
            'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800',
            'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=800',
        ],
        'username': 'ruchers_foret',
        'email': 'ruchers.foret@example.com',
    },
    {
        'name': 'Boulangerie Artisanale Le Pain Bio',
        'category': 'boulangerie',
        'description': 'Boulangerie artisanale utilisant uniquement des farines bio locales. Pain au levain naturel, pâtisseries maison. Ouvert tous les matins.',
        'address': '8 Place du Marché, 69001 Lyon, France',
        'latitude': 45.7640,
        'longitude': 4.8357,
        'phone': '04 78 29 15 67',
        'email_contact': 'bonjour@pain-bio-lyon.fr',
        'website': '',
        'opening_hours': 'Mardi au Dimanche: 7h-19h. Fermé le lundi',
        'photo_urls': [
            'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
            'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=800',
        ],
        'username': 'pain_bio_lyon',
        'email': 'pain.bio.lyon@example.com',
    },
    {
        'name': 'Élevage Bio des Collines',
        'category': 'élevage',
        'description': 'Élevage de porcs et volailles en plein air, alimentation 100% bio. Vente de viande fraîche, charcuterie artisanale. Visite de la ferme possible.',
        'address': '47 Route des Collines, 63120 Courpière, France',
        'latitude': 45.7547,
        'longitude': 3.5397,
        'phone': '04 73 51 23 45',
        'email_contact': 'info@elevage-collines-bio.fr',
        'website': 'https://www.elevage-collines-bio.fr',
        'opening_hours': 'Vendredi: 16h-19h. Samedi: 9h-12h / 14h-18h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=800',
            'https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=800',
        ],
        'username': 'elevage_collines',
        'email': 'elevage.collines@example.com',
    },
    {
        'name': 'Verger du Val de Loire',
        'category': 'arboriculture',
        'description': 'Production de pommes, poires et cerises en agriculture raisonnée. Cueillette libre possible de juillet à octobre. Pressage de jus de pomme.',
        'address': '123 Chemin du Verger, 37150 Chenonceaux, France',
        'latitude': 47.3294,
        'longitude': 1.0694,
        'phone': '02 47 23 98 76',
        'email_contact': 'contact@verger-val-loire.fr',
        'website': '',
        'opening_hours': 'Mars à Octobre: Tous les jours 10h-18h. Novembre à Février: Sur rendez-vous',
        'photo_urls': [
            'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=800',
            'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800',
        ],
        'username': 'verger_val_loire',
        'email': 'verger.val.loire@example.com',
    },
    {
        'name': 'Brasserie Artisanale du Nord',
        'category': 'brasserie',
        'description': 'Brasserie artisanale créée en 2018. Bières bio aux saveurs locales (houblon, épices). Visite de la brasserie et dégustation sur rendez-vous.',
        'address': '56 Rue de la Brasserie, 59000 Lille, France',
        'latitude': 50.6292,
        'longitude': 3.0573,
        'phone': '03 20 45 67 89',
        'email_contact': 'contact@brasserie-nord.fr',
        'website': 'https://www.brasserie-nord.fr',
        'opening_hours': 'Jeudi et Vendredi: 14h-19h. Samedi: 10h-18h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800',
            'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800',
        ],
        'username': 'brasserie_nord',
        'email': 'brasserie.nord@example.com',
    },
    {
        'name': 'Charcuterie des Cévennes',
        'category': 'charcuterie',
        'description': 'Charcutier-traiteur artisanal spécialisé dans les produits du porc. Saucissons, jambons, pâtés. Élevage et transformation à la ferme.',
        'address': '89 Route des Cévennes, 30170 Saint-Hippolyte-du-Fort, France',
        'latitude': 44.0450,
        'longitude': 3.8561,
        'phone': '04 66 77 12 34',
        'email_contact': 'info@charcuterie-cevennes.fr',
        'website': '',
        'opening_hours': 'Mardi au Samedi: 9h-12h30 / 15h-19h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=800',
            'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800',
        ],
        'username': 'charcuterie_cevennes',
        'email': 'charcuterie.cevennes@example.com',
    },
    {
        'name': 'Ferme Céréalière des Plaines',
        'category': 'céréaliculture',
        'description': 'Exploitation céréalière bio (blé, orge, avoine). Vente de farines, flocons et céréales en vrac. Transformation à la ferme.',
        'address': '234 Route de la Plaine, 02400 Château-Thierry, France',
        'latitude': 49.0406,
        'longitude': 3.4017,
        'phone': '03 23 83 45 67',
        'email_contact': 'contact@ferme-plaines.fr',
        'website': 'https://www.ferme-plaines.fr',
        'opening_hours': 'Vendredi: 14h-18h. Samedi: 9h-12h',
        'photo_urls': [
            'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800',
            'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=800',
        ],
        'username': 'ferme_plaines',
        'email': 'ferme.plaines@example.com',
    },
]


class Command(BaseCommand):
    help = 'Ajoute des exploitations d\'exemple avec photos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime les exploitations d\'exemple existantes avant d\'en créer de nouvelles',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Suppression des exploitations d\'exemple existantes...')
            User.objects.filter(
                email__endswith='@example.com'
            ).exclude(
                email__in=[exp['email'] for exp in EXPLOITATIONS]
            ).delete()

        self.stdout.write(f'Ajout de {len(EXPLOITATIONS)} exploitations...')
        
        created_count = 0
        for exp_data in EXPLOITATIONS:
            try:
                with transaction.atomic():
                    # Créer ou récupérer l'utilisateur
                    user, created = User.objects.get_or_create(
                        email=exp_data['email'],
                        defaults={
                            'username': exp_data['username'],
                            'is_producer': True,
                            'is_active': True,
                        }
                    )
                    
                    if not created:
                        self.stdout.write(
                            self.style.WARNING(f'Utilisateur {exp_data["email"]} existe déjà')
                        )

                    # Arrondir les coordonnées à 7 décimales maximum
                    from decimal import Decimal
                    latitude = round(Decimal(str(exp_data['latitude'])), 7)
                    longitude = round(Decimal(str(exp_data['longitude'])), 7)
                    
                    # Créer ou mettre à jour le profil producteur
                    producer, producer_created = ProducerProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'name': exp_data['name'],
                            'category': exp_data['category'],
                            'description': exp_data['description'],
                            'address': exp_data['address'],
                            'latitude': latitude,
                            'longitude': longitude,
                            'phone': exp_data.get('phone', ''),
                            'email_contact': exp_data.get('email_contact', ''),
                            'website': exp_data.get('website', ''),
                            'opening_hours': exp_data.get('opening_hours', ''),
                        }
                    )
                    
                    if not producer_created:
                        # Mettre à jour si déjà existant
                        producer.name = exp_data['name']
                        producer.category = exp_data['category']
                        producer.description = exp_data['description']
                        producer.address = exp_data['address']
                        producer.latitude = latitude
                        producer.longitude = longitude
                        producer.phone = exp_data.get('phone', '')
                        producer.email_contact = exp_data.get('email_contact', '')
                        producer.website = exp_data.get('website', '')
                        producer.opening_hours = exp_data.get('opening_hours', '')
                        producer.save()
                        self.stdout.write(
                            self.style.WARNING(f'Profil {exp_data["name"]} mis à jour')
                        )

                    # Ajouter les photos
                    photo_count = 0
                    for photo_url in exp_data.get('photo_urls', []):
                        try:
                            # Vérifier si la photo existe déjà
                            if ProducerPhoto.objects.filter(
                                producer=producer,
                                image_file__contains=photo_url.split('/')[-1][:20]
                            ).exists():
                                continue

                            # Télécharger l'image
                            response = requests.get(photo_url, timeout=10)
                            response.raise_for_status()
                            
                            # Vérifier que c'est bien une image
                            img = Image.open(BytesIO(response.content))
                            
                            # Convertir en RGB si nécessaire (pour JPEG)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            
                            # Sauvegarder dans un BytesIO
                            img_io = BytesIO()
                            img.save(img_io, format='JPEG', quality=85)
                            img_io.seek(0)
                            
                            # Créer la photo
                            filename = f"{exp_data['username']}_{photo_count + 1}.jpg"
                            photo = ProducerPhoto.objects.create(
                                producer=producer,
                                image_file=ContentFile(img_io.read(), name=filename)
                            )
                            photo_count += 1
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Erreur lors du téléchargement de la photo {photo_url} pour {exp_data["name"]}: {e}'
                                )
                            )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {exp_data["name"]} créé avec {photo_count} photo(s)'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Erreur lors de la création de {exp_data["name"]}: {e}'
                    )
                )
                import traceback
                traceback.print_exc()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {created_count} exploitation(s) ajoutée(s) avec succès!'
            )
        )

