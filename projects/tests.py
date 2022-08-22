import json

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from catalogs.models import Catalog
from components.models import Component
from projects.models import Project, ProjectControl
from testing_utils import AuthenticatedAPITestCase
from users.models import User

TEST_COMPONENT_JSON_BLOB = {
    "component-definition": {
        "uuid": "ced875ac-c5e5-44a8-b34c-8ac4f8ab87e6",
        "metadata": {
            "title": "Cool Component",
            "published": "2021-09-04T02:25:34.558932+00:00",
            "last-modified": "2021-09-04T02:25:34.558936+00:00",
            "version": "1",
            "oscal-version": "1.0.0",
        },
        "components": [
            {
                "uuid": "e35accd9-0cc3-4a02-8557-01764c7cbe0b",
                "type": "software",
                "title": "Cool Component",
                "description": "This is a really cool component.",
                "control-implementations": [
                    {
                        "uuid": "f94a7f03-6ac5-4386-98eb-fa0392f26a1c",
                        "source": "https://raw.githubusercontent.com/NIST/catalog.json",
                        "description": "CMS_ARS_3_1",
                        "implemented-requirements": [
                            {
                                "uuid": "6698d762-5cdc-452e-9f9e-3074df5292c6",
                                "control-id": "ac-2",
                                "description": "This component statisfies a.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-1",
                                "description": "This component statisfies b.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-2",
                                "description": "This component statisfies c.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-3",
                                "description": "This component statisfies d.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "pe-3",
                                "description": "This component statisfies e.",
                            },
                        ],
                    }
                ],
            }
        ],
    }
}


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        cls.user = user

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        cls.test_component = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=test_catalog,
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=user,
            catalog=test_catalog,
        )

    def test_project_permissions(self):
        self.assertTrue(
            self.user.has_perms(("change_project", "view_project", "manage_project_users"), self.test_project)
        )

    def test_project_has_default_component(self):
        private_component = self.test_project.components.get(title="Pretty Ordinary Project private")
        self.assertEqual(private_component.status, Component.Status.SYSTEM)


class ProjectRequiredFieldsTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        cls.no_title_project = {
            "acronym": "NTP",
            "catalog_version": "NIST 800-53",
            "impact_level": "low",
            "location": "other",
            "catalog": test_catalog.id,
        }

        cls.no_acronym_project = {
            "title": "No Acronym Project",
            "catalog_version": "NIST 800-53",
            "impact_level": "low",
            "location": "other",
            "catalog": test_catalog.id,
        }

        cls.no_catalog_project = {
            "title": "No Catalog Project",
            "acronym": "NCP",
            "catalog_version": "NIST 800-53",
            "impact_level": "low",
            "location": "other",
            "catalog": None,
        }

    def test_title_required(self):
        response = self.client.post(
            reverse("project-list"),
            data=json.dumps(self.no_title_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_acronym_required(self):
        response = self.client.post(
            reverse("project-list"),
            data=json.dumps(self.no_acronym_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_catalog_required(self):
        response = self.client.post(
            reverse("project-list"),
            data=json.dumps(self.no_catalog_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectComponentsTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        test_component_2 = Component.objects.create(
            title="Cool Components",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=test_catalog,
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=test_user,
            catalog=test_catalog,
        )

        test_project.components.set(
            [
                test_component,
                test_component_2,
            ]
        )

        cls.test_project = test_project

    def test_get_project_with_components(self):
        response = self.client.get(
            reverse("project-detail", kwargs={"project_id": self.test_project.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        received_num_components = len(response.data["components"])
        received_components_count = response.data["components_count"]
        expected_num_components = 2

        # ensure that response includes all components in the project
        self.assertEqual(received_num_components, expected_num_components)

        # ensure that response includes accurate components_count
        self.assertEqual(received_components_count, expected_num_components)


class ProjectAddComponentViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        call_command(
            "load_catalog",
            name="NIST Test Catalog 2",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.MODERATE,
        )

        test_catalog, test_catalog_2 = Catalog.objects.order_by("name")

        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog_2,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_3 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=test_catalog,
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="moderate",
            location="other",
            creator=test_user,
            catalog=test_catalog,
        )

    def test_invalid_project(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {"component_id": 1, "project_id": 0},
        )
        self.assertEqual(resp.status_code, 404)

    def test_invalid_project_permissions(self):
        user, _ = User.objects.get_or_create(username="invalid_perms")
        token, _ = Token.objects.get_or_create(user=user)

        self.client.force_authenticate(user=user, token=token)

        resp = self.client.post(
            "/api/projects/add-component/",
            {"creator": 0, "component_id": 1, "project_id": self.test_project.id},
        )
        self.assertEqual(resp.status_code, 404)

    def test_invalid_component(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "component_id": 0,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 404)

    def test_different_catalog(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "component_id": self.test_component.id,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 400)

    def test_happy_path(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "component_id": self.test_component_2.id,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 200)


class ProjectControlPage(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        test_component_2 = Component.objects.create(
            title="Cool Components",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=test_user,
            catalog=test_catalog,
        )

        test_project.components.set(
            [
                test_component,
                test_component_2,
            ]
        )

        cls.test_project = test_project

    def test_get_control_page(self):
        resp = self.client.get(
            reverse(
                "project-get-control",
                kwargs={
                    "project_id": self.test_project.id,
                    "control_id": "ac-2",
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_control_page_data(self):
        resp = self.client.get(
            reverse(
                "project-get-control",
                kwargs={
                    "project_id": self.test_project.id,
                    "control_id": "ac-2",
                },
            )
        )
        self.assertIn("catalog_data", resp.data)
        self.assertIn("component_data", resp.data)
        self.assertIn("responsibility", resp.data["component_data"])
        self.assertIn("components", resp.data["component_data"])
        self.assertIn("inherited", resp.data["component_data"]["components"])
        self.assertIn("private", resp.data["component_data"]["components"])


class ProjectPostSaveAddComponentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        cls.test_component = Component.objects.create(
            title="ociso",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="aws",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_user = test_user
        cls.test_catalog = test_catalog

    def test_post_save_component_added_ocisco(self):
        project = Project.objects.create(
            title="Basic Project",
            acronym="BP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=self.test_user,
            catalog=self.test_catalog,
        )

        self.assertTrue(project.components.filter(title="ociso").exists())

    def test_post_save_component_added_both(self):
        project = Project.objects.create(
            title="Basic Project",
            acronym="BP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="cms_aws",
            creator=self.test_user,
            catalog=self.test_catalog,
        )

        for title in ("ociso", "aws"):
            with self.subTest(default_component=title):
                self.assertTrue(project.components.filter(title=title).exists())


class ProjectComponentSearchViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        test_component_2 = Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        test_component_3 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=test_catalog,
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=test_user,
            catalog=test_catalog,
        )
        test_project.components.set(
            [
                test_component,
                test_component_2,
                test_component_3,
            ]
        )

        cls.test_project = test_project

    def test_search_empty_request(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/search/", format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content).get("total_item_count"), 3)
        self.assertEqual(json.loads(resp.content).get("type_list")[0][0], "policy")
        self.assertEqual(json.loads(resp.content).get("type_list")[1][0], "software")

    def test_search_term_ociso(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/search/?search=OCISO",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.content).get("components")[0].get("title"), "OCISO"
        )
        self.assertEqual(json.loads(resp.content).get("total_item_count"), 1)

    def test_search_filter_type_software(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/search/?type=software",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.content).get("components")[0].get("type"), "software"
        )
        self.assertEqual(json.loads(resp.content).get("total_item_count"), 2)


class ProjectComponentNotAddedListViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create()

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=test_catalog,
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        Component.objects.create(
            title="private component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=test_catalog,
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
            status=1,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=test_user,
            catalog=test_catalog,
        )

    def test_ociso_component_not_returned(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/components-not-added/",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)

        content = resp.json()
        for test in content:
            with self.subTest():
                self.assertNotEqual(test.get("title"), "OCISO")

    def test_private_component_not_returned(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/components-not-added/",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.json()

        for test in content:
            with self.subTest():
                self.assertNotEqual(test.get("title"), "private component")


class RetrieveUpdateProjectControlViewTestCase(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        token = Token.objects.create(user=user)

        cls.user, cls.token = user, token

        call_command(
            "load_catalog",
            name="NIST Test Catalog",
            catalog_file="blueprintapi/testdata/NIST_SP-800-53_rev5_test.json",
            catalog_version="NIST 800-53",
            impact_level=Catalog.ImpactLevel.LOW,
        )

        test_catalog = Catalog.objects.get(name="NIST Test Catalog")

        cls.project = Project.objects.create(
            title="Test project",
            acronym="TP",
            catalog_version="NIST 800-53",
            impact_level="low",
            location="other",
            creator=user,
            catalog=test_catalog,
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user, token=self.token)

    def test_get_project_control(self):
        response = self.client.get(
            reverse("project-get-control", kwargs={"project_id": self.project.id, "control_id": "ac-1"})
        )
        self.assertEqual(response.status_code, 200)

        content = response.json()

        # Check top-level response structure
        self.assertTrue(
            all(item in content for item in ("status", "project", "control", "catalog_data", "component_data"))
        )

        # Check control data
        control = content["control"]
        expected = {
            "control_id": "ac-1",
            "control_label": "AC-1",
            "sort_id": "ac-01",
            "title": "Policy and Procedures"
        }

        for field, value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(control[field], value)

    def test_missing_control_returns_404(self):
        response = self.client.get(
            reverse("project-get-control", kwargs={"project_id": self.project.id, "control_id": "not-a-control"})
        )

        self.assertEqual(response.status_code, 404)

    def test_update_control_status(self):
        initial_response = self.client.get(
            reverse("project-get-control", kwargs={"project_id": self.project.id, "control_id": "ac-1"})
        )

        original_status = initial_response.json()["status"]

        response = self.client.patch(
            reverse("project-get-control", kwargs={"project_id": self.project.id, "control_id": "ac-1"}),
            json={"status": ProjectControl.Status.INCOMPLETE}
        )

        self.assertEqual(response.status_code, 200)
        content = response.json()

        self.assertNotEqual(original_status, content["status"])
        self.assertEqual(content["status"], ProjectControl.Status.INCOMPLETE)
