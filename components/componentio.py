import json
from typing import Any, List, Optional, Union

from blueprintapi.oscal import component as oscal_component
from blueprintapi.oscal.oscal import Metadata
from catalogs.models import Catalog


class ComponentTools:
    def __init__(self, component: Union[dict, str]):
        if isinstance(component, dict):
            self.component = component.get("component-definition")
        elif isinstance(component, str):
            comp = json.loads(component)
            self.component = comp.get("component-definition")
        else:
            raise TypeError(f"component can be dict or str. Received: {type(component)}.")

    def get_components(self) -> List[dict]:
        return self.component.get("components") or []

    def get_component_value(self, key: str) -> Optional[Any]:
        component = self.get_components()
        if component:
            return component[0].get(key)

    def get_implemenations(self) -> List[dict]:
        impls = []
        components = self.get_components()
        for component in components:
            if "control-implementations" in component:
                impls = component.get("control-implementations")

        return impls

    def get_controls(self) -> List[dict]:
        controls = []
        implementations = self.get_implemenations()
        if implementations:
            for control_implementation in implementations:
                controls = control_implementation.get("implemented-requirements")

        return controls

    def get_control_ids(self) -> List:
        controls = self.get_controls()
        ids = [item.get("control-id") for item in controls]
        return ids

    def get_control_by_id(self, control_id) -> List[dict]:
        controls = self.get_controls()
        control = [control for control in controls if control.get("control-id") == control_id]

        return control

    @staticmethod
    def get_control_props(control: dict, name: str) -> Optional[Any]:
        if "props" in control and isinstance(control.get("props"), list):
            for prop in control.get("props"):
                if prop.get("name") == name:
                    return prop.get("value")


def create_empty_component_json(title: str, catalog: Catalog) -> str:
    control_implementation = oscal_component.ControlImplementation(
        description=catalog.name,
        source=catalog.source,
    )
    control_implementation.implemented_requirements = []

    component = oscal_component.Component(
        title=title,
        description=title,
        type="software",
    )
    component.control_implementations.append(control_implementation)

    component_definition = oscal_component.ComponentDefinition(
        metadata=Metadata(title=title, version="unknown")
    )
    component_definition.add_component(component)

    return oscal_component.Model(component_definition=component_definition).json(indent=4)
