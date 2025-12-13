from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductCategoryViewSet, ProductPhotoViewSet

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='product-category')
router.register(r'photos', ProductPhotoViewSet, basename='product-photo')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]

