# Tests unitaires - Mon Panier Local

## Lancer les tests

Depuis la racine du projet backend :

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

Ou avec Python :

```bash
cd backend
python -m pytest tests/ -v
```

## Liste des tests

### Auth (`test_auth_api.py`)
- **Login** : succès, mauvais mot de passe, utilisateur inconnu, champs manquants
- **Register** : succès, email existant, mots de passe différents, mot de passe court
- **Me** : profil authentifié, non authentifié, modification
- **Change password** : succès, ancien mot de passe incorrect, non authentifié
- **Token refresh** : rafraîchissement du token

### Producers (`test_producers_api.py`)
- **Liste** : accès public, filtre catégorie, recherche
- **Nearby** : recherche par position, paramètres manquants
- **Détail** : accès public
- **Création** : authentifié, non authentifié

### Products (`test_products_api.py`)
- **Catégories** : liste publique
- **Produits** : liste publique
- **Produits par producteur** : accès public
- **Création** : propriétaire authentifié, non authentifié

### Photos (`test_photos_api.py`)
- **Accès public** : photos producteur/produit visibles sans auth, photo_count dans la liste
- **Producteur** : peut ajouter et supprimer ses photos exploitation
- **Sécurité** : autre utilisateur ne peut pas supprimer, non-auth rejeté
- **Produits** : producteur peut ajouter et supprimer photos de ses produits

## Configuration

Les tests utilisent :
- SQLite (pas de PostgreSQL)
- DummyCache (pas de Redis)
- `testserver` dans ALLOWED_HOSTS
