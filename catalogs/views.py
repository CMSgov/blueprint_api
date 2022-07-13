from pathlib import Path

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .catalogio import CatalogTools as Tools
from .models import Catalog
from .serializers import CatalogListSerializer


class CatalogListView(generics.ListCreateAPIView):
    """
    Use for read-write endpoints to represent a collection of model instances.
    Provides get and post method handlers.
    """

    queryset = Catalog.objects.all().order_by("pk")
    serializer_class = CatalogListSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CatalogListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_controls(request, catalog: int):
    """
    Return a list of all of the Controls for a given Catalog.
    :param catalog: An integer ID for a Catalog.
    :return: A JSON object list of Controls.
    """
    cat = _get_catalog(catalog)
    if not cat:
        return Response(status=status.HTTP_404_NOT_FOUND)

    controls = cat.get_controls_all()
    response = {
        "controls": controls,
    }

    return Response(response)


@api_view(["GET"])
def get_control_by_id(request, catalog: int, control_id: str):
    """
    Return the data for a given catalog's control ID.
    :param catalog: An integer ID for a Catalog.
    :param control_id: An OSCAL control ID.
    :return: JSON object
    """
    cat = _get_catalog(catalog)
    if not cat:
        return Response(status=status.HTTP_404_NOT_FOUND)

    control = cat.get_control_by_id(control_id)
    desc = cat.get_control_statement(control)
    response = {
        "description": desc,
    }

    return Response(response)


def _get_catalog(catalog: int):
    """
    Load a Catalog object.
    :param catalog: An integer ID for a Catalog.
    :return: Return a Catalog object.
    """
    try:
        result = Catalog.objects.get(pk=catalog)
    except Catalog.DoesNotExist:
        return

    path = Path(result.file_name.path)
    catalog_object = Tools(path)

    return catalog_object
