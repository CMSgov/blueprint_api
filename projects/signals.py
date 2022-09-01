import json
import logging

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from guardian.shortcuts import assign_perm

from access_management.permission_constants import PROJECT_ADMIN_GROUP
from access_management.utils import generate_groups_and_permission
from catalogs.models import Catalog, Controls
from components.componentio import create_empty_component_json
from components.models import Component
from projects.models import Project, ProjectControl

logger = logging.getLogger(__name__)


def _add_project_controls(instance: Project):
    catalog_controls = Controls.objects.filter(catalog_id=instance.catalog)
    if catalog_controls.exists():
        instance.controls.set(
            catalog_controls,
            through_defaults={"status": ProjectControl.Status.NOT_STARTED},
        )


def _add_default_component(instance: Project, group: Group):
    default_json = create_empty_component_json(
        title=f"{instance.title} private",
        catalog=instance.catalog,
    )
    default = Component(
        title=f"{instance.title} private",
        description=f"{instance.title} default system component",
        component_json=json.loads(default_json),
        catalog_id=instance.catalog.id,
        status=1,
    )
    default.save()

    # Assign default permissions to "system"/"default" component
    codenames = (
        "add_component",
        "change_component",
        "view_component",
    )
    for codename in codenames:
        permission = Permission.objects.get(codename=codename)
        group.permissions.add(permission)
        assign_perm(codename, group, default)

    instance.components.add(default)


def _add_components_for_project(instance: Project):
    try:
        ociso_component = Component.objects.get(title__iexact="ociso")
        instance.components.add(ociso_component)
        # if location aws add the aws component
        if instance.location == "cms_aws":
            aws_component = Component.objects.get(title__iexact="aws")
            instance.components.add(aws_component)
    except Component.DoesNotExist as exc:
        logger.warning("Inherited components not found: %s", exc)


# noinspection PyUnusedLocal
def post_create_setup(sender, instance: Project, created: bool, **kwargs):  # pylint: disable=unused-argument
    """Additional project set up after successful creation"""
    if created:
        # Create groups for project with associated permissions
        generate_groups_and_permission(
            instance._meta.model_name, str(instance.id), instance
        )

        # add the creator user to the project admin group by default
        project_admin_group = Group.objects.get(
            name=str(instance.id) + PROJECT_ADMIN_GROUP
        )
        instance.creator.groups.add(project_admin_group)

        # Add default/system component; depends on group existing
        _add_default_component(instance, project_admin_group)

        # Add "standard" components
        _add_components_for_project(instance)

        # Add catalog controls to project.
        _add_project_controls(instance)


# noinspection PyUnusedLocal
def add_catalog(sender, instance: Project, **kwargs):  # pylint: disable=unused-argument
    if not hasattr(instance, "catalog"):
        if not (instance.impact_level and instance.catalog_version):
            raise ValidationError("Creating a new project requires impact_level and catalog_version.")

        try:
            catalog = Catalog.objects.get(impact_level=instance.impact_level, version=instance.catalog_version)
            logger.info("Adding matching catalog, %s to project, %s", catalog, instance)
            instance.catalog = catalog
        except Catalog.DoesNotExist as exc:
            raise Catalog.DoesNotExist("Could not determine a matching catalog for project.") from exc
