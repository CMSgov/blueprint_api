from django.http import Http404
from rest_framework.permissions import SAFE_METHODS

from blueprintapi.permissions import StrictDjangoObjectPermissions


class ProjectControlPermissions(StrictDjangoObjectPermissions):
    """Override StrictDjangoObjectPermissions to check required permissions based on the obj class instead of the view's
    queryset.
    This is specific to project control where ProjectControl object permissions should be effectively "inherited" based
    on a user's project permission.
    """
    def has_object_permission(self, request, view, obj):
        model_cls = obj.__class__
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not user.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False

        return True
