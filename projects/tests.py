import json

from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse
from guardian.shortcuts import get_perms
from rest_framework import status

from catalogs.models import Catalog
from components.models import Component
from projects.models import Project
from users.models import User

from .serializers import ProjectSerializer

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
                        "source": "https://raw.githubusercontent.com/usnistgov/oscal-content/main/\
                            nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json",
                        "description": "CMS_ARS_3_1",
                        "implemented-requirements": [
                            {
                                "uuid": "6698d762-5cdc-452e-9f9e-3074df5292c6",
                                "control-id": "ac-2.1",
                                "description": "This component statisfies 2.1.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "ac-2.2",
                                "description": "This component statisfies b.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "ac-2.3",
                                "description": "This component statisfies c.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "ac-2.4",
                                "description": "This component statisfies d.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "ac-2.5",
                                "description": "This component statisfies e.",
                            },
                        ],
                    }
                ],
            }
        ],
    }
}

# initialize the APIClient app
client = Client()


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()
        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )

        cls.test_component = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog_version="NIST 800-53r5",
        )

    # Tests for field labels
    def test_title_label(self):
        project = self.test_project
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_acronym_label(self):
        project = self.test_project
        field_label = project._meta.get_field("acronym").verbose_name
        self.assertEqual(field_label, "acronym")

    def test_impact_level_label(self):
        project = self.test_project
        field_label = project._meta.get_field("impact_level").verbose_name
        self.assertEqual(field_label, "impact level")

    def test_location_label(self):
        project = self.test_project
        field_label = project._meta.get_field("location").verbose_name
        self.assertEqual(field_label, "location")

    def test_status_label(self):
        project = self.test_project
        field_label = project._meta.get_field("status").verbose_name
        self.assertEqual(field_label, "status")

    def test_creator_label(self):
        project = self.test_project
        field_label = project._meta.get_field("creator_id").verbose_name
        self.assertEqual(field_label, "creator")

    def test_created_label(self):
        project = self.test_project
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = self.test_project
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = self.test_project
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_acronym_max_length(self):
        project = self.test_project
        max_length = project._meta.get_field("acronym").max_length
        self.assertEqual(max_length, 20)

    def test_impact_level_max_length(self):
        project = self.test_project
        max_length = project._meta.get_field("impact_level").max_length
        self.assertEqual(max_length, 20)

    def test_location_max_length(self):
        project = self.test_project
        max_length = project._meta.get_field("location").max_length
        self.assertEqual(max_length, 100)

    def test_status_max_length(self):
        project = self.test_project
        max_length = project._meta.get_field("status").max_length
        self.assertEqual(max_length, 20)

    # Tests for default value
    def test_status_default_value(self):
        # create a project without specifying status
        Project.objects.create(
            title="Basic Project",
            acronym="BP",
            impact_level="low",
            location="other",
            creator=self.test_user,
            catalog_version="NIST 800-53r5",
        )

        # ensure project status defaults as expected
        expected_status = "active"
        project = Project.objects.get(title="Basic Project")
        status = project.status
        self.assertEqual(status, expected_status)

        Project.objects.create(
            title="Test Project",
            acronym="TP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=1),
            catalog_version="NIST 800-53r5",
        )
        project = Project.objects.get(title="Test Project")
        user = User.objects.get(id=1)
        self.assertEqual("change_project" in get_perms(user, project), True)
        self.assertEqual("view_project" in get_perms(user, project), True)
        self.assertEqual("manage_project_users" in get_perms(user, project), True)

    def test_default_component(self):
        project = self.test_project
        has_default = False
        for c in project.components.all():
            if c.title == "Pretty Ordinary Project private" and c.status == 1:
                has_default = True

        self.assertTrue(has_default)

    def test_controls(self):
        controls = Project.objects.get(pk=self.test_project.id).control_set.all()
        self.assertEqual(len(controls), 186)


class ProjectRequiredFieldsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )

        cls.no_title_project = {
            "acronym": "NTP",
            "impact_level": "low",
            "location": "other",
            "creator": cls.test_user.id,
            "catalog": cls.test_catalog.id,
        }

        cls.no_acronym_project = {
            "title": "No Acronym Project",
            "impact_level": "low",
            "location": "other",
            "creator": cls.test_user.id,
            "catalog_version": "NIST 800-53r5",
        }

        cls.no_catalog_project = {
            "title": "No Catalog Project",
            "acronym": "NCP",
            "impact_level": "low",
            "location": "other",
            "creator": cls.test_user.id,
            "catalog_version": None,
        }

    def test_title_required(self):
        response = client.post(
            reverse("project-list"),
            data=json.dumps(self.no_title_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_acronym_required(self):
        response = client.post(
            reverse("project-list"),
            data=json.dumps(self.no_acronym_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_catalog_required(self):
        response = client.post(
            reverse("project-list"),
            data=json.dumps(self.no_catalog_project),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectComponentsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )

        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_component_2 = Component.objects.create(
            title="Cool Components",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_component_3 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog_version="NIST 800-53r5",
        )

        cls.test_project.components.set(
            [
                cls.test_component,
                cls.test_component_2,
            ]
        )

    def test_get_project_with_components(self):
        response = client.get(
            reverse("project-detail", kwargs={"project_id": self.test_project.pk})
        )

        project = self.test_project
        serializer = ProjectSerializer(project)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        received_num_components = len(response.data["components"])
        received_components_count = response.data["components_count"]
        expected_num_components = 2

        # ensure that response includes all components in the project
        self.assertEqual(received_num_components, expected_num_components)

        # ensure that response includes accurate components_count
        self.assertEqual(received_components_count, expected_num_components)


class ProjectAddComponentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )
            cls.test_catalog_2 = Catalog.objects.create(
                name="NIST Test Catalog 2",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="moderate",
            )
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog_2,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_3 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog_version="NIST 800-53r5",
        )

    def test_invalid_project(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {"creator": 1, "component_id": 1, "project_id": 0},
        )
        self.assertEqual(resp.status_code, 404)

    def test_invalid_project_permissions(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {"creator": 0, "component_id": 1, "project_id": self.test_project.id},
        )
        self.assertEqual(resp.status_code, 401)

    def test_invalid_component(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "creator": self.test_user.id,
                "component_id": 0,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 404)

    def test_different_catalog(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "creator": self.test_user.id,
                "component_id": self.test_component_2.id,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 400)

    def test_happy_path(self):
        resp = self.client.post(
            "/api/projects/add-component/",
            {
                "creator": self.test_user.id,
                "component_id": self.test_component.id,
                "project_id": self.test_project.id,
            },
        )
        self.assertEqual(resp.status_code, 200)


class ProjectControlPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )

        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_component_2 = Component.objects.create(
            title="Cool Components",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog_version="NIST 800-53r5",
        )

        cls.test_project.components.set(
            [
                cls.test_component,
                cls.test_component_2,
            ]
        )

    def test_get_control_page(self):
        resp = self.client.get(
            reverse(
                "project-get-control",
                kwargs={
                    "project_id": self.test_project.id,
                    "control_id": "ac-2.1",
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
                    "control_id": "ac-2.1",
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
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )
        cls.test_component = Component.objects.create(
            title="ociso",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="aws",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_post_save_component_added_ocisco(self):
        project = Project.objects.create(
            title="Basic Project",
            acronym="BP",
            impact_level="low",
            location="other",
            creator=self.test_user,
            catalog_version="NIST 800-53r5",
        )
        has_ociso = False
        for c in project.components.all():
            if c.title == "ociso":
                has_ociso = True

        self.assertTrue(has_ociso)

    def test_post_save_component_added_both(self):
        project = Project.objects.create(
            title="Basic Project",
            acronym="BP",
            impact_level="low",
            location="cms_aws",
            creator=self.test_user,
            catalog_version="NIST 800-53r5",
        )
        has_ociso = False
        has_aws = False
        for c in project.components.all():
            if c.title == "ociso":
                has_ociso = True
            elif c.title == "aws":
                has_aws = True

        self.assertTrue(has_ociso)
        self.assertTrue(has_aws)


class ProjectComponentSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="NIST 800-53r5",
                impact_level="low",
            )
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_3 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog_version="NIST 800-53r5",
        )
        cls.test_project.components.set(
            [
                cls.test_component,
                cls.test_component_2,
                cls.test_component_3,
            ]
        )

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


class ProjectComponentNotAddedListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            cls.test_catalog = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version="CMS ARS 3.1",
                impact_level="low",
            )
        cls.test_component_0 = Component.objects.create(
            title="OCISO",
            description="OCISO Inheritable Controls",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=[],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_1 = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="New Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_3 = Component.objects.create(
            title="private component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=cls.test_catalog,
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
            status=1,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=cls.test_user,
            catalog=cls.test_catalog,
        )

    def test_ociso_component_not_returned(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/components-not-added/",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        formatedResponse = json.loads(resp.content)
        for test in formatedResponse:
            self.assertNotEqual(test.get("title"), "OCISO")

    def test_private_component_not_returned(self):
        resp = self.client.get(
            "/api/projects/" + str(self.test_project.id) + "/components-not-added/",
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        formatedResponse = json.loads(resp.content)
        for test in formatedResponse:
            self.assertNotEqual(test.get("title"), "private component")
