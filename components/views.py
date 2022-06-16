from rest_framework import generics

from .models import Component
from .serializers import ComponentSerializer


# Use for read-write endpoints to represent a collection of model instances.
# Provides get and post method handlers.
class ComponentListView(generics.ListCreateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


# Use for read or update endpoints to represent a single model instance.
# Provides get, put, and patch method handlers.
class ComponentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
