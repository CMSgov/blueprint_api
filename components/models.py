from django.contrib.postgres.fields import ArrayField
from django.db import models

from catalogs.models import Catalog


class Component(models.Model):
    class Status(models.IntegerChoices):
        SYSTEM = 1, "System Specific"
        PUBLIC = 2, "Public"

    title = models.CharField(
        max_length=100,
        unique=True,
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
        null=True,
        blank=True,
        unique=False,
        help_text="Type category of the component",
    )
    supported_catalog_versions = ArrayField(
        models.CharField(choices=Catalog.Version.choices, max_length=16),
        help_text="Catalog versions that this component is defined on.",
    )
    controls = ArrayField(
        models.CharField(max_length=30, blank=True),
        help_text="List of controls that the component addresses",
        null=True,
        blank=True,
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
        null=True,
        blank=True,
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
