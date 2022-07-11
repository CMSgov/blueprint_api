from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from access_management.permission_constants import (
    PROJECT_ADMIN_GROUP,
    manage_project_users_permission,
)
from access_management.utils import generate_groups_and_permission
from catalogs.models import Catalog
from components.models import Component
from users.models import User


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
    IMPACT_LEVEL_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("pii/phi", "PII or PHI"),
    ]
    impact_level = models.CharField(
        choices=IMPACT_LEVEL_CHOICES,
        max_length=20,
        default=None,
        null=True,
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
