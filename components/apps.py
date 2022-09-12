from django.apps import AppConfig
from django.db.models.signals import pre_save


class ComponentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "components"

    def ready(self):
        from components.signals import (
            parse_component_json, add_description, convert_to_lowercase, add_controls, add_supported_catalog_versions
        )

        signal_setup = [
            (parse_component_json, "parse_component_json"),
            (add_description, "parse_component_description"),
            (convert_to_lowercase, "lower_case_component_type"),
            (add_controls, "parse_component_controls"),
            (add_supported_catalog_versions, "add_supported_catalog_versions")
        ]

        for receiver, uid in signal_setup:
            pre_save.connect(receiver, sender="components.Component", dispatch_uid=uid)
