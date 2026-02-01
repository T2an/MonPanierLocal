"""
Cache service for producers using Redis.
"""
import logging
import hashlib
from functools import wraps
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Durées de cache par type de données
CACHE_DURATIONS = {
    'producers_list': 300,      # 5 minutes
    'producers_nearby': 300,    # 5 minutes
    'producer_detail': 600,     # 10 minutes
    'categories_list': 3600,    # 1 heure
}


def get_cache_key(prefix: str, **kwargs) -> str:
    """
    Génère une clé de cache unique basée sur le préfixe et les paramètres.
    """
    # Créer une représentation triée des kwargs pour la cohérence
    params = ':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()) if v is not None)
    if params:
        # Hash pour les clés longues
        if len(params) > 100:
            params = hashlib.md5(params.encode()).hexdigest()
        return f'{prefix}:{params}'
    return prefix


def cache_response(prefix: str, timeout: int = None):
    """
    Décorateur pour cacher les réponses des vues.
    
    Args:
        prefix: Préfixe de la clé de cache
        timeout: Durée en secondes (utilise CACHE_DURATIONS si None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Construire la clé de cache
            cache_params = {
                'page': request.query_params.get('page', '1'),
                'category': request.query_params.get('category', ''),
                'search': request.query_params.get('search', ''),
                'ordering': request.query_params.get('ordering', ''),
            }
            
            # Ajouter les paramètres spécifiques à l'action
            if kwargs:
                cache_params.update(kwargs)
            
            cache_key = get_cache_key(prefix, **cache_params)
            cache_timeout = timeout or CACHE_DURATIONS.get(prefix, settings.CACHE_TTL)
            
            # Essayer de récupérer depuis le cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f'Cache HIT for {cache_key}')
                return cached_response
            
            logger.debug(f'Cache MISS for {cache_key}')
            
            # Exécuter la fonction et cacher le résultat
            response = func(self, request, *args, **kwargs)
            
            # Ne cacher que les réponses réussies
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache.set(cache_key, response, cache_timeout)
                logger.debug(f'Cached response for {cache_key} (TTL: {cache_timeout}s)')
            
            return response
        return wrapper
    return decorator


def cache_nearby_response(timeout: int = None):
    """
    Décorateur spécifique pour cacher les réponses nearby avec coordonnées arrondies.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Arrondir les coordonnées pour augmenter les hits de cache
            lat = request.query_params.get('latitude', '')
            lng = request.query_params.get('longitude', '')
            radius = request.query_params.get('radius_km', '50')
            
            if lat and lng:
                try:
                    # Arrondir à 2 décimales (~1km de précision)
                    lat_rounded = round(float(lat), 2)
                    lng_rounded = round(float(lng), 2)
                except (ValueError, TypeError):
                    lat_rounded = lat
                    lng_rounded = lng
            else:
                lat_rounded = lat
                lng_rounded = lng
            
            cache_params = {
                'lat': lat_rounded,
                'lng': lng_rounded,
                'radius': radius,
                'page': request.query_params.get('page', '1'),
            }
            
            cache_key = get_cache_key('producers_nearby', **cache_params)
            cache_timeout = timeout or CACHE_DURATIONS.get('producers_nearby', 300)
            
            # Essayer de récupérer depuis le cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f'Cache HIT for nearby: {cache_key}')
                return cached_response
            
            logger.debug(f'Cache MISS for nearby: {cache_key}')
            
            # Exécuter la fonction et cacher le résultat
            response = func(self, request, *args, **kwargs)
            
            # Ne cacher que les réponses réussies
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache.set(cache_key, response, cache_timeout)
                logger.debug(f'Cached nearby response for {cache_key} (TTL: {cache_timeout}s)')
            
            return response
        return wrapper
    return decorator


def invalidate_producer_cache(producer_id: int = None):
    """
    Invalide le cache lié aux producteurs.
    
    Args:
        producer_id: ID du producteur à invalider (None pour tout invalider)
    """
    try:
        if producer_id:
            # Invalider le détail du producteur
            cache.delete(get_cache_key('producer_detail', id=producer_id))
            logger.info(f'Invalidated cache for producer {producer_id}')
        
        # Invalider les listes (utiliser un pattern si Redis le supporte)
        # Note: django-redis supporte delete_pattern
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('mpl:producers_list:*')
            cache.delete_pattern('mpl:producers_nearby:*')
            logger.info('Invalidated all producers list cache')
        else:
            # Fallback: invalider les clés connues
            cache.delete('producers_list')
            logger.info('Invalidated producers list cache (fallback)')
            
    except Exception as e:
        logger.error(f'Error invalidating producer cache: {e}')


def invalidate_all_cache():
    """Invalide tout le cache."""
    try:
        cache.clear()
        logger.info('Cleared all cache')
    except Exception as e:
        logger.error(f'Error clearing cache: {e}')


def get_cache_stats():
    """Récupère les statistiques du cache Redis."""
    try:
        client = cache.client.get_client()
        info = client.info()
        return {
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 'N/A'),
            'total_keys': client.dbsize(),
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': round(
                info.get('keyspace_hits', 0) / 
                max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 
                2
            ),
        }
    except Exception as e:
        logger.error(f'Error getting cache stats: {e}')
        return {'error': str(e)}


