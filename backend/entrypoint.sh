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

# Appliquer les migrations
echo "📦 Application des migrations..."
runuser -u appuser -- python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
runuser -u appuser -- python manage.py collectstatic --noinput || true

echo "✅ Backend prêt"

# Exécuter la commande passée en argument (gunicorn) en tant qu'appuser
exec runuser -u appuser -- "$@"

