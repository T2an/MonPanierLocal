from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProducerProfileViewSet, SaleModeViewSet

router = DefaultRouter()
router.register(r'', ProducerProfileViewSet, basename='producer')
router.register(r'(?P<producer_id>\d+)/sale-modes', SaleModeViewSet, basename='producer-sale-mode')

urlpatterns = [
    path('', include(router.urls)),
    path('nearby/', ProducerProfileViewSet.as_view({'get': 'nearby'}), name='producer-nearby'),
]

