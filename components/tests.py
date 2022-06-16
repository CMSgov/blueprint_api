import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from catalogs.models import Catalog

from .models import Component
from .serializers import ComponentSerializer

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


class ComponentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_catalog = Catalog.objects.create(
            name="NIST_SP-800", file_name="NIST_SP-800.json"
        )

        Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=Catalog.objects.get(id=1),
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    # Tests for field labels
    def test_title_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_description_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_controls_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("controls").verbose_name
        self.assertEqual(field_label, "controls")

    def test_type_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("type").verbose_name
        self.assertEqual(field_label, "type")

    def test_search_terms_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("search_terms").verbose_name
        self.assertEqual(field_label, "search terms")

    def test_component_json_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("component_json").verbose_name
        self.assertEqual(field_label, "component json")

    def test_created_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = Component.objects.get(id=1)
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = Component.objects.get(id=1)
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_description_max_length(self):
        project = Component.objects.get(id=1)
        max_length = project._meta.get_field("description").max_length
        self.assertEqual(max_length, 500)

    def test_type_max_length(self):
        project = Component.objects.get(id=1)
        max_length = project._meta.get_field("type").max_length
        self.assertEqual(max_length, 100)


class GetAllComponentsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_catalog = Catalog.objects.create(
            name="NIST_SP-800", file_name="NIST_SP-800.json"
        )

        Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        Component.objects.create(
            title="Another Even Cooler Component",
            description="This one is better.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1", "sc-2"],
            search_terms=["cool", "best"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_get_all_components(self):
        expected_num_components = 2

        response = client.get(reverse("component-list"))
        components = Component.objects.all()
        serializer = ComponentSerializer(components, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), expected_num_components)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleComponentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_get_valid_single_component(self):
        response = client.get(
            reverse("component-detail", kwargs={"pk": self.test_component.pk})
        )
        component = Component.objects.get(pk=self.test_component.pk)
        serializer = ComponentSerializer(component)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_component(self):
        invalid_id = 0
        response = client.get(reverse("component-detail", kwargs={"pk": invalid_id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewComponentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_catalog = Catalog.objects.create(
            name="NIST_SP-800", file_name="NIST_SP-800.json"
        )

    def test_create_valid_component(self):
        self.valid_payload = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_component(self):
        self.invalid_payload = {
            "not_real": "this is not a valid field for a component and will fail create attempt"
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # NON-required field tests
    def test_search_terms_field_is_NOT_required(self):
        self.valid_payload_without_search_terms = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.valid_payload_without_search_terms),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # required field tests
    def test_title_field_is_required(self):
        self.invalid_payload_without_title = {
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_title),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_description_field_is_required(self):
        self.invalid_payload_without_description = {
            "title": "Cool Component",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_description),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_catalog_field_is_required(self):
        self.invalid_payload_without_catalog = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_catalog),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_controls_field_is_required(self):
        self.invalid_payload_without_controls = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_controls),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_type_field_is_required(self):
        self.invalid_payload_without_type = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_type),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_component_json_field_is_required(self):
        self.invalid_payload_without_component_json = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.invalid_payload_without_component_json),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_type_field_is_lowercase(self):
        self.uppercase_type_field = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "catalog": self.test_catalog.id,
            "controls": ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            "search_terms": ["cool", "magic", "software"],
            "type": "SOFTWARE",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = client.post(
            reverse("component-list"),
            data=json.dumps(self.uppercase_type_field),
            content_type="application/json",
        )

        received_type = response.data["type"]
        expected_lowercase_type = "software"

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(received_type, expected_lowercase_type)
