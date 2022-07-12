from typing import List


class ComponentTools(object):
    def __init__(self, component):
        if isinstance(component, dict):
            self.component = component.get("component-definition")
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
