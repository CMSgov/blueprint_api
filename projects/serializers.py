from typing import Optional
from rest_framework import serializers

from catalogs.catalogio import CatalogTools
from catalogs.io.v5_0 import CatalogModel
from catalogs.models import Catalog
from catalogs.serializers import ControlSerializer
from components.models import Component
from components.serializers import ComponentListSerializer
from projects.models import Project, ProjectControl

from blueprintapi.oscal.component import Model as ComponentModel


class ProjectListSerializer(serializers.ModelSerializer):
    completed_controls = serializers.IntegerField(required=False)
    total_controls = serializers.IntegerField(required=False)

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
            "completed_controls",
            "total_controls",
        )
        read_only_fields = ("id", "creator", "catalog", "completed_controls", "total_controls", )

    def create(self, validated_data):
        return Project.objects.create(
            creator=self.context["request"].user, **validated_data
        )


class ProjectSerializer(serializers.ModelSerializer):
    components = ComponentListSerializer(many=True)
    components_count = serializers.SerializerMethodField()
    completed_controls = serializers.IntegerField(required=False)
    total_controls = serializers.IntegerField(required=False)

    # noinspection PyMethodMayBeStatic
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
            "completed_controls",
            "total_controls",
        )
        read_only_fields = ("id", "creator", "completed_controls", "total_controls", )
        depth = 1


class BasicViewProjectSerializer(serializers.ModelSerializer):
    """Project serializer for the case where only basic project info is needed."""
    private_component = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = ("id", "title", "acronym", "private_component", )
        read_only_fields = ("id", "title", "acronym", )

    # noinspection PyMethodMayBeStatic
    def get_private_component(self, obj: Project) -> int:
        return obj.components.get(title=f"{obj.title} private").id


class ProjectControlSerializer(serializers.ModelSerializer):
    control = ControlSerializer(read_only=True)
    project = BasicViewProjectSerializer(read_only=True)
    catalog_data = serializers.SerializerMethodField(read_only=True)
    component_data = serializers.SerializerMethodField(read_only=True)
    disable_narratives = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True, required=False)
    enable_narratives = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = ProjectControl
        fields = (
            "status",
            "project",
            "control",
            "remarks",
            "catalog_data",
            "component_data",
            "disable_narratives",
            "enable_narratives",
        )

    def validate(self, attrs):
        if attrs.get("status") == ProjectControl.Status.NA and not attrs.get("remarks"):
            raise serializers.ValidationError("A justification is required for non-applicable controls.")
        return attrs

    def validate_disabled_narratives(self, value: list[int]) -> list[int]:
        invalid = []
        for item in value:
            if not self.instance.project.components.filter(id=item).exists():
                invalid.append(item)

        if invalid:
            raise serializers.ValidationError(f"Invalid ids are present in 'disabled_narratives': {invalid}")

        return value

    def update(self, instance, validated_data):
        if disable := validated_data.get("disable_narratives"):
            instance.disabled_narratives = list(set(instance.disabled_narratives).union(disable))

        if enable := validated_data.get("enable_narratives"):
            instance.disabled_narratives = list(set(instance.disabled_narratives).difference(enable))

        if status := validated_data.get("status"):
            instance.status = status

        instance.save()

        return instance


    def get_catalog_data(self, obj: ProjectControl) -> Optional[dict]:
        """Get the Catalog data for a given Control."""
        control_data = {}

        file = obj.control.catalog.file_name.path
        control_id = self.context.get("control_id")

        match obj.project.catalog_version:
            case Catalog.Version.CMS_ARS_3_1:
                catalog = CatalogTools(file)
                control_data = catalog.get_control_data_simplified(control_id=control_id)
                control_data["version"] = catalog.catalog_title
            case Catalog.Version.CMS_ARS_5_0:
                catalog = CatalogModel.from_json(file)
                control_data.update({"version": catalog.metadata.title, **catalog.control_summary(control_id)})

        return control_data

    def get_component_data(self, obj: ProjectControl) -> dict:
        """Get the narratives from any Component that includes the given Control."""
        if obj.project.components.exists():
            return self._get_control_data(obj, self.context.get("control_id"))

        return {}

    @staticmethod
    def _get_control_data(obj: ProjectControl, control_id: str) -> dict:
        type_map = {
            Component.Status.PUBLIC: "inherited",
            Component.Status.SYSTEM: "private"
        }

        result = {
            "responsibility": "Allocated",
            "components": {"inherited": {}, "private": {"description": None}},
        }

        responsibilities = []
        catalog_version = obj.project.catalog.version
        disabled_narratives = obj.disabled_narratives

        for component in obj.project.components.all():
            enabled = component.id not in disabled_narratives
            component_def = ComponentModel(**component.component_json).component_definition.components[0]

            try:
                control_data = component_def.get_control(control_id, catalog_version=catalog_version)
            except KeyError:
                control_data = None

            if control_data is not None:
                responsibility = control_data.responsibility
                responsibilities.append(responsibility)

                if (status := type_map[component.status]) == "private":
                    result["components"][status] = {
                        "id": component.id,
                        "description": control_data.description,
                        "enabled": enabled
                    }
                else:
                    # noinspection PyTypeChecker
                    result["components"][status][component.title] = {
                        "id": component.id,
                        "description": control_data.description,
                        "responsibility": responsibility,
                        "provider": control_data.provider,
                        "enabled": enabled
                    }

        if len(responsibilities) > 1:
            result["responsibility"] = "Hybrid"
        elif len(responsibilities) == 1:
            result["responsibility"] = responsibilities[0]

        return result


class ProjectControlListSerializer(serializers.ModelSerializer):
    control = ControlSerializer()
    project = BasicViewProjectSerializer()

    class Meta:
        model = ProjectControl
        fields = (
            "status",
            "control",
            "project",
            "remarks",
        )
        read_only_fields = ("status", "control", "project", "remarks", )
