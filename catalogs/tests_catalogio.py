from typing import List

from django.core.files import File
from django.test import TestCase

from .catalogio import CatalogTools as Tools
from .models import Catalog


class CatalogModelTest(TestCase):
    @classmethod
    def setUp(self):
        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cat = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
            )
        self.catalog = Tools(cat.file_name.path)

    def test_load_catalog(self):
        """Test loading a Catalog"""
        self.assertIsInstance(self.catalog, Tools)

    def test_catalog_title(self):
        """Get the Catalog title"""
        self.assertEquals(
            self.catalog.catalog_title, "NIST SP 800-53 Rev 5 Controls Test Catalog"
        )

    # Groups
    def test_get_groups(self):
        """Get Catalog Groups as List"""
        groups = self.catalog.get_groups()
        self.assertIsInstance(groups, List)
        self.assertEquals(len(groups), 20)

    def test_get_group_ids(self):
        """Test getting the Groups for a Catalog"""
        groups = self.catalog.get_group_ids()
        self.assertIn("ac", groups)

    def test_get_group_title_by_id(self):
        """Test getting the Group title by ID"""
        title = self.catalog.get_group_title_by_id("ac")
        self.assertEquals(title, "Access Control")

    def test_get_group_id_by_control_id(self):
        """Test getting a Group ID from a Control ID"""
        group_id = self.catalog.get_group_id_by_control_id("ac-1")
        self.assertEquals(group_id, "ac")

    # Controls
    def test_get_controls(self):
        """Test getting all controls"""
        controls = self.catalog.get_controls()
        self.assertEquals(len(controls), 53)
        self.assertEquals(controls[0].get("title"), "Policy and Procedures")

    def test_get_control_by_id(self):
        """Get a control by the Control ID"""
        control = self.catalog.get_control_by_id("ac-2")
        self.assertEquals(control.get("title"), "Account Management")
        self.assertIsInstance(control.get("params"), List)

    def test_get_control_statement(self):
        """Get the control statement with placeholders"""
        control = self.catalog.get_control_by_id("ac-2")
        prose = self.catalog.get_control_statement(control)
        self.assertIsInstance(prose, List)

    def test_get_controls_all(self):
        controls = self.catalog.get_controls_all()
        self.assertIsInstance(controls, List)
        self.assertIsInstance(controls[0], dict)

    def test_get_controls_all_ids(self):
        controls = self.catalog.get_controls_all_ids()
        self.assertIsInstance(controls, List)
        self.assertEquals(len(controls), 186)

    def test_get_control_property_by_name(self):
        control = self.catalog.get_control_by_id("ac-2")
        prop = self.catalog.get_control_property_by_name(control, "label")
        self.assertEquals(prop, "AC-2")

    def test_get_control_part_by_name(self):
        control = self.catalog.get_control_by_id("ac-2")
        part = self.catalog.get_control_part_by_name(control, "statement")
        self.assertIsInstance(part, dict)

    # Params
    def test_get_control_parameter_label_by_id(self):
        control = self.catalog.get_control_by_id("ac-2")
        label = self.catalog.get_control_parameter_label_by_id(control, "ac-02_odp.01")
        self.assertEquals(label, "prerequisites and criteria")

    def test_get_control_parameters(self):
        control = self.catalog.get_control_by_id("ac-2")
        params = self.catalog.get_control_parameters(control)
        self.assertIsInstance(params, dict)
        self.assertIn("ac-02_odp.01", params)

    def test_get_resource_by_uuid(self):
        resource = self.catalog.get_resource_by_uuid(
            "91f992fb-f668-4c91-a50f-0f05b95ccee3"
        )
        self.assertIn("uuid", resource)
        self.assertEquals(resource.get("title"), "32 CFR 2002")

    def test_get_next_control_by_id(self):
        """Get a control by the Control ID"""
        control = self.catalog.get_next_control_by_id("ac-1")
        self.assertEquals(control, "ac-2")
