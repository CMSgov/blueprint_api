import logging

from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from access_management.permission_constants import manage_project_users_permission

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

    def __str__(self):
        return self.title


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
