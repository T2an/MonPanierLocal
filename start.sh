#!/bin/bash
# Script de démarrage en production
# Lance toute l'application avec Docker Compose

set -e

echo "🚀 Démarrage de Mon Panier Local en mode production"
echo ""

# Vérifier que le .env existe
if [ ! -f ".env" ]; then
  echo "❌ Erreur: Le fichier .env n'existe pas à la racine du projet"
  echo "   Copiez .env.example vers .env et configurez vos variables"
  exit 1
fi

echo "✅ Fichier .env trouvé"
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
  echo "❌ Erreur: Docker n'est pas installé"
  echo "   Installez Docker pour continuer"
  exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
  echo "❌ Erreur: Docker Compose n'est pas installé"
  echo "   Installez Docker Compose pour continuer"
  exit 1
fi

echo "✅ Docker et Docker Compose détectés"
echo ""

# Lancer Docker Compose
echo "🐳 Démarrage des conteneurs..."
cd infra
# Utiliser --env-file pour charger le .env depuis la racine du projet
docker compose -f docker-compose.prod.yml --env-file ../.env up --build

echo ""
echo "✅ Application démarrée !"
echo ""
echo "🌐 URLs:"
echo "   - Application: http://localhost (port configurable via NGINX_HTTP_PORT dans .env)"
echo "   - API: http://localhost/api"
echo ""
echo "📋 Commandes utiles:"
echo "   - Voir les logs: cd infra && docker compose -f docker-compose.prod.yml --env-file ../.env logs -f"
echo "   - Arrêter: cd infra && docker compose -f docker-compose.prod.yml --env-file ../.env down"
echo "   - Redémarrer: cd infra && docker compose -f docker-compose.prod.yml --env-file ../.env restart"
echo ""