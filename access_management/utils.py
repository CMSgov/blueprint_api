from django.contrib.auth.models import Group, Permission
from guardian.shortcuts import assign_perm
from access_management.permission_constants import all_perms

PERMISSION_GROUP_SUFFIX = "_permission_group"


def generate_groups_and_permission(model_name, instance_name, instance):
    """
    Create a list of groups and assign associated permissions to that group
    using the naming convention and permission mapping in the permission_constants file.
    """
    groups = all_perms[model_name + PERMISSION_GROUP_SUFFIX]

    for suffix, permissions in groups.items():
        # append the object id to the partial name of the group
        # e.g. 10_project_admin_group
        group_name = instance_name + suffix

        # create a group based on the generated group name
        group = Group.objects.create(name=group_name)

        # loop through the array of partial permissions
        for permission in permissions:
            permission_code = permission[0]

            # Add the permission to the associated group that was just created.
            # The instance indicates the object that this object level permission is for.
            permission_obj = Permission.objects.get(codename=permission_code)
            group.permissions.add(permission_obj)  # Model-level permissions
            assign_perm(permission[0], group, instance)  # Object-level permissions
