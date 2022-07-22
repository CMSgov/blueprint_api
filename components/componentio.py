import json
from typing import List

from blueprintapi.oscal import component as oscal_component
from blueprintapi.oscal.oscal import Metadata


class ComponentTools(object):
    def __init__(self, component):
        if isinstance(component, dict):
            self.component = component.get("component-definition")
        elif isinstance(component, str):
            comp = json.loads(component)
            self.component = comp.get("component-definition")
        else:
            return None

    def get_components(self):
        components: List[dict] = []
        if self.component and "components" in self.component:
            components = self.component["components"]
        return components

    def get_component_value(self, key):
        component = self.get_components()
        if component:
            return component[0].get(key)

    def get_implemenations(self):
        impls: List[dict] = []
        component = self.get_components()
        for c in component:
            if "control-implementations" in c:
                impls = c.get("control-implementations")
        return impls

    def get_controls(self):
        controls: List[dict] = []
        implementations = self.get_implemenations()
        if implementations:
            for ci in implementations:
                controls = ci.get("implemented-requirements")
        return controls

    def get_control_ids(self) -> List:
        controls = self.get_controls()
        ids = [item.get("control-id") for item in controls]
        return ids

    def get_control_by_id(self, control_id):
        controls = self.get_controls()
        control = [(c) for c in controls if c.get("control-id") == control_id]
        return control

    def get_control_props(self, control, prop):
        if "props" in control and isinstance(control.get("props"), list):
            for p in control.get("props"):
                if p.get("name") == prop:
                    return p.get("value")


class EmptyComponent(object):
    """Create an empty OSCAL Component object."""

    def __init__(self, title: str, description: str, catalog: object):
        self.title = title
        self.description = description
        self.catalog = catalog

    def add_metadata(self):
        self.md = Metadata(title=self.title, version="unknown")

    def add_components(self):
        self.add_control_implementations()
        self.c = oscal_component.Component(
            title=self.title,
            description=self.title,
            type="software",
        )
        self.c.control_implementations.append(self.ci)

    def add_control_implementations(self):
        self.ci = oscal_component.ControlImplementation(
            description=self.catalog.name,
            source=self.catalog.source,
        )
        self.ci.implemented_requirements = []

    def add_component_definition(self):
        self.add_metadata()
        self.add_components()
        self.cd = oscal_component.ComponentDefinition(metadata=self.md)
        self.cd.add_component(self.c)

    def create_component(self):
        self.add_component_definition()
        self.component = oscal_component.Model(component_definition=self.cd)
        return self.component.json(indent=None)
