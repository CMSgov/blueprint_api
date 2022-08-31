from django.apps import AppConfig
from django.contrib.auth.signals import user_login_failed
from django.db.models.signals import post_save


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from users.signals import add_default_user_perms, user_login_failed_callback

        post_save.connect(
            add_default_user_perms, sender="users.User", dispatch_uid="add_user_perms"
        )
        user_login_failed.connect(
            user_login_failed_callback, dispatch_uid="failed_login"
        )
