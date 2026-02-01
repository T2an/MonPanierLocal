# 🚀 Guide de Production

Ce guide explique comment déployer l'application en production.

## 📋 Prérequis

- **Docker** et Docker Compose installés
- **Domaine** configuré (optionnel mais recommandé)
- **Certificat SSL** (pour HTTPS, recommandé)

## 🔧 Configuration

### 1. Variables d'Environnement

Créez un fichier `.env` à la racine du projet ou dans le dossier `infra/` :

```env
# Base de données
DB_NAME=monpanierlocal
DB_USER=postgres
DB_PASSWORD=CHANGEZ_MOI_AVEC_UN_MOT_DE_PASSE_FORT
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=GÉNÉREZ_UNE_CLÉ_SECRÈTE_ALÉATOIRE_ET_LONGUE
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# API URL (pour le frontend)
API_URL=https://votre-domaine.com/api

# Ports (plage autorisée : 3500-3600)
NGINX_HTTP_PORT=3500
# NGINX_HTTPS_PORT=3501
```

**⚠️ IMPORTANT** : Ne commitez jamais le fichier `.env` dans Git !

### 2. Générer une Clé Secrète Django

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Configuration SSL (Optionnel mais Recommandé)

Si vous avez des certificats SSL :

```bash
# Créer le dossier ssl dans infra/nginx/
mkdir -p infra/nginx/ssl

# Copier vos certificats
cp votre-cert.pem infra/nginx/ssl/cert.pem
cp votre-key.pem infra/nginx/ssl/key.pem
```

Puis décommentez la section HTTPS dans `infra/nginx/nginx.conf`.

## 🚀 Déploiement

### 1. Construire et Lancer les Conteneurs

```bash
cd infra
docker-compose -f docker-compose.prod.yml up -d --build
```

### 2. Initialiser la Base de Données

```bash
# Accéder au conteneur backend
docker exec -it monpanierlocal_backend_prod bash

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### 3. Vérifier le Déploiement

> **Note** : Les services utilisent par défaut le port 3500 (configurable via `NGINX_HTTP_PORT` dans `.env`).

- Frontend : `http://votre-domaine.com:3500` (ou `http://localhost:3500` si pas de domaine)
- Backend API : `http://votre-domaine.com:3500/api/`
- Admin Django : `http://votre-domaine.com:3500/admin/`

## 🔒 Sécurité

### Checklist de Sécurité

- [ ] `DEBUG=False` dans les variables d'environnement
- [ ] `SECRET_KEY` forte et unique
- [ ] `DB_PASSWORD` fort
- [ ] HTTPS configuré (SSL/TLS)
- [ ] `ALLOWED_HOSTS` correctement configuré
- [ ] Firewall configuré sur le serveur
- [ ] Backups réguliers de la base de données
- [ ] Mots de passe des utilisateurs admin forts

### Recommandations

1. **Backups** : Configurez des backups automatiques de PostgreSQL
2. **Monitoring** : Utilisez des outils comme Prometheus/Grafana
3. **Logs** : Centralisez les logs avec ELK Stack ou similaire
4. **Rate Limiting** : Ajoutez du rate limiting sur l'API (ex: django-ratelimit)
5. **CORS** : Restreignez les origines CORS en production

## 📊 Monitoring

### Vérifier les Logs

```bash
# Logs de tous les services
docker-compose -f infra/docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker-compose -f infra/docker-compose.prod.yml logs -f backend
docker-compose -f infra/docker-compose.prod.yml logs -f frontend
docker-compose -f infra/docker-compose.prod.yml logs -f nginx
```

### Vérifier l'État des Conteneurs

```bash
docker-compose -f infra/docker-compose.prod.yml ps
```

## 🔄 Mises à Jour

### 1. Arrêter les Services

```bash
docker-compose -f infra/docker-compose.prod.yml down
```

### 2. Mettre à Jour le Code

```bash
git pull origin main  # ou votre branche
```

### 3. Reconstruire et Redémarrer

```bash
docker-compose -f infra/docker-compose.prod.yml up -d --build
```

### 4. Appliquer les Migrations (si nécessaire)

```bash
docker exec -it monpanierlocal_backend_prod python manage.py migrate
```

## 💾 Backups

### Backup de la Base de Données

```bash
# Créer un backup
docker exec monpanierlocal_db_prod pg_dump -U postgres monpanierlocal > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer un backup
cat backup_20240101_120000.sql | docker exec -i monpanierlocal_db_prod psql -U postgres monpanierlocal
```

### Backup des Médias

```bash
# Créer un backup des médias
docker cp monpanierlocal_backend_prod:/app/media ./backup_media_$(date +%Y%m%d_%H%M%S)

# Restaurer les médias
docker cp ./backup_media_20240101_120000/. monpanierlocal_backend_prod:/app/media/
```

## 🐛 Dépannage

### Le Frontend ne se charge pas

1. Vérifiez les logs : `docker-compose -f infra/docker-compose.prod.yml logs frontend`
2. Vérifiez que `NEXT_PUBLIC_API_URL` est correctement configuré
3. Vérifiez que le backend est accessible

### Le Backend ne répond pas

1. Vérifiez les logs : `docker-compose -f infra/docker-compose.prod.yml logs backend`
2. Vérifiez la connexion à la base de données
3. Vérifiez les variables d'environnement

### Erreurs 502 Bad Gateway

1. Vérifiez que tous les services sont démarrés
2. Vérifiez la configuration Nginx
3. Vérifiez les logs Nginx

### Problèmes de Permissions

```bash
# Corriger les permissions des médias
docker exec monpanierlocal_backend_prod chown -R www-data:www-data /app/media
docker exec monpanierlocal_backend_prod chmod -R 755 /app/media
```

## 📈 Optimisations

### Performance

1. **Cache** : Configurez Redis pour le cache Django
2. **CDN** : Utilisez un CDN pour les fichiers statiques
3. **Compression** : Nginx gzip est déjà configuré
4. **Base de données** : Configurez des index sur les champs fréquemment recherchés

### Scalabilité

1. **Load Balancer** : Ajoutez un load balancer devant Nginx
2. **Multiple Workers** : Ajustez le nombre de workers Gunicorn
3. **Database Replication** : Configurez la réplication PostgreSQL pour la lecture

## 🔗 Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Next.js](https://nextjs.org/docs)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation Nginx](https://nginx.org/en/docs/)

