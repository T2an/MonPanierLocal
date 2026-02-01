"""
URL configuration for MonPanierLocal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.producers.views import ProducerPhotoViewSet
from rest_framework.routers import DefaultRouter
from .health import health_check, readiness_check, cache_stats, clear_cache

router = DefaultRouter()
router.register(r'photos', ProducerPhotoViewSet, basename='photo')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.auth.urls')),
    path('api/producers/', include('apps.producers.urls')),
    path('api/producers/<int:producer_id>/products/', include('apps.products.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/', include(router.urls)),
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('api/cache/stats/', cache_stats, name='cache_stats'),
    path('api/cache/clear/', clear_cache, name='clear_cache'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Mon Panier Local - Administration'
admin.site.site_title = 'Mon Panier Local Admin'
admin.site.index_title = 'Gestion des producteurs locaux'

