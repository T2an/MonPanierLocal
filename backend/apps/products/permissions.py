from rest_framework import permissions


class IsProductOwner(permissions.BasePermission):
    """Permission pour vérifier que l'utilisateur est propriétaire du producteur du produit."""
    def has_object_permission(self, request, view, obj):
        return obj.producer.user == request.user

