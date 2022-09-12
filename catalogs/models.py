import json
import jsonschema

from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonschema.exceptions import SchemaError, ValidationError


def validate_catalog(file_name):
    cat = json.load(file_name.file)
    with open("catalogs/schemas/oscal_catalog_schema.json", "r") as file:
        oscal_schema = json.load(file)

    try:
        jsonschema.validate(instance=cat, schema=oscal_schema)
    except ValidationError as exc:
        raise ValidationError("The Catalog is not a valid OSCAL catalog.") from exc
    except SchemaError as exc:
        raise ValidationError("The Catalog schema is not a valid OSCAL catalog schema.") from exc


class Catalog(models.Model):
    class ImpactLevel(models.TextChoices):
        LOW = "low", _("Low")
        MODERATE = "moderate", _("Moderate")
        HIGH = "high", _("High")

    class Version(models.TextChoices):
        CMS_ARS_3_1 = "CMS_ARS_3_1", _("CMS ARS 3.1")
        CMS_ARS_5_0 = "CMS_ARS_5_0", _("CMS ARS 5.0")

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
        choices=Version.choices,
        max_length=16,
        blank=False,
        default=Version.CMS_ARS_3_1,
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

    class Meta:
        unique_together = ("version", "impact_level")


class Controls(models.Model):
    catalog = models.ForeignKey(to="catalogs.Catalog", on_delete=models.CASCADE)
    control_id = models.CharField(
        max_length=12,
        help_text="Catalog control ID, for example ac-1",
    )
    control_label = models.CharField(
        max_length=12,
        help_text="Catalog control label, for example AC-01",
    )
    sort_id = models.CharField(
        max_length=12,
        help_text="Catalog ID used for sorting, for example ac-01",
    )
    title = models.CharField(
        max_length=124,
        help_text="Catalog control title, for example Access Control Policy and Procedures.",
    )

    def __str__(self):
        return self.control_label
