import json

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from catalogs.models import Catalog

from .componentio import ComponentTools as Tools


class Component(models.Model):
    class Status(models.IntegerChoices):
        SYSTEM = 1, "System Specific"
        PUBLIC = 2, "Public"

    title = models.CharField(
        max_length=100,
        unique=False,
        help_text="Name of the component",
    )
    description = models.CharField(
        max_length=500,
        unique=False,
        blank=True,
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
    component_file = models.FileField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Upload an OSCAL formatted JSON Component file",
    )
    status = models.IntegerField(default=Status.PUBLIC, choices=Status.choices)

    def __str__(self):
        return self.title


@receiver(pre_save, sender=Component)
def parse_component_json(sender, instance, *args, **kwargs):
    """
    If the Component is an uploaded file, load the JSON and add it to the
    component_json field.
    """
    if instance.component_file:
        file = instance.component_file.file.open("r")
        instance.component_json = json.load(file)


@receiver(pre_save, sender=Component)
def add_description(sender, instance, *args, **kwargs):
    """Get the Description from a given Component JSON object."""
    if instance.component_json and not instance.description:
        tool = Tools(instance.component_json)
        instance.description = tool.get_component_value("description")


@receiver(pre_save, sender=Component)
def convert_to_lowercase(sender, instance, *args, **kwargs):
    """Ensure the "type" field value is lowercase before saving."""
    if instance.component_json and not instance.type:
        tool = Tools(instance.component_json)
        instance.type = tool.get_component_value("type").lower()
    elif instance.type:
        instance.type = instance.type.lower()


@receiver(pre_save, sender=Component)
def add_controls(sender, instance, *args, **kwargs):
    """Add the controls from the component to the controls field."""
    if instance.component_json:
        tool = Tools(instance.component_json)
        instance.controls = tool.get_control_ids()
