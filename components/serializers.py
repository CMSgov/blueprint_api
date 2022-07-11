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
            user = User.objects.exclude(username=AnonymousUser).first()
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
    remove = Project.objects.filter(creator_id=user).filter(components=component_id)
    form_values = {
        "add": [],
        "remove": [],
    }
    for r in remove:
        form_values["remove"].append({"value": r.id, "label": r.title})
    add = Project.objects.filter(creator_id=user).exclude(pk__in=remove)
    for a in add:
        form_values["add"].append({"value": a.id, "label": a.title})
    return form_values
