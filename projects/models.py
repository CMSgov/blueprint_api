import json
import logging

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from access_management.permission_constants import (
    PROJECT_ADMIN_GROUP,
    manage_project_users_permission,
)
from access_management.utils import generate_groups_and_permission
from catalogs.models import Catalog
from components.componentio import EmptyComponent
from components.models import Component
from users.models import User

logger = logging.getLogger(__name__)


class Project(models.Model):
    title = models.CharField(
        max_length=100, help_text="Name of the project", unique=False
    )
    acronym = models.CharField(
        max_length=20, help_text="Acronym for the name of the project", unique=False
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        default=None,
        related_name="projects_created",
        help_text="User id of the project creator",
    )
    components = models.ManyToManyField(
        Component,
        blank=True,
        related_name="used_by_projects",
        help_text="Components that exist in the project",
    )
    catalog = models.ForeignKey(
        Catalog,
        null=False,
        default=None,
        on_delete=models.PROTECT,
        related_name="projects_catalog",
        help_text="Catalog id that this project uses",
    )
    catalog_version = models.CharField(
        max_length=64,
        default="CMS ARS 3.1",
        blank=False,
        help_text="The Catalog version, for example, NIST 800-53r5",
    )
    IMPACT_LEVEL_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("pii/phi", "PII or PHI"),
    ]
    impact_level = models.CharField(
        choices=IMPACT_LEVEL_CHOICES,
        max_length=20,
        null=True,
        default="moderate",
        help_text="FISMA impact level of the project",
    )
    LOCATION_CHOICES = [
        ("cms_aws", "CMS AWS Commercial East-West"),
        ("govcloud", "CMS AWS GovCloud"),
        ("azure", "Microsoft Azure"),
        ("other", "Other"),
    ]
    location = models.CharField(
        choices=LOCATION_CHOICES,
        max_length=100,
        default=None,
        null=True,
        help_text="Where the project is located",
    )
    STATUS_CHOICES = [
        ("active", "Active"),
        ("archived", "Archived"),
    ]
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=20,
        default="active",
        help_text="Status of the project",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)

    class Meta:
        """
        Additional permissions to manage members.
        (Add, change, delete, and view permissions are automatically created)
        """

        permissions = [
            ("can_add_members", "Can add members"),
            ("can_delete_members", "Can delete members"),
            manage_project_users_permission,
        ]

    def save(self, *args, **kwargs):
        version = getattr(self, "catalog_version")
        impact = getattr(self, "impact_level")
        if version and impact:
            catalog = Catalog.objects.filter(
                version=version, impact_level=impact
            ).first()
            self.catalog = catalog
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Project)
def add_default_component(sender, instance, **kwargs):
    if kwargs["created"]:
        default_component = EmptyComponent(
            title=f"{instance.title} private",
            description=f"{instance.title} default system component",
            catalog=instance.catalog,
        )
        default_json = default_component.create_component()
        default = Component(
            title=f"{instance.title} private",
            description=f"{instance.title} default system component",
            component_json=json.loads(default_json),
            catalog_id=instance.catalog.id,
            status=1,
        )
        default.save()

        try:
            instance.components.add(default)
        except Exception as e:
            logger.error(f"Could not create default component: {e}")


@receiver(post_save, sender=Project)
def create_groups_for_project(sender, instance, **kwargs):
    # only want to do this when a project is created
    if kwargs["created"]:
        try:
            # Create groups for project with associated permissions
            generate_groups_and_permission(
                instance._meta.model_name, str(instance.id), instance
            )

            # add the creator user to the project admin group by default
            project_admin_group = Group.objects.get(
                name=str(instance.id) + PROJECT_ADMIN_GROUP
            )
            instance.creator.groups.add(project_admin_group)

        except Exception as e:
            # TODO: log failure
            raise e
    else:
        print("Object not created yet.")


@receiver(post_save, sender=Project)
def add_components_for_project(sender, instance, **kwargs):
    if kwargs["created"]:
        try:
            ociso_component = Component.objects.get(title__iexact="ociso")
            instance.components.add(ociso_component)
            # if location aws add the aws component
            if instance.location == "cms_aws":
                aws_component = Component.objects.get(title__iexact="aws")
                instance.components.add(aws_component)
        except ObjectDoesNotExist as e:
            logger.warning(f"Inherited components not found: {e}")


class Control(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 1, "Not started"
        INCOMPLETE = 2, "Incomplete"
        COMPLETE = 3, "Complete"

    class Responsibility(models.IntegerChoices):
        ALLOCATED = 1, "Allocated"
        SHARED = 2, "Shared"
        INHERITED = 3, "Inherited"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    control_id = models.CharField(
        max_length=12,
        unique=False,
        blank=False,
    )
    description = models.JSONField(
        blank=False,
        help_text="Control description OSCAL JSON formatted.",
    )
    implementation = models.TextField(
        blank=True,
        help_text="Control implementation text.",
    )
    guidance = models.TextField(
        blank=True,
        help_text="Control guidance text.",
    )
    status = models.IntegerField(
        default=Status.NOT_STARTED,
        choices=Status.choices,
    )
    responsibility = models.IntegerField(
        default=Responsibility.ALLOCATED,
        choices=Responsibility.choices,
    )

    def get_status(self):
        return self.Status(self.status).label

    def get_responsibility(self):
        return self.Responsibility(self.responsibility).label
