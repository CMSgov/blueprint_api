import json

import jsonschema
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Component


class ComponentAdminForm(ModelForm):
    class Meta:
        model = Component
        fields = [
            "title",
            "component_file",
            "supported_catalog_versions",
        ]

    def clean_component_file(self):
        component_upload = self.cleaned_data.get("component_file")
        component = json.load(component_upload.file)
        with open("components/schema/oscal_component_schema.json", "r") as file:
            oscal_schema = json.load(file)
        try:
            jsonschema.validate(instance=component, schema=oscal_schema)
        except ValidationError as exc:
            raise ValidationError("OSCAL validation error") from exc
        return component_upload
