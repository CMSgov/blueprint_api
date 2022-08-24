from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete, pre_save


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalogs"

    def ready(self):
        from catalogs.signals import add_controls, auto_delete_file_on_delete, auto_delete_file_on_change

        signal_config = [
            (post_save, add_controls, "ingest_catalog_controls"),
            (post_delete, auto_delete_file_on_delete, "remove_catalog_media"),
            (pre_save, auto_delete_file_on_change, "remove_stale_media"),
        ]

        for signal, receiver, uid in signal_config:
            signal.connect(receiver, sender="catalogs.Catalog", dispatch_uid=uid)
