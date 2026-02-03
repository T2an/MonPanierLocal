"""
Commande Django pour créer 10 producteurs avec profils complets et photos téléchargées.
Usage: python manage.py add_10_complete_producers
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

# 10 exploitations complètes avec profils remplis
PRODUCERS_DATA = [
    {
        'name': 'Ferme Bio des Vallons',
        'category': 'maraîchage',
        'description': 'Exploitation maraîchère biologique certifiée AB depuis 2015. Légumes de saison, visites sur rendez-vous.',
        'address': '12 Route de la Vallée, 35320 Crevin, France',
        'latitude': 47.9450,
        'longitude': -1.6744,
        'phone': '02 99 45 67 89',
        'email_contact': 'contact@ferme-vallons-bio.fr',
        'website': 'https://www.ferme-vallons-bio.fr',
        'opening_hours': 'Mardi au Samedi: 9h-12h / 14h-18h. Dimanche: 9h-12h',
        'username': 'ferme_vallons_bio',
        'email': 'ferme.vallons.bio@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800',
            'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800',
            'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800',
        ],
        'products': [
            {'name': 'Tomates', 'description': 'Tomates anciennes bio', 'category': 'legumes', 'availability_type': 'custom', 'availability_start_month': 6, 'availability_end_month': 10, 'photos': ['https://images.unsplash.com/photo-1546470427-e26264be0b0e?w=600', 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600']},
            {'name': 'Salades', 'description': 'Salades variées', 'category': 'legumes', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=600']},
            {'name': 'Carottes', 'description': 'Carottes primeurs', 'category': 'legumes', 'availability_type': 'custom', 'availability_start_month': 5, 'availability_end_month': 3, 'photos': ['https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Vente à la ferme', 'instructions': 'Paiement CB ou espèces.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 6, 'is_closed': False, 'opening': '09:00', 'closing': '12:00'},
            ], 'order': 0},
            {'mode_type': 'phone_order', 'title': 'Commande téléphone', 'instructions': 'Appelez 24h à l\'avance.', 'phone_number': '02 99 45 67 89', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 6, 'is_closed': False, 'opening': '09:00', 'closing': '12:00'},
            ], 'order': 1},
        ],
    },
    {
        'name': 'Fromagerie du Mont Blanc',
        'category': 'fromagerie',
        'description': 'Artisan fromager, fromages de chèvre et brebis. Dégustation et vente directe.',
        'address': '45 Chemin des Alpages, 74400 Chamonix-Mont-Blanc, France',
        'latitude': 45.9237,
        'longitude': 6.8694,
        'phone': '04 50 53 00 45',
        'email_contact': 'bonjour@fromagerie-montblanc.fr',
        'website': 'https://www.fromagerie-montblanc.fr',
        'opening_hours': 'Lundi au Vendredi: 10h-18h. Samedi: 9h-19h',
        'username': 'fromagerie_montblanc',
        'email': 'fromagerie.montblanc@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800',
            'https://images.unsplash.com/photo-1618164436268-8c72e7390280?w=800',
            'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800',
        ],
        'products': [
            {'name': 'Tomme de chèvre', 'description': 'Fromage de chèvre affiné', 'category': 'autre', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=600']},
            {'name': 'Fromage frais', 'description': 'Fromage blanc fermier', 'category': 'autre', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Vente à la fromagerie', 'instructions': 'Dégustation gratuite.', 'opening_hours': [
                {'day': 0, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 1, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 2, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 3, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 4, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Vignoble de Provence',
        'category': 'viticulture',
        'description': 'Domaine viticole familial, vins bio. Rosé, rouge, blanc. Dégustation sur place.',
        'address': 'Route de Gordes, 84220 Gordes, France',
        'latitude': 43.9117,
        'longitude': 5.2006,
        'phone': '04 90 72 02 75',
        'email_contact': 'accueil@vignoble-provence.fr',
        'website': 'https://www.vignoble-provence.fr',
        'opening_hours': 'Tous les jours: 10h-18h (sauf dimanche matin)',
        'username': 'vignoble_provence',
        'email': 'vignoble.provence@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800',
            'https://images.unsplash.com/photo-1537640538966-79f369143a8f?w=800',
            'https://images.unsplash.com/photo-1547595628-c61a29f496f0?w=800',
        ],
        'products': [
            {'name': 'Rosé Côtes de Provence', 'description': 'Vin rosé bio', 'category': 'autre', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600']},
            {'name': 'Rouge AOC', 'description': 'Vin rouge domaine', 'category': 'autre', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1547595628-c61a29f496f0?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Cave et dégustation', 'instructions': 'Dégustation offerte.', 'opening_hours': [
                {'day': 0, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 1, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 2, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 3, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 4, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 6, 'is_closed': False, 'opening': '14:00', 'closing': '18:00'},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Ruchers de la Forêt',
        'category': 'apiculture',
        'description': 'Apiculteur passionné depuis 20 ans. Miels variés (acacia, tilleul, châtaignier).',
        'address': 'Hameau des Ruches, 59190 Hazebrouck, France',
        'latitude': 50.7250,
        'longitude': 2.5378,
        'phone': '03 28 49 12 34',
        'email_contact': 'contact@ruchers-foret.fr',
        'website': '',
        'opening_hours': 'Mercredi et Samedi: 14h-18h. Sur RDV autres jours',
        'username': 'ruchers_foret',
        'email': 'ruchers.foret@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800',
            'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=800',
            'https://images.unsplash.com/photo-1587049633312-d628ae50a8ae?w=800',
        ],
        'products': [
            {'name': 'Miel d\'acacia', 'description': 'Miel doux et clair', 'category': 'miel', 'availability_type': 'custom', 'availability_start_month': 5, 'availability_end_month': 7, 'photos': ['https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600']},
            {'name': 'Miel de tilleul', 'description': 'Miel floral', 'category': 'miel', 'availability_type': 'custom', 'availability_start_month': 6, 'availability_end_month': 8, 'photos': ['https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Vente au rucher', 'instructions': 'Mercredi et Samedi après-midi.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': True}, {'day': 2, 'is_closed': False, 'opening': '14:00', 'closing': '18:00'}, {'day': 3, 'is_closed': True}, {'day': 4, 'is_closed': True}, {'day': 5, 'is_closed': False, 'opening': '14:00', 'closing': '18:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Boulangerie Artisanale Le Pain Bio',
        'category': 'boulangerie',
        'description': 'Boulangerie artisanale, farines bio locales. Pain au levain, pâtisseries maison.',
        'address': '8 Place du Marché, 69001 Lyon, France',
        'latitude': 45.7640,
        'longitude': 4.8357,
        'phone': '04 78 29 15 67',
        'email_contact': 'bonjour@pain-bio-lyon.fr',
        'website': '',
        'opening_hours': 'Mardi au Dimanche: 7h-19h. Fermé lundi',
        'username': 'pain_bio_lyon',
        'email': 'pain.bio.lyon@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
            'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=800',
            'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800',
        ],
        'products': [
            {'name': 'Pain au levain', 'description': 'Pain bio au levain naturel', 'category': 'pain', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600']},
            {'name': 'Baguette tradition', 'description': 'Baguette au levain', 'category': 'pain', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Boulangerie', 'instructions': 'Ouvert tôt le matin.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'}, {'day': 2, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'}, {'day': 3, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'}, {'day': 4, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'}, {'day': 5, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'}, {'day': 6, 'is_closed': False, 'opening': '07:00', 'closing': '19:00'},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Élevage Bio des Collines',
        'category': 'élevage',
        'description': 'Élevage porcs et volailles plein air, alimentation 100% bio. Viande fraîche, charcuterie.',
        'address': '47 Route des Collines, 63120 Courpière, France',
        'latitude': 45.7547,
        'longitude': 3.5397,
        'phone': '04 73 51 23 45',
        'email_contact': 'info@elevage-collines-bio.fr',
        'website': 'https://www.elevage-collines-bio.fr',
        'opening_hours': 'Vendredi: 16h-19h. Samedi: 9h-12h / 14h-18h',
        'username': 'elevage_collines',
        'email': 'elevage.collines@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=800',
            'https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=800',
            'https://images.unsplash.com/photo-1546445317-29f4545e9d53?w=800',
        ],
        'products': [
            {'name': 'Côtes de porc', 'description': 'Porc élevé en plein air', 'category': 'viande', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=600']},
            {'name': 'Saucisson sec élevage', 'description': 'Charcuterie artisanale', 'category': 'viande', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Vente à la ferme', 'instructions': 'Vendredi et Samedi.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': True}, {'day': 2, 'is_closed': True}, {'day': 3, 'is_closed': True}, {'day': 4, 'is_closed': False, 'opening': '16:00', 'closing': '19:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '18:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Verger du Val de Loire',
        'category': 'arboriculture',
        'description': 'Pommes, poires, cerises en agriculture raisonnée. Cueillette libre juillet-octobre.',
        'address': '123 Chemin du Verger, 37150 Chenonceaux, France',
        'latitude': 47.3294,
        'longitude': 1.0694,
        'phone': '02 47 23 98 76',
        'email_contact': 'contact@verger-val-loire.fr',
        'website': '',
        'opening_hours': 'Mars à Oct: 10h-18h. Nov-Fév: sur RDV',
        'username': 'verger_val_loire',
        'email': 'verger.val.loire@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=800',
            'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800',
            'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=800',
        ],
        'products': [
            {'name': 'Pommes Golden', 'description': 'Pommes à couteau', 'category': 'fruits', 'availability_type': 'custom', 'availability_start_month': 8, 'availability_end_month': 4, 'photos': ['https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600']},
            {'name': 'Poires', 'description': 'Poires Williams et Conférence', 'category': 'fruits', 'availability_type': 'custom', 'availability_start_month': 8, 'availability_end_month': 11, 'photos': ['https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Cueillette et vente', 'instructions': 'Apportez vos contenants.', 'opening_hours': [
                {'day': 0, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 1, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 2, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 3, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 4, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 6, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Brasserie Artisanale du Nord',
        'category': 'brasserie',
        'description': 'Brasserie artisanale créée en 2018. Bières bio aux saveurs locales.',
        'address': '56 Rue de la Brasserie, 59000 Lille, France',
        'latitude': 50.6292,
        'longitude': 3.0573,
        'phone': '03 20 45 67 89',
        'email_contact': 'contact@brasserie-nord.fr',
        'website': 'https://www.brasserie-nord.fr',
        'opening_hours': 'Jeudi et Vendredi: 14h-19h. Samedi: 10h-18h',
        'username': 'brasserie_nord',
        'email': 'brasserie.nord@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800',
            'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800',
            'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=800',
        ],
        'products': [
            {'name': 'Bière blonde', 'description': 'Bière blonde houblonnée', 'category': 'biere', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600']},
            {'name': 'Bière ambrée', 'description': 'Bière ambrée maltée', 'category': 'biere', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Dégustation brasserie', 'instructions': 'Visite sur rendez-vous.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': True}, {'day': 2, 'is_closed': True}, {'day': 3, 'is_closed': False, 'opening': '14:00', 'closing': '19:00'}, {'day': 4, 'is_closed': False, 'opening': '14:00', 'closing': '19:00'}, {'day': 5, 'is_closed': False, 'opening': '10:00', 'closing': '18:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Charcuterie des Cévennes',
        'category': 'charcuterie',
        'description': 'Charcutier-traiteur artisanal. Saucissons, jambons, pâtés. Élevage et transformation à la ferme.',
        'address': '89 Route des Cévennes, 30170 Saint-Hippolyte-du-Fort, France',
        'latitude': 44.0450,
        'longitude': 3.8561,
        'phone': '04 66 77 12 34',
        'email_contact': 'info@charcuterie-cevennes.fr',
        'website': '',
        'opening_hours': 'Mardi au Samedi: 9h-12h30 / 15h-19h',
        'username': 'charcuterie_cevennes',
        'email': 'charcuterie.cevennes@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=800',
            'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800',
            'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800',
        ],
        'products': [
            {'name': 'Saucisson sec', 'description': 'Saucisson artisanal', 'category': 'viande', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=600']},
            {'name': 'Jambon sec', 'description': 'Jambon affiné 18 mois', 'category': 'viande', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Boutique', 'instructions': 'Paiement CB accepté.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 2, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 3, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 4, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '19:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
    {
        'name': 'Ferme Céréalière des Plaines',
        'category': 'céréaliculture',
        'description': 'Exploitation céréalière bio. Farines, flocons et céréales en vrac. Transformation à la ferme.',
        'address': '234 Route de la Plaine, 02400 Château-Thierry, France',
        'latitude': 49.0406,
        'longitude': 3.4017,
        'phone': '03 23 83 45 67',
        'email_contact': 'contact@ferme-plaines.fr',
        'website': 'https://www.ferme-plaines.fr',
        'opening_hours': 'Vendredi: 14h-18h. Samedi: 9h-12h',
        'username': 'ferme_plaines',
        'email': 'ferme.plaines@example.com',
        'producer_photos': [
            'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800',
            'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=800',
            'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800',
        ],
        'products': [
            {'name': 'Farine de blé T80', 'description': 'Farine bio meulée à la ferme', 'category': 'cereales', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=600']},
            {'name': 'Flocons d\'avoine', 'description': 'Avoine bio en flocons', 'category': 'cereales', 'availability_type': 'all_year', 'photos': ['https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600']},
        ],
        'sale_modes': [
            {'mode_type': 'on_site', 'title': 'Vente à la ferme', 'instructions': 'Vendredi et Samedi.', 'opening_hours': [
                {'day': 0, 'is_closed': True}, {'day': 1, 'is_closed': True}, {'day': 2, 'is_closed': True}, {'day': 3, 'is_closed': True}, {'day': 4, 'is_closed': False, 'opening': '14:00', 'closing': '18:00'}, {'day': 5, 'is_closed': False, 'opening': '09:00', 'closing': '12:00'}, {'day': 6, 'is_closed': True},
            ], 'order': 0},
        ],
    },
]


def download_image(url, timeout=15):
    """Télécharge une image depuis une URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85, optimize=True)
        img_io.seek(0)
        return img_io
    except Exception as e:
        raise Exception(f"Erreur téléchargement {url}: {e}")


def get_or_create_category(name):
    """Retourne la catégorie produit par nom (legumes, fromage, etc.)."""
    defaults = {'icon': 'tag', 'display_name': name.capitalize(), 'order': 0}
    cat, _ = ProductCategory.objects.get_or_create(name=name, defaults=defaults)
    return cat


class Command(BaseCommand):
    help = 'Crée 10 producteurs avec profils complets et photos téléchargées'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Supprime les producteurs @example.com existants avant')
        parser.add_argument('--skip-photos', action='store_true', help='Ne pas télécharger les photos (création rapide)')

    def handle(self, *args, **options):
        if options['clear']:
            deleted = User.objects.filter(email__endswith='@example.com').delete()
            self.stdout.write(self.style.WARNING(f'Supprimé {deleted[0]} utilisateur(s) @example.com'))
        skip_photos = options.get('skip_photos', False)
        if skip_photos:
            self.stdout.write(self.style.WARNING('Mode --skip-photos: pas de téléchargement d\'images'))

        self.stdout.write(self.style.SUCCESS('\nCreation de 10 producteurs complets\n'))

        category_map = {cat.name: cat for cat in ProductCategory.objects.all()}
        created_count = 0

        for data in PRODUCERS_DATA:
            try:
                with transaction.atomic():
                    user, _ = User.objects.get_or_create(
                        email=data['email'],
                        defaults={'username': data['username'], 'is_producer': True, 'is_active': True}
                    )
                    if not user.password or not user.check_password('demo123456'):
                        user.set_password('demo123456')
                        user.save()

                    lat = round(Decimal(str(data['latitude'])), 7)
                    lng = round(Decimal(str(data['longitude'])), 7)
                    producer, created = ProducerProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'name': data['name'], 'category': data['category'], 'description': data['description'],
                            'address': data['address'], 'latitude': lat, 'longitude': lng,
                            'phone': data.get('phone', ''), 'email_contact': data.get('email_contact', ''),
                            'website': data.get('website', ''), 'opening_hours': data.get('opening_hours', ''),
                        }
                    )
                    if not created:
                        producer.name = data['name']
                        producer.category = data['category']
                        producer.description = data['description']
                        producer.address = data['address']
                        producer.latitude = lat
                        producer.longitude = lng
                        producer.phone = data.get('phone', '')
                        producer.email_contact = data.get('email_contact', '')
                        producer.website = data.get('website', '')
                        producer.opening_hours = data.get('opening_hours', '')
                        producer.save()

                    # Photos exploitation (ne pas dupliquer si déjà présentes)
                    photo_count = producer.photos.count()
                    if not skip_photos and photo_count < len(data.get('producer_photos', [])):
                        for i, url in enumerate(data.get('producer_photos', []), 1):
                            if photo_count >= len(data['producer_photos']):
                                break
                            try:
                                img_io = download_image(url)
                                fname = f"{data['username']}_photo_{photo_count + 1}.jpg"
                                ProducerPhoto.objects.create(
                                    producer=producer,
                                    image_file=ContentFile(img_io.read(), name=fname)
                                )
                                photo_count += 1
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f'  Photo {i} {data["name"]}: {e}'))

                    # Produits
                    for pdata in data.get('products', []):
                        cat_name = pdata.get('category', 'legumes')
                        cat = category_map.get(cat_name) or get_or_create_category(cat_name)
                        product, _ = Product.objects.get_or_create(
                            producer=producer, name=pdata['name'],
                            defaults={
                                'description': pdata.get('description', ''),
                                'category': cat,
                                'availability_type': pdata.get('availability_type', 'all_year'),
                                'availability_start_month': pdata.get('availability_start_month'),
                                'availability_end_month': pdata.get('availability_end_month'),
                            }
                        )
                        if not skip_photos and product.photos.count() < len(pdata.get('photos', [])):
                            for j, url in enumerate(pdata.get('photos', []), 1):
                                if product.photos.count() >= len(pdata['photos']):
                                    break
                                try:
                                    img_io = download_image(url)
                                    fname = f"{data['username']}_{pdata['name'][:20].replace(' ', '_')}_{j}.jpg"
                                    fname = ''.join(c if c.isalnum() or c in '._-' else '_' for c in fname)[:80]
                                    ProductPhoto.objects.create(
                                        product=product,
                                        image_file=ContentFile(img_io.read(), name=fname)
                                    )
                                except Exception:
                                    pass

                    # Modes de vente
                    SaleMode.objects.filter(producer=producer).delete()
                    for sm in data.get('sale_modes', []):
                        sm_obj = SaleMode.objects.create(
                            producer=producer,
                            mode_type=sm['mode_type'],
                            title=sm['title'],
                            instructions=sm['instructions'],
                            phone_number=sm.get('phone_number', ''),
                            order=sm.get('order', 0),
                        )
                        for h in sm.get('opening_hours', []):
                            OpeningHours.objects.create(
                                sale_mode=sm_obj,
                                day_of_week=h['day'],
                                is_closed=h.get('is_closed', False),
                                opening_time=time.fromisoformat(h['opening']) if not h.get('is_closed') and 'opening' in h else None,
                                closing_time=time.fromisoformat(h['closing']) if not h.get('is_closed') and 'closing' in h else None,
                            )

                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'OK {data["name"]} ({photo_count} photos exploitation)'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'ERREUR {data["name"]}: {e}'))
                import traceback
                traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} producteur(s) crees'))
        self.stdout.write('Identifiants: email @example.com, mot de passe: demo123456')
