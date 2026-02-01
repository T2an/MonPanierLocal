"""
Health check endpoints for monitoring.
"""
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Endpoint de santé basique.
    Retourne 200 si l'application est opérationnelle.
    """
    return JsonResponse({'status': 'healthy'})


def readiness_check(request):
    """
    Endpoint de disponibilité complet.
    Vérifie la connexion à la base de données et à Redis.
    """
    health = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
    }
    errors = []
    
    # Vérifier la base de données
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health['database'] = 'connected'
    except Exception as e:
        health['database'] = 'error'
        errors.append(f'Database: {str(e)}')
        logger.error(f'Database health check failed: {e}')
    
    # Vérifier Redis
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health['cache'] = 'connected'
        else:
            health['cache'] = 'error'
            errors.append('Cache: Unable to read/write')
    except Exception as e:
        health['cache'] = 'error'
        errors.append(f'Cache: {str(e)}')
        logger.error(f'Cache health check failed: {e}')
    
    # Déterminer le statut global
    if errors:
        health['status'] = 'unhealthy'
        health['errors'] = errors
        return JsonResponse(health, status=503)
    
    return JsonResponse(health)


@api_view(['GET'])
@permission_classes([AllowAny])
def cache_stats(request):
    """
    Endpoint pour récupérer les statistiques du cache Redis.
    """
    try:
        from apps.producers.cache import get_cache_stats
        stats = get_cache_stats()
        return Response({
            'status': 'ok',
            'cache': stats
        })
    except Exception as e:
        logger.error(f'Error getting cache stats: {e}')
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])  # En production, restreindre à IsAdminUser
def clear_cache(request):
    """
    Endpoint pour vider le cache.
    Note: En production, cet endpoint devrait être protégé.
    """
    try:
        from apps.producers.cache import invalidate_all_cache
        invalidate_all_cache()
        return Response({
            'status': 'ok',
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logger.error(f'Error clearing cache: {e}')
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=500)


