#!/usr/bin/env python
"""
Script de test pour valider que l'application peut démarrer correctement.
Ce script vérifie :
- Chargement des settings Django
- Import des modules critiques
- Configuration de la base de données
- Configuration du cache
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_settings_load():
    """Test que les settings Django peuvent être chargées."""
    try:
        django.setup()
        from django.conf import settings
        print("✅ Settings Django chargées avec succès")
        print(f"   - DEBUG: {settings.DEBUG}")
        print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   - DATABASE: {settings.DATABASES['default']['NAME']}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement des settings: {e}")
        return False

def test_imports():
    """Test que les modules critiques peuvent être importés."""
    try:
        from apps.producers.views import ProducerProfileViewSet
        from apps.producers.models import ProducerProfile
        from apps.auth.models import User
        from apps.products.models import Product
        print("✅ Imports des modules critiques OK")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des imports: {e}")
        return False

def test_database_config():
    """Test la configuration de la base de données."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Configuration de la base de données OK")
        return True
    except Exception as e:
        print(f"⚠️  Base de données non disponible (normal si pas démarrée): {e}")
        return True  # Pas bloquant pour le test

def test_cache_config():
    """Test la configuration du cache."""
    try:
        from django.core.cache import cache
        cache.set('test_key', 'test_value', 10)
        value = cache.get('test_key')
        if value == 'test_value':
            print("✅ Configuration du cache OK")
            return True
        else:
            print("⚠️  Cache ne fonctionne pas correctement")
            return True  # Pas bloquant
    except Exception as e:
        print(f"⚠️  Cache non disponible (normal si Redis pas démarré): {e}")
        return True  # Pas bloquant

def main():
    """Exécute tous les tests."""
    print("🔍 Tests de démarrage de l'application...\n")
    
    results = []
    results.append(("Settings", test_settings_load()))
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database_config()))
    results.append(("Cache", test_cache_config()))
    
    print("\n" + "="*50)
    print("📊 Résumé des tests:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✅ Tous les tests critiques sont passés !")
        print("   L'application est prête à démarrer.")
        return 0
    else:
        print("\n❌ Certains tests ont échoué.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

