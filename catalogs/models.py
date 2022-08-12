import json
import os

import jsonschema
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from jsonschema.exceptions import SchemaError, ValidationError

from .catalogio import CatalogTools


def validate_catalog(file_name):
    cat = json.load(file_name.file)
    with open("catalogs/schemas/oscal_catalog_schema.json", "r") as file:
        oscal_schema = json.load(file)

    try:
        jsonschema.validate(instance=cat, schema=oscal_schema)
    except ValidationError:
        raise ValidationError("The Catalog is not a valid OSCAL catalog.")
    except SchemaError:
        raise ValidationError("The Catalog schema is not a valid OSCAL catalog schema.")


class Catalog(models.Model):
    class ImpactLevel(models.TextChoices):
        LOW = "low", _("Low")
        MODERATE = "moderate", _("Moderate")
        HIGH = "high", _("High")

    name = models.CharField(max_length=100, help_text="Name of Catalog", unique=True)
    file_name = models.FileField(
        max_length=100,
        help_text="Location of static catalog data file",
        validators=[validate_catalog],
    )
    source = models.URLField(
        max_length=500,
        null=False,
        default="https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/"
        "SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json",
    )
    version = models.CharField(
        max_length=64,
        blank=False,
        default="CMS ARS 3.1",
    )
    impact_level = models.CharField(
        choices=ImpactLevel.choices,
        max_length=20,
        blank=False,
        default=ImpactLevel.MODERATE,
        help_text="FISMA impact level of the project",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Catalog)
def add_controls(sender, instance, **kwargs):
    if kwargs["created"]:
        catalog = CatalogTools(instance.file_name.path)
        controls = catalog.get_controls_all_ids()
        if controls:
            for c in controls:
                control_data = catalog.get_control_data_simplified(c)
                ctrl = Controls(
                    catalog=instance,
                    control_id=c,
                    control_label=control_data.get("label"),
                    sort_id=control_data.get("sort_id"),
                    title=control_data.get("title"),
                )
                ctrl.save()


@receiver(models.signals.post_delete, sender=Catalog)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Delete files from the filesystem when a Catalog object is deleted.
    """
    if instance.file_name:
        if os.path.isfile(instance.file_name.path):
            os.remove(instance.file_name.path)


@receiver(models.signals.pre_save, sender=Catalog)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Delete old file from filesystem when Catalog object is update with a new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Catalog.objects.get(pk=instance.pk).file_name
    except Catalog.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Controls(models.Model):
    catalog = models.ForeignKey(to="catalogs.Catalog", on_delete=models.CASCADE)
    control_id = models.CharField(
        max_length=12,
        unique=False,
        blank=False,
    )
    control_label = models.CharField(
        max_length=12,
        unique=False,
        blank=False,
    )
    sort_id = models.CharField(
        max_length=12,
        unique=False,
        blank=False,
    )
    title = models.CharField(
        max_length=124,
        unique=False,
        blank=False,
    )

    def __str__(self):
        return self.control_label
