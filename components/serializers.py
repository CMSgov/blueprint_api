from rest_framework import serializers

from catalogs.catalogio import CatalogTools
from components.componentio import ComponentTools
from components.models import Component


class ComponentListSerializer(serializers.ModelSerializer):
    controls_count = serializers.SerializerMethodField()

    def get_controls_count(self, obj):
        return len(obj.controls)

    class Meta:
        model = Component
        fields = (
            "id",
            "title",
            "description",
            "type",
            "catalog",
            "controls_count",
        )


class ComponentSerializer(serializers.ModelSerializer):
    catalog_data = serializers.SerializerMethodField()
    component_data = serializers.SerializerMethodField()

    def get_catalog_data(self, obj):
        data = get_catalog_data(obj.controls, obj.catalog)
        return data

    def get_component_data(self, obj):
        data = get_component_data(obj.component_json)
        return data

    class Meta:
        model = Component
        fields = (
            "id",
            "title",
            "description",
            "type",
            "catalog",
            "controls",
            "search_terms",
            "status",
            "catalog_data",
            "component_data",
        )


def get_catalog_data(controls: list, catalog):
    """Return the Catalog data for the given Controls."""
    cat_data = CatalogTools(catalog.file_name.path)
    data: dict = {}
    data["version"] = cat_data.catalog_title
    data["controls"] = {}
    for ct in controls:
        data["controls"][ct] = cat_data.get_control_data_simplified(ct)
    return data


def get_component_data(component: dict):
    comp = ComponentTools(component)

    component_data: dict = {}
    control_list = comp.get_controls()
    print(control_list)
    controls: dict = {}
    for c in control_list:
        print(c)
        controls[c.get("control-id")] = {
            "narrative": c.get("description"),
            "responsibility": get_control_responsibility(c, "security_control_type"),
            "provider": get_control_responsibility(c, "provider"),
        }

    cp = comp.get_components()[0]
    component_data = {
        "title": cp.get("title"),
        "description": cp.get("description"),
        "standard": cp.get("control-implementations")[0].get("description"),
        "source": cp.get("control-implementations")[0].get("source"),
    }
    component_data["controls"] = controls
    return component_data


def get_control_responsibility(control, prop):
    if "props" in control and isinstance(control.get("props"), list):
        for p in control.get("props"):
            if p.get("name") == prop:
                return p.get("value")
