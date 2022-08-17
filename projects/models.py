import json
import logging

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import assign_perm

from access_management.permission_constants import (
    PROJECT_ADMIN_GROUP,
    manage_project_users_permission,
)
from access_management.utils import generate_groups_and_permission
from components.componentio import EmptyComponent

logger = logging.getLogger(__name__)


class Project(models.Model):
    class ImpactLevel(models.TextChoices):
        LOW = "low", _("Low")
        MODERATE = "moderate", _("Moderate")
        HIGH = "high", _("High")

    class LocationChoices(models.TextChoices):
        CMSAWS = "cms_aws", _("CMS AWS Commercial East-West")
        GOVCLOUD = "govcloud", _("CMS AWS GovCloud")
        AZURE = "azure", _("Microsoft Azure")
        OTHER = "other", _("Other")

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", _("Active")
        ARCHIVED = "archived", _("Archived")

    title = models.CharField(
        max_length=100, help_text="Name of the project", unique=False
    )
    acronym = models.CharField(
        max_length=20, help_text="Acronym for the name of the project", unique=False
    )
    creator = models.ForeignKey(
        to="users.User",
        on_delete=models.PROTECT,
        default=None,
        related_name="projects_created",
        help_text="User id of the project creator",
    )
    components = models.ManyToManyField(
        to="components.Component",
        blank=True,
        related_name="used_by_projects",
        help_text="Components that exist in the project",
    )
    catalog = models.ForeignKey(
        to="catalogs.Catalog",
        null=False,
        default=None,
        on_delete=models.PROTECT,
        related_name="projects_catalog",
        help_text="Catalog id that this project uses",
    )
    controls = models.ManyToManyField(
        to="catalogs.Controls",
        through="ProjectControl",
        related_name="project_controls",
    )
    impact_level = models.CharField(
        choices=ImpactLevel.choices,
        max_length=20,
        default=None,
        null=True,
        help_text="FISMA impact level of the project",
    )
    catalog_version = models.CharField(
        max_length=32,
        default=None,
        null=False,
        help_text="The Catalog version, for example ARS 3.1",
    )
    location = models.CharField(
        choices=LocationChoices.choices,
        max_length=100,
        default=None,
        null=True,
        help_text="Where the project is located",
    )
    status = models.CharField(
        choices=StatusChoices.choices,
        max_length=20,
        default=StatusChoices.ACTIVE,
        help_text="Status of the project",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)

    # Additional permissions to manage members.
    # (Add, change, delete, and view permissions are automatically created)
    class Meta:
        permissions = [
            ("can_add_members", "Can add members"),
            ("can_delete_members", "Can delete members"),
            manage_project_users_permission,
        ]

    def save(self, *args, **kwargs):
        cat = apps.get_model("catalogs", "Catalog")
        if self.impact_level and self.catalog_version:
            catalog = cat.objects.get(
                impact_level=self.impact_level, version=self.catalog_version
            )

        self.catalog = catalog
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def add_project_controls(instance: Project):
    controls = apps.get_model("catalogs", "Controls")
    catalog_controls = controls.objects.filter(catalog_id=instance.catalog)
    if catalog_controls.exists():
        instance.controls.set(
            catalog_controls,
            through_defaults={"status": ProjectControl.Status.NOT_STARTED},
        )


def add_default_component(instance: Project, group: Group):
    component = apps.get_model("components", "Component")

    default_component = EmptyComponent(
        title=f"{instance.title} private",
        description=f"{instance.title} default system component",
        catalog=instance.catalog,
    )
    default_json = default_component.create_component()
    default = component(
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

    try:
        instance.components.add(default)
    except Exception as e:
        logger.error(f"Could not create default component: {e}")


def add_components_for_project(instance: Project):
    component = apps.get_model("components", "Component")
    try:
        ociso_component = component.objects.get(title__iexact="ociso")
        instance.components.add(ociso_component)
        # if location aws add the aws component
        if instance.location == "cms_aws":
            aws_component = component.objects.get(title__iexact="aws")
            instance.components.add(aws_component)
    except ObjectDoesNotExist as e:
        logger.warning(f"Inherited components not found: {e}")


@receiver(post_save, sender=Project)
def post_create_setup(sender, instance, created, **kwargs):
    # only want to do this when a project is created
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
        add_default_component(instance, project_admin_group)

        # Add "standard" components
        add_components_for_project(instance)

        # Add catalog controls to project.
        add_project_controls(instance)


class ProjectControl(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", _("Not started")
        INCOMPLETE = "incomplete", _("Incomplete")
        COMPLETE = "completed", _("Completed")

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="to_project",
    )
    control = models.ForeignKey(
        "catalogs.Controls",
        on_delete=models.PROTECT,
        related_name="to_control",
    )
    status = models.CharField(
        choices=Status.choices,
        max_length=20,
        default=Status.NOT_STARTED,
        null=False,
        help_text="The Project Control status; completed, incomplete, or not started",
    )

    def __str__(self):
        return self.control.control_id
