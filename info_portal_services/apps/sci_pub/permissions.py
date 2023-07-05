from rest_framework.permissions import BasePermission 


class IsSciPubOwnerOrStaff(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_groups = [g.name for g in request.user.groups.all()]
        return (obj.created_by == request.user) or \
               ("app-moderator" in user_groups or "app-admin" in user_groups)