from django.apps import AppConfig
from django.db.models.signals import post_save

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from users.signals import add_default_user_perms

        post_save.connect(add_default_user_perms, sender="users.User", dispatch_uid="add_user_perms")
