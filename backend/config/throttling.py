"""
Custom throttling classes using Redis cache.
"""
from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import caches


class RedisThrottleMixin:
    """Mixin pour utiliser le cache Redis pour le throttling."""
    cache = caches['ratelimit']


class RedisAnonRateThrottle(RedisThrottleMixin, SimpleRateThrottle):
    """Rate throttle pour les utilisateurs anonymes avec Redis."""
    scope = 'anon'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None  # Ne pas throttle les utilisateurs authentifiés
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class RedisUserRateThrottle(RedisThrottleMixin, SimpleRateThrottle):
    """Rate throttle pour les utilisateurs authentifiés avec Redis."""
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class RedisBurstAnonRateThrottle(RedisThrottleMixin, SimpleRateThrottle):
    """Throttle burst pour les utilisateurs anonymes (protection contre les pics)."""
    scope = 'burst_anon'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class RedisBurstUserRateThrottle(RedisThrottleMixin, SimpleRateThrottle):
    """Throttle burst pour les utilisateurs authentifiés (protection contre les pics)."""
    scope = 'burst_user'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


