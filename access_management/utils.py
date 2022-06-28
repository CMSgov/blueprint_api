from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

PERMISSION_GROUP_SUFFIX = "_permission_group"
current_module_variables = vars()


def generate_groups_and_permission(model_name, instance_name, instance):
    """
    Create a list of groups and assign associated permissions to that group
    using the naming convention and permission mapping in the permission_constants file.
    """
    groups = current_module_variables[model_name + PERMISSION_GROUP_SUFFIX]

    for k, v in groups.items():
        try:
            # append the object id to the partial name of the group
            # e.g. 10_project_admin_group
            group_name = instance_name + k

            # create a group based on the generated group name
            group = Group.objects.create(name=group_name)

            # loop through the array of partial permissions
            for permission in v:
                # Add the permission to the associated group that was just created.
                # The instance indicates the object that this object level permission is for.
                assign_perm(permission[0], group, instance)

        except Exception as e:
            raise e
