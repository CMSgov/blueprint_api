from rest_framework import serializers

from catalogs.catalogio import CatalogTools
from components.componentio import ComponentTools
from components.serializers import ComponentListSerializer
from projects.models import Project


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "catalog_version",
            "impact_level",
            "creator",
            "location",
            "catalog",
        )


class ProjectSerializer(serializers.ModelSerializer):
    components = ComponentListSerializer(many=True)
    components_count = serializers.SerializerMethodField()

    def get_components_count(self, obj):
        return obj.components.count()

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "catalog_version",
            "impact_level",
            "location",
            "status",
            "creator",
            "components",
            "components_count",
        )
        depth = 1


class ProjectControlSerializer(serializers.ModelSerializer):
    catalog_data = serializers.SerializerMethodField()
    component_data = serializers.SerializerMethodField()

    def get_catalog_data(self, obj):
        """
        Get the Catalog data for a given Control.
        """
        project_catalog = obj.catalog
        control_id = self.context.get("control_id")
        catalog = CatalogTools(project_catalog.file_name.path)
        control_data = catalog.get_control_data_simplified(control_id)
        control_data["version"] = catalog.catalog_title
        return control_data

    def get_component_data(self, obj):
        """
        Get the narratives from any Component that includes the given Control.
        """
        control_id = self.context.get("control_id")
        components: dict = {}
        if hasattr(obj, "components"):
            components = self.get_control_data(obj.components, control_id)
        return components

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "catalog_data",
            "component_data",
        )

    def get_control_data(self, components, control_id):
        component_data = {
            "responsibility": "Allocated",
            "components": {"inherited": {}, "private": {}},
        }
        count = 0
        responsibility: str = ""
        for c in components.all():
            status = "inherited" if c.status == 2 else "private"
            if control_id in c.controls:
                count += 1
                controls = ComponentTools(c.component_json)
                control_data = controls.get_control_by_id(control_id)
                responsibility = (
                    controls.get_control_props(
                        control_data[0],
                        "security_control_type",
                    ),
                )
                component_data["components"][status][c.title] = {
                    "description": control_data[0].get("description"),
                    "responsibility": responsibility,
                    "provider": controls.get_control_props(control_data[0], "provider"),
                }

        if count > 1:
            component_data["responsibility"] = "Hybrid"
        elif count == 1:
            component_data["responsibility"] = responsibility

        return component_data
