from pathlib import Path

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from .catalogio import CatalogTools as Tools
from .models import Catalog
from .serializers import CatalogListSerializer


class CatalogListView(generics.ListAPIView):
    """Use for read-write endpoints to represent a collection of model instances.
    Provides get and post method handlers.
    """
    queryset = Catalog.objects.all().order_by("pk")
    permission_classes = [AllowAny, ]
    serializer_class = CatalogListSerializer


class CatalogControlBaseView(generics.GenericAPIView):
    queryset = Catalog.objects.all()
    permission_classes = [AllowAny, ]
    lookup_url_kwarg = "catalog"

    @staticmethod
    def _parse_catalog(catalog: Catalog) -> Tools:
        """Parse Catalog instance into CatalogTools for easy data access."""
        return Tools(Path(catalog.file_name.path))

    def get_object(self):
        instance = super().get_object()
        return self._parse_catalog(instance)


class CatalogControlsView(CatalogControlBaseView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        catalog = self.get_object()

        return Response({"controls": catalog.get_controls_all()}, status=status.HTTP_200_OK)


class CatalogControlDescriptionView(CatalogControlBaseView):
    def get(self, request: Request, control_id: str, *args, **kwargs) -> Response:
        catalog = self.get_object()
        control = catalog.get_control_by_id(control_id)

        return Response({"description": catalog.get_control_statement(control)})
