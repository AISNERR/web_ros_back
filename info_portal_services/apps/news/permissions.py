from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import PubReviews


class IsOwnerAndReadOnly(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, PubReviews) and request.method in SAFE_METHODS:
            return obj.publication.created_by == request.user
        return False


class NewsDetailsPermissions(BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            user_groups = [g.name for g in request.user.groups.all()]
        except AttributeError:
            user_groups = []

        if "app-admin" in user_groups:
            return True
        elif "app-moderator" in user_groups and request.method in SAFE_METHODS:
            return True
        elif (obj.status.status == 'published' and request.method in SAFE_METHODS) or \
                (obj.status.status == 'created' and obj.created_by == request.user) or \
                (obj.created_by == request.user and request.method in SAFE_METHODS):
            return True

        return False
