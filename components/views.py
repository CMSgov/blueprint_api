from rest_framework import generics
from rest_framework.response import Response

from .models import Component
from .serializers import ComponentListSerializer, ComponentSerializer


# Use for read-write endpoints to represent a collection of model instances.
# Provides get and post method handlers.
class ComponentListView(generics.ListCreateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ComponentListSerializer(queryset, many=True)
        return Response(serializer.data)


# Use for read or update endpoints to represent a single model instance.
# Provides get, put, and patch method handlers.
class ComponentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
