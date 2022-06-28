import json

import jsonschema
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .componentio import ComponentTools as Tools
from .models import Component


class ComponentAdminForm(ModelForm):
    class Meta:
        model = Component
        fields = [
            "title",
            "component_file",
            "catalog",
        ]

    def clean_component_file(self):
        cleaned_data = super().clean()
        component_upload = cleaned_data.get("component_file")
        self.component = json.load(component_upload.file)
        with open("components/schema/oscal_component_schema.json", "r") as file:
            oscal_schema = json.load(file)
        try:
            jsonschema.validate(instance=self.component, schema=oscal_schema)
            self.comp = Tools(self.component)
        except ValidationError:
            raise ValidationError("OSCAL validation error")
        return component_upload
