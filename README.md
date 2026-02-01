# 🌱 Mon Panier Local

Application web pour découvrir et contacter les producteurs locaux.

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose

### Configuration

1. **Copiez le fichier d'exemple des variables d'environnement :**
```bash
cp .env.example .env
```

2. **Éditez le fichier `.env` à la racine** et configurez vos variables :
   - `SECRET_KEY` : Générez une clé secrète Django (voir ci-dessous)
   - `DB_PASSWORD` : Choisissez un mot de passe fort pour PostgreSQL
   - `DEBUG=False` : Pour la production
   - `ALLOWED_HOSTS` : Ajoutez votre domaine

**Générer une clé secrète Django :**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Lancement

**Une seule commande pour démarrer toute l'application :**

```bash
./start.sh
```

L'application sera accessible sur `http://localhost:3500` (port configurable via `NGINX_HTTP_PORT` dans `.env`, plage autorisée : 3500-3600).

### Commandes utiles

```bash
# Voir les logs
docker compose -f infra/docker-compose.prod.yml logs -f

# Arrêter les conteneurs
docker compose -f infra/docker-compose.prod.yml down

# Redémarrer les conteneurs
docker compose -f infra/docker-compose.prod.yml restart

# Accéder au conteneur backend
docker exec -it monpanierlocal_backend_prod bash

# Créer un superutilisateur Django
docker exec -it monpanierlocal_backend_prod python manage.py createsuperuser

# Appliquer les migrations
docker exec -it monpanierlocal_backend_prod python manage.py migrate
```

### Note importante

Toutes les variables d'environnement sont centralisées dans le fichier `.env` à la racine du projet. Ce fichier est utilisé par Docker Compose pour configurer tous les services (base de données, backend, frontend, nginx).

## 📚 Documentation

- [Documentation Production](docs/PRODUCTION.md)

## 🛠️ Stack Technique

- **Backend**: Django + Django REST Framework, PostgreSQL
- **Frontend**: Next.js 14, React, TailwindCSS, Leaflet
- **Infrastructure**: Docker, Nginx

## 📝 Licence

Propriétaire
