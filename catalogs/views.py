from pathlib import Path

from django.http import JsonResponse

from .catalogio import CatalogTools as Tools
from .models import Catalog


def get_all_controls(request, catalog: int):
    """
    Return a list of all of the Controls for a given Catalog.
    :param catalog: An integer ID for a Catalog.
    :return: A JSON object list of Controls.
    """
    cat = get_catalog(catalog)
    controls = cat.get_controls_all()
    response = {
        "controls": controls,
    }

    return JsonResponse(response)


def get_control_by_id(request, catalog: int, control_id: str):
    """
    Return the data for a given catalog's control ID.
    :param catalog: An integer ID for a Catalog.
    :param control_id: An OSCAL control ID.
    :return: JSON object
    """
    cat = get_catalog(catalog)
    control = cat.get_control_by_id(control_id)
    desc = cat.get_control_statement(control)
    response = {
        "description": desc,
    }

    return JsonResponse(response)


def get_catalog(catalog: int):
    """
    Load a Catalog object.
    :param catalog: An integer ID for a Catalog.
    :return: Return a Catalog object.
    """
    result = Catalog.objects.get(pk=catalog)
    path = Path(result.file_name.path)
    catalog_object = Tools(path)

    return catalog_object
