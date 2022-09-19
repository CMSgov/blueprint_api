import json

from typing import Any, List, Optional, Tuple

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from blueprintapi.oscal.component import ImplementedRequirement, Model
from catalogs.catalogio import CatalogTools
from catalogs.models import Catalog
from components.models import Component
from projects.models import Project


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
            "supported_catalog_versions",
            "component_json",
            "component_file",
            "controls_count",
        )
        read_only_fields = ("supported_catalog_versions", "id", )


class ComponentSerializer(serializers.ModelSerializer):
    catalog_data = serializers.SerializerMethodField()
    component_data = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()

    class Meta:
        model = Component
        fields = (
            "id",
            "title",
            "description",
            "type",
            "controls",
            "search_terms",
            "status",
            "catalog_data",
            "component_data",
            "project_data",
        )
        read_only_fields = ("id", "catalog_data", "component_data", "project_data", )

    def get_catalog_data(self, obj):
        data = collect_catalog_data(obj.controls, obj.supported_catalog_versions)
        return data

    def get_component_data(self, obj):
        data = collect_component_data(obj.component_json)
        return data

    def get_project_data(self, obj):
        user = self.context["request"].user

        form_values = {
            "add": [],
            "remove": [],
        }

        all_projects = Project.objects.filter(creator_id=user)

        remove = (
            Project.components.through.objects.filter(
                component_id=obj.id, project_id__in=all_projects
            )
            .select_related()
            .values_list("project_id", flat=True)
        )
        for project_id in remove:
            project_data = Project.objects.get(pk=project_id)
            form_values["remove"].append({"value": project_id, "label": project_data.title})

        add = Project.objects.filter(creator_id=user).exclude(pk__in=remove)
        for project in add:
            form_values["add"].append({"value": project.id, "label": project.title})

        return form_values


def collect_catalog_data(controls: list, catalog_versions: List[Catalog.Version]) -> dict:
    """Return the Catalog data for the given Controls."""
    data = {}
    catalogs = Catalog.objects.filter(version__in=catalog_versions)

    for catalog in catalogs:
        if (version := catalog.version) not in data:
            data[version] = {}

        cat_data = CatalogTools(catalog.file_name.path)
        data[version][catalog.impact_level] = {
            "controls": {control: cat_data.get_control_data_simplified(control) for control in controls}
        }

    return data


def collect_component_data(component: dict) -> dict:
    component_model = Model(**component)
    component_def = component_model.component_definition.components[0]

    return {
        "title": component_def.title,
        "description": component_def.description,
        "standards": {
            item.description: {
                "source": item.source,
                "controls": {
                    control.control_id: {
                        "narrative": control.description,
                        "responsibility": control.responsibility,
                        "provider": control.provider
                    }
                    for control in item.implemented_requirements
                }
            }
            for item in component_def.control_implementations
        }
    }


def get_control_responsibility(control: dict, name: str) -> Optional[Any]:
    if "props" in control and isinstance(control.get("props"), list):
        for prop in control.get("props"):
            if prop.get("name") == name:
                return prop.get("value")


class ComponentListBasicSerializer(serializers.ModelSerializer):
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
            "supported_catalog_versions",
            "controls_count",
        )


class ComponentControlSerializer(serializers.ModelSerializer):
    class Action(TextChoices):
        ADD = "add", _("Add control")
        REMOVE = "remove", _("Remove control")

    catalog_version = serializers.CharField(write_only=True)
    action = serializers.ChoiceField(choices=Action.choices, write_only=True)

    class Meta:
        model = Component
        fields = (
            "pk",
            "controls",
            "description",
            "component_json",
            "action",
            "catalog_version",
        )
        read_only_fields = ("component_json", "pk", )

    def validate(self, attrs: dict) -> dict:
        def _check_required_field(field_: str):
            if not attrs.get(field_):
                raise serializers.ValidationError(f"Required field, {field_} was not provided or is empty.")

        # Controls, action, catalog_version always required.
        for field in ("action", "controls", "catalog_version"):
            _check_required_field(field)

        if attrs.get("action") == self.Action.ADD and not attrs.get("description"):
            raise serializers.ValidationError(f"'description' is required for 'add' action.")

        return attrs

    # noinspection PyMethodMayBeStatic
    def validate_controls(self, value: list) -> list:
        if len(value) > 1:
            raise serializers.ValidationError("Updating multiple controls is not supported.")

        return value

    # noinspection PyMethodMayBeStatic
    def validate_catalog_version(self, value: str):
        try:
            catalog_version = Catalog.Version(value)
        except ValueError as exc:
            raise serializers.ValidationError(f"Invalid catalog version: '{value}'") from exc

        return catalog_version

    def update(self, instance: Component, validated_data: dict) -> Component:
        control = validated_data["controls"][0]
        action = validated_data["action"]
        catalog_version = validated_data["catalog_version"]

        try:
            location, component_model = self._find_update_location(instance, catalog_version)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError(
                f"Could not find a matching section for the provided catalog version, {catalog_version}."
            ) from exc

        if action == self.Action.REMOVE:
            self._remove_implemented_requirement(instance, control, location, component_model)
        else:
            self._add_implemented_requirement(
                instance, control, validated_data["description"], location, component_model
            )

        instance.save()

        return instance

    @staticmethod
    def _find_update_location(
            instance: Component, catalog_version: str
    ) -> Optional[Tuple[List[ImplementedRequirement], Model]]:
        """Find the sections of a Component's json that needs to be updated."""
        component_data = Model(**instance.component_json)

        for component in component_data.component_definition.components:
            for implementation in component.control_implementations:
                if catalog_version in implementation.description:
                    return implementation.implemented_requirements, component_data

    @staticmethod
    def _add_implemented_requirement(
            instance: Component,
            control: str,
            description: str,
            location: List[ImplementedRequirement],
            component_model: Model
    ):
        requirement = next(filter(lambda req: req.control_id == control, location), None)

        if requirement is None:
            location.append(ImplementedRequirement(control_id=control, description=description))
        else:
            requirement.description = description

        instance.component_json = json.loads(component_model.json(by_alias=True, exclude_none=True))

    @staticmethod
    def _remove_implemented_requirement(
            instance: Component,
            control: str,
            location: List[ImplementedRequirement],
            component_model: Model
    ):
        try:
            location.remove(next(filter(lambda requirement: requirement.control_id == control, location)))
        except StopIteration as exc:
            raise serializers.ValidationError(
                f"Could not remove control, {control} from {instance.title}. Matching control not found."
            ) from exc

        instance.component_json = json.loads(component_model.json(by_alias=True, exclude_none=True))
