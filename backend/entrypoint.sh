#!/bin/bash
set -e

echo "🚀 Démarrage du backend Django..."

# Créer les dossiers media nécessaires avec les bonnes permissions
echo "📁 Création des dossiers media..."
mkdir -p /app/media/producers /app/media/products
chown -R appuser:appuser /app/media
chmod -R 755 /app/media

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
until runuser -u appuser -- python manage.py shell -c "from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
  echo "   Base de données non disponible, attente..."
  sleep 2
done
echo "✅ Base de données disponible"

# Attendre que Redis soit prêt
echo "⏳ Attente de Redis..."
REDIS_HOST="${REDIS_URL:-redis://redis:6379/0}"
# Extraire le host de l'URL Redis
REDIS_HOST_ONLY=$(echo $REDIS_HOST | sed -E 's/redis:\/\/([^:\/]+).*/\1/')
REDIS_PORT=$(echo $REDIS_HOST | sed -E 's/.*:([0-9]+).*/\1/')
REDIS_PORT=${REDIS_PORT:-6379}

until runuser -u appuser -- python -c "
import redis
import os
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
r = redis.from_url(redis_url)
r.ping()
print('Redis OK')
" 2>/dev/null; do
  echo "   Redis non disponible, attente..."
  sleep 2
done
echo "✅ Redis disponible"

# Appliquer les migrations
echo "📦 Application des migrations..."
runuser -u appuser -- python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
runuser -u appuser -- python manage.py collectstatic --noinput || true

# Vérification finale de la santé
echo "🔍 Vérification de la santé du système..."
runuser -u appuser -- python manage.py shell -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.core.cache import cache
from django.db import connection

# Test DB
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Base de données: OK')
except Exception as e:
    print(f'❌ Base de données: {e}')
    sys.exit(1)

# Test Cache (non bloquant)
try:
    cache.set('startup_check', 'ok', 10)
    if cache.get('startup_check') != 'ok':
        raise AssertionError('Cache read failed')
    print('✅ Cache Redis: OK')
except Exception as e:
    print(f'⚠️ Cache Redis: {e} (le backend démarre quand même)')
" || echo "⚠️ Vérification de santé échouée, le backend démarre quand même"

echo "✅ Backend prêt"

# Exécuter la commande passée en argument (gunicorn) en tant qu'appuser
exec runuser -u appuser -- "$@"

