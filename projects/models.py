from django.db import models

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
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)

    # Additional permissions to manage members.
    # (Add, change, delete, and view permissions are automatically created)
    class Meta:
        permissions = [
            ("can_add_members", "Can add members"),
            ("can_delete_members", "Can delete members"),
        ]

    def __str__(self):
        return "%s id=%d" % (self.title, self.id)

    def get_absolute_url(self):
        return f"/projects/{self.id}"
