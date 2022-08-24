import json

from components.componentio import ComponentTools
from components.models import Component


# noinspection PyUnusedLocal
def parse_component_json(sender, instance: Component, *args, **kwargs):
    """If the Component is an uploaded file, load the JSON and add it to the component_json field.
    """
    if instance.component_file:
        file = instance.component_file.file.open("r")
        instance.component_json = json.load(file)


# noinspection PyUnusedLocal
def add_description(sender, instance: Component, *args, **kwargs):
    """Get the Description from a given Component JSON object."""
    if instance.component_json and not instance.description:
        tool = ComponentTools(instance.component_json)
        instance.description = tool.get_component_value("description")


# noinspection PyUnusedLocal
def convert_to_lowercase(sender, instance: Component, *args, **kwargs):
    """Ensure the "type" field value is lowercase before saving."""
    if instance.component_json and not instance.type:
        tool = ComponentTools(instance.component_json)
        instance.type = tool.get_component_value("type").lower()
    elif instance.type:
        instance.type = instance.type.lower()


# noinspection PyUnusedLocal
def add_controls(sender, instance: Component, *args, **kwargs):
    """Add the controls from the component to the controls field."""
    if instance.component_json:
        tool = ComponentTools(instance.component_json)
        instance.controls = tool.get_control_ids()
