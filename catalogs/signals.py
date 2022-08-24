import os

from typing import List

from catalogs.catalogio import CatalogTools
from catalogs.models import Catalog, Controls


# noinspection PyUnusedLocal
def add_controls(sender, instance: Catalog, created: bool, **kwargs):
    if created:
        catalog = CatalogTools(instance.file_name.path)
        control_ids = catalog.get_controls_all_ids()
        if control_ids:
            control_objects: List = []
            for c in control_ids:
                control_data = catalog.get_control_data_simplified(c)
                control_objects.append(
                    Controls(
                        catalog=instance,
                        control_id=c,
                        control_label=control_data.get("label"),
                        sort_id=control_data.get("sort_id"),
                        title=control_data.get("title"),
                    )
                )
            Controls.objects.bulk_create(control_objects)


# noinspection PyUnusedLocal
def auto_delete_file_on_delete(sender, instance: Catalog, **kwargs):
    """Delete files from the filesystem when a Catalog object is deleted."""
    if instance.file_name:
        if os.path.isfile(instance.file_name.path):
            os.remove(instance.file_name.path)


# noinspection PyUnusedLocal
def auto_delete_file_on_change(sender, instance: Catalog, **kwargs):
    """Delete old file from filesystem when Catalog object is update with a new file."""
    if not instance.pk:
        return False

    try:
        old_file = Catalog.objects.get(pk=instance.pk).file_name
    except Catalog.DoesNotExist:
        return False

    new_file = instance.file_name
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)