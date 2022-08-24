from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"

    def ready(self):
        from projects.signals import post_create_setup, add_catalog

        pre_save.connect(add_catalog, sender="projects.Project", dispatch_uid="project_pre_save_setup")
        post_save.connect(post_create_setup, sender="projects.Project", dispatch_uid="project_post_save_setup")
