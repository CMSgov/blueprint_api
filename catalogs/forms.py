import json

import jsonschema
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Catalog


class CatalogAdminForm(ModelForm):
    class Meta:
        model = Catalog
        fields = "__all__"

    def clean_file_name(self):
        cat_upload = self.cleaned_data["file_name"]
        cat = json.load(cat_upload.file)

        with open("catalogs/schemas/oscal_catalog_schema.json", "r") as file:
            oscal_schema = json.load(file)

        try:
            jsonschema.validate(instance=cat, schema=oscal_schema)
        except ValidationError:
            raise ValidationError("Validation error")

        return cat_upload
