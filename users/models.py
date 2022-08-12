from django.contrib.auth.models import AbstractUser, PermissionsMixin, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm


class User(AbstractUser):
    pass


@receiver(post_save, sender=User)
def add_default_user_perms(sender, instance, created, **kwargs):
    """After a User is created, assign object permissions to view/edit/delete to that user."""
    if created:
        user_perms = ('change_user', 'delete_user', 'view_user', )
        project_perms = ('add_project', 'change_project', 'view_project', )

        for code in user_perms + project_perms:
            try:
                permission = Permission.objects.get(codename=code)
            except Permission.DoesNotExist:
                break  # If the permissions don't exist, likely a setup step, so don't try and add perms

            instance.user_permissions.add(permission)  # Model permissions

            if code in user_perms:
                assign_perm(code, instance, instance)  # Object permissions for user
