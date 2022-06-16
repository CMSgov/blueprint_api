from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from catalogs.models import Catalog


class Component(models.Model):
    title = models.CharField(
        max_length=100,
        unique=False,
        help_text="Name of the component",
    )
    description = models.CharField(
        max_length=500,
        unique=False,
        help_text="Description of the component",
    )
    type = models.CharField(
        max_length=100,
        null=False,
        unique=False,
        help_text="Type category of the component",
    )
    catalog = models.ForeignKey(
        Catalog,
        null=False,
        on_delete=models.PROTECT,
        related_name="components_for_catalog",
        help_text="Catalog id that this component applies to",
    )
    controls = ArrayField(
        models.CharField(max_length=30, blank=True),
        help_text="List of controls that the component addresses",
    )
    search_terms = ArrayField(
        models.CharField(max_length=50, blank=True),
        null=True,
        help_text="List of keywords to search for the component",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(
        auto_now=True,
        db_index=True,
        null=True,
    )
    component_json = models.JSONField(
        null=False,
        help_text="OSCAL JSON representation of the component",
    )


# ensure the "type" field value is lowercase before saving
@receiver(pre_save, sender=Component)
def convert_to_lowercase(sender, instance, *args, **kwargs):
    instance.type = instance.type.lower()
