from rest_framework import serializers

from catalogs.catalogio import CatalogTools
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

    def get_catalog_data(self, obj):
        data = get_catalog_data(obj.controls, obj.catalog)
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
            "component_json",
            "component_file",
            "status",
            "catalog_data",
        )


def get_catalog_data(controls: list, catalog):
    """Return the Catalog data for the given Controls."""
    cat_data = CatalogTools(catalog.file_name.path)
    data: dict = {}
    for ct in controls:
        control = cat_data.get_control_by_id(ct)
        data[ct] = {
            "label": cat_data.get_control_property_by_name(control, "label"),
            "description": cat_data.get_control_statement(control),
            "implementation": cat_data.get_control_part_by_name(
                control, "implementation"
            ),
            "guidance": cat_data.get_control_part_by_name(control, "guidance"),
        }
    return data
