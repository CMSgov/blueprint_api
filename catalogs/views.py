from pathlib import Path

from django.http import JsonResponse

from blueprintapi.settings import CATALOGS_DIR

from .catalogio import CatalogTools as Tools
from .models import Catalog


def getControlDescription(request, catalog: int, page: int, offset: int):
    """
    Return the data for a given catalog's control ID.
    :param catalog: An integer ID for a Catalog.
    :return: JSON object
    """

    result = Catalog.objects.get(pk=catalog)
    path = Path(CATALOGS_DIR).joinpath(result.file_name)
    catalog_object = Tools(path)
    controls = catalog_object.get_controls_all()
    start = page * offset
    end = start + offset
    values = {
        "title": catalog_object.catalog_title,
        "controls": controls[start:end],
    }

    return JsonResponse(values)
