import uuid

from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

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
            "component_json",
        )

    def partial_update(self, instance, validated_data):
        if controls := validated_data.get("controls"):
            existing_control = controls not in instance.controls
            if not existing_control:
                instance.controls = list(set(instance.controls).union(controls))

            if description := validated_data.get("description"):
                implemented_requirement = {
                    "uuid": str(uuid.uuid4()),
                    "props": [
                        {
                            "name": "security_control_type",
                            "uuid": str(uuid.uuid4()),
                            "value": "Hybrid",
                        },
                        {"name": "provider", "uuid": str(uuid.uuid4()), "value": "No"},
                    ],
                    "control-id": controls[0],
                    "description": description,
                }
                if existing_control:
                    for implemented in (
                        instance.component_json.get("component-definition")
                        .get("components")[0]
                        .get("control-implementations")[0]
                        .get("implemented-requirements")
                    ):
                        if implemented.get("control-id") == controls[0]:
                            instance.component_json.get("component-definition").get(
                                "components"
                            )[0].get("control-implementations")[0].get(
                                "implemented-requirements"
                            ).remove(
                                implemented
                            )

                    instance.component_json.get("component-definition").get(
                        "components"
                    )[0].get("control-implementations")[0].get(
                        "implemented-requirements"
                    ).append(
                        implemented_requirement
                    )
                else:
                    instance.component_json.get("component-definition").get(
                        "components"
                    )[0].get("control-implementations")[0].get(
                        "implemented-requirements"
                    ).append(
                        implemented_requirement
                    )

        instance.save()
        return instance


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
    class Meta:
        model = Component
        fields = (
            "pk",
            "controls",
            "description",
            "component_json",
        )

    def update(self, instance, validated_data):
        if controls := validated_data.get("controls"):
            existing_control = controls not in instance.controls
            if description := validated_data.get("description"):
                acronym = acronym_generator(instance.title)
                implemented_requirement = {
                    "uuid": str(uuid.uuid4()),
                    "props": [
                        {
                            "name": "security_control_type",
                            "uuid": str(uuid.uuid4()),
                            "value": "Allocated",
                        },
                        {
                            "name": "provider",
                            "uuid": str(uuid.uuid4()),
                            "value": "Blueprint_" + acronym,
                        },
                    ],
                    "control-id": controls[0],
                    "description": description,
                }
                if existing_control:
                    for implemented in (
                        instance.component_json.get("component-definition")
                        .get("components")[0]
                        .get("control-implementations")[0]
                        .get("implemented-requirements")
                    ):
                        if implemented.get("control-id") == controls[0]:
                            instance.component_json.get("component-definition").get(
                                "components"
                            )[0].get("control-implementations")[0].get(
                                "implemented-requirements"
                            ).remove(
                                implemented
                            )
                instance.component_json.get("component-definition").get("components")[
                    0
                ].get("control-implementations")[0].get(
                    "implemented-requirements"
                ).append(
                    implemented_requirement
                )
                instance.save()
                return instance
            else:
                raise serializers.ValidationError(
                    "Description must be provided for the control narrative"
                )
        else:
            raise serializers.ValidationError("Controls must be provided")


def acronym_generator(name):
    xs = name
    name_list = xs.split()
    acronym = ""
    for name in name_list:
        acronym + name[0]
    acronym = [name[0] for name in name_list]
    return "".join(acronym)
