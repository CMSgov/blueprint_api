from django.contrib.auth.models import AbstractUser, PermissionsMixin, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm


class User(AbstractUser, PermissionsMixin):
    pass


@receiver(post_save, sender=User)
def add_default_user_perms(sender, instance, created, **kwargs):
    """After a User is created, assign object permissions to view/edit/delete to that user."""
    if created:
        for code in ('change_user', 'delete_user', 'view_user', ):
            permission = Permission.objects.get(codename=code)
            instance.user_permissions.add(permission)
            assign_perm(code, instance, instance)
