import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from catalogs.models import Catalog

from .models import Component
from .serializers import ComponentListSerializer, ComponentSerializer

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
                                "control-id": "ac-2.1",
                                "description": "This component statisfies a.",
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


class ComponentModelTest(TestCase):
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

    # Tests for field labels
    def test_title_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_description_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_controls_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("controls").verbose_name
        self.assertEqual(field_label, "controls")

    def test_type_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("type").verbose_name
        self.assertEqual(field_label, "type")

    def test_search_terms_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("search_terms").verbose_name
        self.assertEqual(field_label, "search terms")

    def test_component_json_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("component_json").verbose_name
        self.assertEqual(field_label, "component json")

    def test_created_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = Component.objects.get(id=self.test_component.id)
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = Component.objects.get(id=self.test_component.id)
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_description_max_length(self):
        project = Component.objects.get(id=self.test_component.id)
        max_length = project._meta.get_field("description").max_length
        self.assertEqual(max_length, 500)

    def test_type_max_length(self):
        project = Component.objects.get(id=self.test_component.id)
        max_length = project._meta.get_field("type").max_length
        self.assertEqual(max_length, 100)


TEST_COMPONENT_CONTROLS = ["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"]


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
            controls=TEST_COMPONENT_CONTROLS,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        Component.objects.create(
            title="Another Even Cooler Component",
            description="This one is better.",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=TEST_COMPONENT_CONTROLS,
            search_terms=["cool", "best"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_get_all_components(self):

        response = client.get(reverse("component-list"))
        components = Component.objects.all()
        serializer = ComponentListSerializer(components, many=True)

        expected_num_components = 2
        received_num_components = len(response.data)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(received_num_components, expected_num_components)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_controls_count_is_returned(self):
        response = client.get(reverse("component-list"))
        component = response.data[0]

        expected_controls_count = len(TEST_COMPONENT_CONTROLS)
        received_controls_count = component["controls_count"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(received_controls_count, expected_controls_count)


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


class ComponentViewTest(TestCase):
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
        cls.test_component_2 = Component.objects.create(
            title="testing title",
            description="testing description",
            catalog=Catalog.objects.get(id=cls.test_catalog.id),
            controls=["ac-2.1"],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_search_empty_request(self):
        resp = self.client.get("/api/components/search/?format=json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)[2].get("total_item_count"), 2)

    def test_search_query_win(self):
        resp = self.client.get("/api/components/search/?search=win", format="json")
        expectedResonse = [{"total_item_count": 0}]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, expectedResonse)

    def test_search_filter_type_software(self):
        resp = self.client.get("/api/components/search/?type=software", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)[0].get("type"), "software")
        self.assertEqual(json.loads(resp.content)[1].get("total_item_count"), 1)

    def test_search_filter_type_policy(self):
        resp = self.client.get("/api/components/search/?type=policy", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)[0].get("type"), "policy")
        self.assertEqual(json.loads(resp.content)[1].get("total_item_count"), 1)
