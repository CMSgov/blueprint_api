import decimal

from django.db.models import QuerySet
from rest_framework import serializers

from catalogs.catalogio import CatalogTools
from catalogs.serializers import ControlSerializer
from components.componentio import ComponentTools
from components.models import Component
from components.serializers import ComponentListSerializer
from projects.models import Project, ProjectControl


class ProjectListSerializer(serializers.ModelSerializer):
    percent_complete = serializers.DecimalField(
        max_digits=3, decimal_places=0, coerce_to_string=False, required=False, rounding=decimal.ROUND_UP
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "impact_level",
            "catalog_version",
            "creator",
            "location",
            "catalog",
            "percent_complete",
        )
        read_only_fields = ("id", "creator", "catalog", "percent_complete", )

    def create(self, validated_data):
        return Project.objects.create(
            creator=self.context["request"].user, **validated_data
        )


class ProjectSerializer(serializers.ModelSerializer):
    components = ComponentListSerializer(many=True)
    components_count = serializers.SerializerMethodField()
    percent_complete = serializers.DecimalField(
        max_digits=3, decimal_places=0, coerce_to_string=False, required=False, rounding=decimal.ROUND_UP
    )

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
            "percent_complete",
        )
        read_only_fields = ("id", "creator", "percent_complete", )
        depth = 1


class BasicViewProjectSerializer(serializers.ModelSerializer):
    """Project serializer for the case where only basic project info is needed."""
    class Meta:
        model = Project
        fields = ("id", "title", "acronym", )
        read_only_fields = ("id", "title", "acronym", )


class ProjectControlSerializer(serializers.ModelSerializer):
    control = ControlSerializer(read_only=True)
    project = BasicViewProjectSerializer(read_only=True)
    catalog_data = serializers.SerializerMethodField(read_only=True)
    component_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectControl
        fields = ("status", "project", "control", "catalog_data", "component_data", )

    def get_catalog_data(self, obj: ProjectControl) -> dict:
        """Get the Catalog data for a given Control."""
        catalog = CatalogTools(obj.control.catalog.file_name.path)
        control_data = catalog.get_control_data_simplified(control_id=self.context.get("control_id"))
        control_data["version"] = catalog.catalog_title

        return control_data

    def get_component_data(self, obj: ProjectControl) -> dict:
        """Get the narratives from any Component that includes the given Control."""
        if obj.project.components.exists():
            return self._get_control_data(obj.project.components.all(), self.context.get("control_id"))

        return {}

    @staticmethod
    def _get_control_data(components: QuerySet, control_id: str) -> dict:
        component_data = {
            "responsibility": "Allocated",
            "components": {"inherited": {}, "private": {}},
        }
        count = 0
        responsibility: str = ""
        for component in components:
            status = "inherited" if component.status == Component.Status.PUBLIC else "private"
            if control_id in component.controls:
                count += 1
                controls = ComponentTools(component.component_json)
                control_data = controls.get_control_by_id(control_id)
                responsibility = controls.get_control_props(control_data[0], "security_control_type")
                component_data["components"][status][component.title] = {
                    "description": control_data[0].get("description"),
                    "responsibility": responsibility,
                    "provider": controls.get_control_props(control_data[0], "provider"),
                }

        if count > 1:
            component_data["responsibility"] = "Hybrid"
        elif count == 1:
            component_data["responsibility"] = responsibility

        return component_data


class ProjectControlListSerializer(serializers.ModelSerializer):
    control = ControlSerializer()
    project = BasicViewProjectSerializer()

    class Meta:
        model = ProjectControl
        fields = (
            "status",
            "control",
            "project",
        )
        read_only_fields = ("status", "control", "project", )
