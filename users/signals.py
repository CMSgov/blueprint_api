import logging

from django.contrib.auth.models import Permission
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from users.models import User

logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
def add_default_user_perms(sender, instance: User, created: bool, **kwargs):
    """After a User is created, assign object permissions to view/edit/delete to that user."""
    if created:
        user_perms = (
            "change_user",
            "delete_user",
            "view_user",
        )
        project_perms = (
            "add_project",
            "change_project",
            "view_project",
        )
        component_perms = (
            "add_component",
            "change_component",
            "view_component",
        )
        project_control_perms = (
            "add_projectcontrol",
            "change_projectcontrol",
            "view_projectcontrol",
        )

        for code in (
            component_perms + project_perms + user_perms + project_control_perms
        ):
            try:
                permission = Permission.objects.get(codename=code)
            except Permission.DoesNotExist:
                break  # If the perms don't exist, likely a setup step, so don't try and add perms

            instance.user_permissions.add(permission)  # Model permissions

            if code in user_perms:
                assign_perm(code, instance, instance)  # Object permissions for user


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    user = credentials.get("username")
    logger.warning(f"Log in failed for: {user}")
