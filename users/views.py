from rest_framework import generics

from blueprintapi.filters import ObjectPermissionsFilter
from users.models import User
from users.permissions import UserPermissions
from users.serializers import UserSerializer


# Use for read-write endpoints to represent a collection of model instances.
# Provides get and post method handlers.
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions, ]
    filter_backends = [ObjectPermissionsFilter, ]


# Use for read or update endpoints to represent a single model instance.
# Provides get, put, and patch method handlers.
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
