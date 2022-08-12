from blueprintapi.permissions import StrictDjangoObjectPermissions


SAFE_METHODS = ("POST", )


class UserPermissions(StrictDjangoObjectPermissions):
    """Permissions class that allows POST operations for the User view."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)
