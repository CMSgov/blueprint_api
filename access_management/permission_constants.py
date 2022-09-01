# # Project permissions name and code
manage_project_users_permission = (
    "manage_project_users",
    "Can manage users on project",
)
add_project_permission = ("add_project", "Can add project")
change_project_permission = ("change_project", "Can edit project")
view_project_permission = ("view_project", "Can view project")

# # Project permission list associated with groups
project_admin_permissions = [
    add_project_permission,
    manage_project_users_permission,
    change_project_permission,
    view_project_permission,
]
project_contributor_permissions = [change_project_permission, view_project_permission]
project_view_only_permissions = [view_project_permission]

# Group names
PROJECT_ADMIN_GROUP = "_project_admin_group"
PROJECT_CONTRIBUTOR_GROUP = "_project_contributor_group"
PROJECT_VIEW_ONLY_GROUP = "_project_view_only_group"

# Group and permission list mappings
project_permission_group = {
    PROJECT_ADMIN_GROUP: project_admin_permissions,
    PROJECT_CONTRIBUTOR_GROUP: project_contributor_permissions,
    PROJECT_VIEW_ONLY_GROUP: project_view_only_permissions,
}

all_perms = vars()
