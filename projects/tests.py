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
    }
}

# initialize the APIClient app
client = Client()


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=cls.test_user.id),
        )

    # Tests for field labels
    def test_title_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_acronym_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("acronym").verbose_name
        self.assertEqual(field_label, "acronym")

    def test_impact_level_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("impact_level").verbose_name
        self.assertEqual(field_label, "impact level")

    def test_location_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("location").verbose_name
        self.assertEqual(field_label, "location")

    def test_status_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("status").verbose_name
        self.assertEqual(field_label, "status")

    def test_creator_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("creator_id").verbose_name
        self.assertEqual(field_label, "creator")

    def test_created_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = Project.objects.get(id=self.test_project.id)
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = Project.objects.get(id=self.test_project.id)
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_acronym_max_length(self):
        project = Project.objects.get(id=self.test_project.id)
        max_length = project._meta.get_field("acronym").max_length
        self.assertEqual(max_length, 20)

    def test_impact_level_max_length(self):
        project = Project.objects.get(id=self.test_project.id)
        max_length = project._meta.get_field("impact_level").max_length
        self.assertEqual(max_length, 20)

    def test_location_max_length(self):
        project = Project.objects.get(id=self.test_project.id)
        max_length = project._meta.get_field("location").max_length
        self.assertEqual(max_length, 100)

    def test_status_max_length(self):
        project = Project.objects.get(id=self.test_project.id)
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
            creator=User.objects.get(id=self.test_user.id),
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
        )
        project = Project.objects.get(title="Test Project")
        user = User.objects.get(id=1)
        self.assertEqual("change_project" in get_perms(user, project), True)
        self.assertEqual("view_project" in get_perms(user, project), True)
        self.assertEqual("manage_project_users" in get_perms(user, project), True)


class ProjectComponentsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        cls.test_catalog = Catalog.objects.create(
            name="NIST_SP-800", file_name="NIST_SP-800.json"
        )

        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_component_2 = Component.objects.create(
            title="Cool Components",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=cls.test_user.id),
            # components=cls.test_component.id
        )

        cls.test_project.components.set(
            [
                Component.objects.get(id=cls.test_component.id),
                Component.objects.get(id=cls.test_component_2.id),
            ]
        )

    def test_get_project_with_components(self):
        response = client.get(
            reverse("project-detail", kwargs={"project_id": self.test_project.pk})
        )

        project = Project.objects.get(pk=self.test_project.pk)
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
        cls.test_catalog = Catalog.objects.create(
            name="NIST_SP-800", file_name="NIST_SP-800.json"
        )
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_project = Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=cls.test_user.id),
            # components=cls.test_component.id
        )

    def test_invalid_project(self):
        resp = self.client.post(
            "/api/projects/0/add-component", {"creator": 1, "component_id": 1}
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_project_permissions(self):
        resp = self.client.post(
            "/api/projects/" + str(self.test_project.id) + "/add-component",
            {"creator": 0, "component_id": 1},
        )
        self.assertEqual(resp.status_code, 401)

    def test_invalid_component(self):
        resp = self.client.post(
            "/api/projects/" + str(self.test_project.id) + "/add-component",
            {"creator": self.test_user.id, "component_id": 0},
        )
        self.assertEqual(resp.status_code, 400)

    def test_happy_path(self):
        resp = self.client.post(
            "/api/projects/" + str(self.test_project.id) + "/add-component",
            {"creator": self.test_user.id, "component_id": self.test_component.id},
        )
        self.assertEqual(resp.status_code, 200)
