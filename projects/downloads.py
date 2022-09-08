from blueprintapi.oscal.oscal import Metadata
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
    Party,
    Resource,
    Role,
    SecurityImpactLevel,
    SystemCharacteristics,
    SystemImplementation,
    SystemInformation,
    SystemSecurityPlan,
    SystemStatus,
)
from components.componentio import ComponentTools
from projects.models import Project


class OscalSSP:
    metadata = None
    sec_impact_level = None
    import_profile = None
    information_type = None
    system_information = None
    system_characteristics = None
    component_ref = {}
    system_implementation = None
    control_implementations = None
    back_matter = None

    def __init__(self, project: Project):
        self.project = project

    def get_ssp(self):
        self.set_metadata()
        self.set_roles()
        self.set_impact_level()
        self.set_import_profile()
        self.set_information_type()
        self.set_system_information()
        self.set_system_characteristics()
        self.add_components()
        self.add_implemented_requirements()
        self.set_back_matter()
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
        preparer = Role(id="prepared_by", title="Prepared by")
        fen = Party(
            type="person",
            name="Fen",
            email_address="fen@example.com"
        )  # Example
        self.metadata.parties = ([fen],)
        self.metadata.roles = [preparer]

    def set_impact_level(self):
        self.sec_impact_level = SecurityImpactLevel(
            security_objective_confidentiality=f"fips-199-{self.project.impact_level}",
            security_objective_availability=f"fips-199-{self.project.impact_level}",
            security_objective_integrity=f"fips-199-{self.project.impact_level}",
        )

    def set_import_profile(self):
        self.import_profile = ImportProfile(href=self.project.catalog.source)

    def set_information_type(self):
        self.information_type = InformationType(
            title=self.project.title,
            description=self.project.title,
            confidentiality_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
            integrity_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
            availability_impact=Impact(base=f"fips-199-{self.project.impact_level}"),
        )

    def set_system_information(self):
        self.system_information = SystemInformation(
            information_types=[self.information_type]
        )

    def set_system_characteristics(self):
        self.system_characteristics = SystemCharacteristics(
            system_name=self.project.title,
            description=self.project.acronym,
            security_sensitivity_level=self.project.impact_level,
            system_information=self.system_information,
            security_impact_level=self.sec_impact_level,
            authorization_boundary=NetworkDiagram(description="Authorization Boundary"),
            status=SystemStatus(state="operational"),
        )

    def add_components(self):
        self.system_implementation = SystemImplementation()
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
            description="EXAMPLE SSP", implemented_requirements=[]
        )
        for control in self.project.controls.all():
            implemented_requirement = ImplementedRequirement(
                control_id=control.control_id,
                statements=[],
            )
            for component in self.project.components.all():
                cmpt = ComponentTools(component.component_json)
                if control.control_id in component.controls:
                    ctrl = cmpt.get_control_by_id(control.control_id)
                    implemented_requirement.add_by_component(
                        ByComponent(
                            component_uuid=self.component_ref[component.title],
                            description=ctrl[0].get("description"),
                        )
                    )
            self.control_implementations.implemented_requirements.append(implemented_requirement)

    def set_back_matter(self):
        self.back_matter = BackMatter(resources=[Resource(title="Test Resource")])
