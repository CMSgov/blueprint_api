import re
from typing import List

from blueprintapi.oscal.oscal import Metadata, Property
from blueprintapi.oscal.ssp import (
    BackMatter,
    ByComponent,
    Component,
    ControlImplementation,
    Impact,
    ImplementedRequirement,
    ImportProfile,
    InformationType,
    Model,
    NetworkDiagram,
    Resource,
    Role,
    SecurityImpactLevel,
    SystemCharacteristics,
    SystemImplementation,
    SystemInformation,
    SystemSecurityPlan,
    SystemStatus,
    User,
)
from components.componentio import ComponentTools
from projects.models import Project


class OscalSSP:
    def __init__(self, project: Project, extras: str):
        self.project = project
        self.extras = extras
        self.metadata = None
        self.set_metadata()
        self.users: List = []
        self.set_roles()
        self.sec_impact_level = None
        self.set_impact_level()
        self.import_profile = ImportProfile(href=self.project.catalog.source)
        self.information_type = None
        self.set_information_type()
        self.system_information = SystemInformation(
            information_types=[self.information_type]
        )
        self.system_characteristics = None
        self.set_system_characteristics()
        self.component_ref: dict = {}
        self.system_implementation = None
        self.add_components()
        self.control_implementations = None
        self.add_implemented_requirements()
        self.back_matter = None
        # self.set_back_matter()

    def get_ssp(self):
        ssp = SystemSecurityPlan(
            metadata=self.metadata,
            import_profile=self.import_profile,
            system_characteristics=self.system_characteristics,
            system_implementation=self.system_implementation,
            control_implementation=self.control_implementations,
            back_matter=self.back_matter,
        )
        root = Model(system_security_plan=ssp)
        return root.json(indent=2)

    def set_metadata(self):
        self.metadata = Metadata(
            title=self.project.title,
            version="0.1",
            oscal_version="1.0.2",
        )

    def set_roles(self):
        self.metadata.roles = []
        ids = []
        properties = None
        for stakeholder in self.extras.get("stakeholders"):
            title, short_name, role_id = "", "", ""
            for key, value in stakeholder.items():
                if re.search(r"\((.*?)\)", key):
                    short = re.search(r"\((.*?)\)", key)
                    short_name = short.group(1)
                    title = key[: key.find(" (")]
                else:
                    title = key
                    words = title.split()
                    short = [word[0] for word in words]
                    short_name = "".join(short)
                properties = Property(
                    name=value.get("props").get("name"),
                    value=value.get("props").get("value"),
                )
            role_id = title.replace(" ", "-").lower()
            if title and role_id not in ids:
                ids.append(role_id)
                self.users.append(
                    User(
                        role_ids=[role_id],
                        title=title,
                        short_name=short_name,
                        props=[properties],
                    )
                )
                self.metadata.roles.append(
                    Role(
                        title=title.strip(),
                        short_name=short_name.upper(),
                        id=role_id,
                    )
                )

    def set_impact_level(self):
        self.sec_impact_level = SecurityImpactLevel(
            security_objective_confidentiality=f"fips-199-{self.project.impact_level}",
            security_objective_availability=f"fips-199-{self.project.impact_level}",
            security_objective_integrity=f"fips-199-{self.project.impact_level}",
        )

    def set_information_type(self):
        self.information_type = InformationType(
            title=self.project.title,
            description=self.project.title,
            confidentiality_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
            integrity_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
            availability_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
        )

    def set_system_characteristics(self):
        self.system_characteristics = SystemCharacteristics(
            system_name=self.project.title,
            description=self.project.acronym,
            security_sensitivity_level=self.project.impact_level,
            system_information=self.system_information,
            security_impact_level=self.sec_impact_level,
            authorization_boundary=NetworkDiagram(
                description="INSERT AUTHORIZATION BOUNDARY DESCRIPTION HERE"
            ),
            status=SystemStatus(state="operational"),
        )

    def add_components(self):
        self.system_implementation = SystemImplementation()
        self.system_implementation.users = self.users
        for component in self.project.components.all():
            if component.status == 1:
                cpt = Component(
                    title="This System",
                    type="this-system",
                    description=self.project.title,
                    status=SystemStatus(state="operational"),
                )
            else:
                cpt = Component(
                    title=component.title,
                    type=component.type,
                    description=component.description,
                    status=SystemStatus(state="operational"),
                )
            self.system_implementation.add_component(cpt)
            self.component_ref[component.title] = cpt.uuid

    def add_implemented_requirements(self):
        self.control_implementations = ControlImplementation(
            description="[INSERT SYSTEM DESCRIPTION HERE]", implemented_requirements=[]
        )
        for control in self.project.controls.all():
            implemented_requirement = ImplementedRequirement(
                control_id=control.control_id,
                statements=[],
            )
            for component in self.project.components.all():
                cmp = ComponentTools(component.component_json)
                if control.control_id in component.controls:
                    ctrl = cmp.get_control_by_id(control.control_id)
                    implemented_requirement.add_by_component(
                        ByComponent(
                            component_uuid=self.component_ref[component.title],
                            description=ctrl[0].get("description"),
                        )
                    )
                    self.control_implementations.implemented_requirements.append(
                        implemented_requirement
                    )

    def set_back_matter(self):
        self.back_matter = BackMatter(resources=[Resource(title="Test Resource")])
