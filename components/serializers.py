import json

from typing import List, Optional, Tuple

from django.contrib.auth.models import AnonymousUser
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from blueprintapi.oscal.component import ImplementedRequirement, Model
from catalogs.catalogio import CatalogTools
from components.componentio import ComponentTools
from components.models import Component
from projects.models import Project
from users.models import User


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
            "component_json",
            "component_file",
            "controls_count",
        )


class ComponentSerializer(serializers.ModelSerializer):
    catalog_data = serializers.SerializerMethodField()
    component_data = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()

    def get_catalog_data(self, obj):
        data = collect_catalog_data(obj.controls, obj.catalog)
        return data

    def get_component_data(self, obj):
        data = collect_component_data(obj.component_json)
        return data

    def get_project_data(self, obj):
        data: dict = {}
        user: dict = {}
        request = self.context.get("request")
        if hasattr(request, "user"):
            user = request.user

        """
        @todo - Remove this when we can corrolate a request to a user.
        """
        if not user or isinstance(user, AnonymousUser):
            user = User.objects.exclude(username="AnonymousUser").first()
        """end @todo"""

        data = collect_project_data(obj.id, user)
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
            "project_data",
        )


def collect_catalog_data(controls: list, catalog):
    """Return the Catalog data for the given Controls."""
    cat_data = CatalogTools(catalog.file_name.path)
    data: dict = {}
    data["version"] = cat_data.catalog_title
    data["controls"] = {}
    for ct in controls:
        data["controls"][ct] = cat_data.get_control_data_simplified(ct)
    return data


def collect_component_data(component: dict):
    tools = ComponentTools(component)

    component_data: dict = {}
    control_list = tools.get_controls()
    controls: dict = {}
    for c in control_list:
        controls[c.get("control-id")] = {
            "narrative": c.get("description"),
            "responsibility": get_control_responsibility(c, "security_control_type"),
            "provider": get_control_responsibility(c, "provider"),
        }

    cp = tools.get_components()[0]
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


def collect_project_data(component_id, user):
    form_values = {
        "add": [],
        "remove": [],
    }

    all_projects = Project.objects.filter(creator_id=user)

    remove = (
        Project.components.through.objects.filter(
            component_id=component_id, project_id__in=all_projects
        )
        .select_related()
        .values_list("project_id", flat=True)
    )
    for r in remove:
        project_data = Project.objects.get(pk=r)
        form_values["remove"].append({"value": r, "label": project_data.title})

    add = Project.objects.filter(creator_id=user).exclude(pk__in=remove)
    for a in add:
        form_values["add"].append({"value": a.id, "label": a.title})

    return form_values


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
            "catalog",
            "controls_count",
        )


class ComponentControlSerializer(serializers.ModelSerializer):
    class Action(TextChoices):
        ADD = "add", _("Add control")
        REMOVE = "remove", _("Remove control")
        UPDATE = "update", _("Update control description")

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

    def validate(self, data: dict) -> dict:
        def _check_required_field(field_: str):
            if not data.get(field_):
                raise serializers.ValidationError(f"Required field, {field_} was not provided or is empty.")

        # Controls, action, catalog_version always required.
        for field in ("action", "controls", "catalog_version"):
            _check_required_field(field)

        return data

    # noinspection PyMethodMayBeStatic
    def validate_controls(self, value: list) -> list:
        if len(value) > 1:
            raise serializers.ValidationError("Updating multiple controls is not supported.")

        return value

    def update(self, instance: Component, validated_data: dict) -> Component:
        control = validated_data["controls"][0]
        action = validated_data["action"]
        catalog_version = validated_data["catalog_version"]

        if action == self.Action.REMOVE:
            self._remove_implemented_requirement(instance, control, catalog_version)
        elif action == self.Action.ADD:
            self._add_implemented_requirement(instance, control, validated_data["description"], catalog_version)
        else:
            self._update_implemented_requirement(instance, control, catalog_version, validated_data["description"])

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

    def _add_implemented_requirement(self, instance: Component, control: str, description: str, catalog_version: str):
        if control in instance.controls:
            raise serializers.ValidationError(f"{control} has already been added to {instance}.")

        location, component_model = self._find_update_location(instance, catalog_version)

        if location:
            location.append(ImplementedRequirement(control_id=control, description=description))
            instance.component_json = json.loads(component_model.json(by_alias=True, exclude_none=True))

    def _remove_implemented_requirement(self, instance: Component, control: str, catalog_version: str):
        if control not in instance.controls:
            raise serializers.ValidationError(f"Missing control, {control} cannot be removed from {instance}.")

        location, component_model = self._find_update_location(instance, catalog_version)

        if location:
            location.remove(next(filter(lambda requirement: requirement.control_id == control, location)))
            instance.component_json = json.loads(component_model.json(by_alias=True, exclude_none=True))

    def _update_implemented_requirement(
            self, instance: Component, control: str, catalog_version: str, description: str
    ):
        if control not in instance.controls:
            raise serializers.ValidationError(f"Missing control, {control} cannot be updated in {instance}")

        location, component_model = self._find_update_location(instance, catalog_version)

        if location:
            for requirement in location:
                if requirement.control_id == control:
                    requirement.description = description

            instance.component_json = json.loads(component_model.json(by_alias=True, exclude_none=True))
