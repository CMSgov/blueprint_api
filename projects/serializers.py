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
            "impact_level",
            "location",
            "status",
            "creator",
            "components",
            "components_count",
            "catalog",
        )
        depth = 1


class ProjectControlSerializer(serializers.ModelSerializer):
    catalog_data = serializers.SerializerMethodField()
    component_data = serializers.SerializerMethodField()
    responsibility = serializers.SerializerMethodField()

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

    def get_responsibility(self, obj):
        """
        Calculate the user's responsibility.
        """
        responsibility = "Allocated"
        if hasattr(self, "component_data"):
            if self.component_data.len() == 1:
                component = list(self.component_data.items())[0]
                responsibility = component.get("responsibility")
            else:
                responsibility = "Shared"
        return responsibility

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "catalog_data",
            "component_data",
            "responsibility",
        )

    def get_control_data(self, components, control_id):
        component_data: dict = {}
        for c in components.all():
            if control_id in c.controls:
                controls = ComponentTools(c.component_json)
                control_data = controls.get_control_by_id(control_id)
                component_data[c.title] = {
                    "description": control_data[0].get("description"),
                    "responsibility": controls.get_control_props(
                        control_data[0], "security_control_type"
                    ),
                    "provider": controls.get_control_props(control_data[0], "provider"),
                }

        return component_data
