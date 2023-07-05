from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAppModerator(BasePermission):

    def has_permission(self, request, view):
        user_groups = [g.name for g in request.user.groups.all()]
        return "app-moderator" in user_groups

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAppModeratorOrAdmin(BasePermission):

    def has_permission(self, request, view):
        user_groups = [g.name for g in request.user.groups.all()]
        return "app-moderator" in user_groups or "app-admin" in user_groups

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAppAdmin(BasePermission):

    def has_permission(self, request, view):
        return "app-admin" in [g.name for g in request.user.groups.all()]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsObjectOwnerOrAppAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.created_by == request.user) or ("app-admin" in [g.name for g in request.user.groups.all()])


class IsAppAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return "app-admin" in [g.name for g in request.user.groups.all()] or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
