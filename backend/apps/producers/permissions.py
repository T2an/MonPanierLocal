docfrom rest_framework import permissions


class IsProducerOwner(permissions.BasePermission):
    """Permission pour vérifier que l'utilisateur est propriétaire du profil producteur."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

