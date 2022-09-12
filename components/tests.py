import json
from typing import List

from django.core.files import File
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from catalogs.models import Catalog
from components.componentio import ComponentTools, create_empty_component_json
from components.models import Component
from components.serializers import ComponentListSerializer, ComponentSerializer
from testing_utils import AuthenticatedAPITestCase, prevent_request_warnings
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
                                "control-id": "ac-1",
                                "description": "This component statisfies a.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "ac-2",
                                "description": "This component statisfies b.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-1",
                                "description": "This component statisfies c.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-2",
                                "description": "This component statisfies d.",
                            },
                            {
                                "uuid": "73dd3c2e-54eb-43c6-a488-dfb7c79d9413",
                                "control-id": "at-3",
                                "description": "This component statisfies e.",
                            },
                        ],
                    }
                ],
            }
        ],
    }
}
TEST_COMPONENT_CONTROLS = ["ac-1", "ac-2", "at-1", "at-2", "st-3"]


class GetAllComponentsTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=TEST_COMPONENT_CONTROLS,
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        Component.objects.create(
            title="Another Even Cooler Component",
            description="This one is better.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=TEST_COMPONENT_CONTROLS,
            search_terms=["cool", "best"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_get_all_components(self):
        response = self.client.get(reverse("component-list"))
        components = Component.objects.all().order_by("pk")
        serializer = ComponentListSerializer(components, many=True)
        expected_num_components = 2
        received_num_components = len(response.data)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(received_num_components, expected_num_components)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_controls_count_is_returned(self):
        response = self.client.get(reverse("component-list"))
        component = response.data

        expected_controls_count = len(TEST_COMPONENT_CONTROLS)
        received_controls_count = component[0].get("controls_count")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(received_controls_count, expected_controls_count)


class GetSingleComponentTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_get_valid_single_component(self):
        response = self.client.get(
            reverse("component-detail", kwargs={"pk": self.test_component.pk})
        )

        component = Component.objects.get(pk=self.test_component.pk)
        serializer = ComponentSerializer(component, context=response.data.serializer.context)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @prevent_request_warnings
    def test_get_invalid_single_component(self):
        invalid_id = 0
        response = self.client.get(
            reverse("component-detail", kwargs={"pk": invalid_id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewComponentTest(AuthenticatedAPITestCase):
    def test_create_valid_component(self):
        valid_payload = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = self.client.post(
            reverse("component-list"),
            data=json.dumps(valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @prevent_request_warnings
    def test_create_invalid_component(self):
        invalid_payload = {
            "not_real": "this is not a valid field for a component and will fail create attempt"
        }

        response = self.client.post(
            reverse("component-list"),
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # NON-required field tests
    def test_search_terms_field_is_not_required(self):
        valid_payload_without_search_terms = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = self.client.post(
            reverse("component-list"),
            data=json.dumps(valid_payload_without_search_terms),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # required field tests
    @prevent_request_warnings
    def test_title_field_is_required(self):
        invalid_payload_without_title = {
            "description": "Probably the coolest component you ever did see. It's magical.",
            "search_terms": ["cool", "magic", "software"],
            "type": "software",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = self.client.post(
            reverse("component-list"),
            data=json.dumps(invalid_payload_without_title),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_type_field_is_lowercase(self):
        uppercase_type_field = {
            "title": "Cool Component",
            "description": "Probably the coolest component you ever did see. It's magical.",
            "search_terms": ["cool", "magic", "software"],
            "type": "SOFTWARE",
            "component_json": TEST_COMPONENT_JSON_BLOB,
        }

        response = self.client.post(
            reverse("component-list"),
            data=json.dumps(uppercase_type_field),
            content_type="application/json",
        )

        received_type = response.data["type"]
        expected_lowercase_type = "software"

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(received_type, expected_lowercase_type)


class ComponentViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="testing title",
            description="testing description",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.test_component_3 = Component.objects.create(
            title="testing different catalog",
            description="testing description",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_5_0],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_search_empty_request(self):
        resp = self.client.get("/api/components/search/", format="json")
        self.assertEqual(resp.status_code, 200)

        content = resp.json()
        self.assertEqual(content[3].get("total_item_count"), 3)

    def test_search_query_win(self):
        resp = self.client.get("/api/components/search/?search=win", format="json")
        expected_response = [{"total_item_count": 0}]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), expected_response)

    def test_search_filter_type_software(self):
        resp = self.client.get("/api/components/search/?type=software", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)[0].get("type"), "software")
        self.assertEqual(json.loads(resp.content)[1].get("total_item_count"), 1)

    def test_search_filter_type_policy(self):
        resp = self.client.get("/api/components/search/?type=policy", format="json")
        self.assertEqual(resp.status_code, 200)

        content = resp.json()
        self.assertTrue(all(item["type"] == "policy" for item in content if "total_item_count" not in item))
        self.assertEqual(content[2]["total_item_count"], 2)

    def test_search_filter_catalog_version(self):
        resp = self.client.get(
            f"/api/components/search/?catalog_version={Catalog.Version.CMS_ARS_3_1}", format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)[0].get("type"), "software")
        self.assertEqual(json.loads(resp.content)[2].get("total_item_count"), 2)


class ComponentioTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_component = Component.objects.create(
            title="Cool Component",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.tools = ComponentTools(test_component.component_json)
        cls.test_component = test_component

    def test_get_components(self):
        components = self.tools.get_components()
        self.assertIsInstance(components, List)

    def test_get_component_value(self):
        title = self.tools.get_component_value("title")
        description = self.tools.get_component_value("description")
        self.assertEqual(title, "Cool Component")
        self.assertEqual(description, "This is a really cool component.")

    def test_get_implemenations(self):
        impl = self.tools.get_implemenations()
        self.assertEqual(impl[0].get("description"), "CMS_ARS_3_1")
        self.assertIsInstance(impl[0].get("implemented-requirements"), List)

    def test_get_controls(self):
        controls = self.tools.get_controls()
        self.assertEqual(len(controls), 5)
        self.assertEqual(controls[0].get("control-id"), "ac-1")

    def test_get_control_ids(self):
        ids = self.tools.get_control_ids()
        self.assertEqual(len(ids), 5)
        self.assertEqual(ids[0], "ac-1")


class ComponentTypesViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )
        cls.test_component_2 = Component.objects.create(
            title="testing title",
            description="testing description",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=["ac-2.1"],
            search_terms=["cool", "magic", "software"],
            type="policy",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        # Create component with duplicate type
        Component.objects.create(
            title="Duplicate Type Component",
            description="Component with duplicate type",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=[
                "ac-2.1",
            ],
            search_terms=[
                "cool",
            ],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

    def test_get_types_list(self):
        resp = self.client.get("/api/components/types/", format="json")
        self.assertEqual(resp.status_code, 200)

        content = resp.json()
        # Data structure in response is [["type1"], ["type2"], ..]
        flattened = sorted(value for item in content for value in item)
        self.assertEqual(flattened, ["policy", "software"])

    def test_types_without_superuser(self):
        # Create a non-super user with default permissions
        user = User.objects.create(username="TestUser", password="password")
        token = Token.objects.create(user=user)
        self.client.force_authenticate(user=user, token=token)

        # Create a private component (result should not be available to types endpoint)
        Component.objects.create(
            title="Private component",
            description="testing description",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            search_terms=["cool", "magic", "software"],
            type="crazy-type",
            component_json=TEST_COMPONENT_JSON_BLOB,
            status=Component.Status.SYSTEM,
        )

        response = self.client.get("/api/components/types/")
        self.assertEqual(response.status_code, 200)

        content = response.json()
        # Data structure in response is [["type1"], ["type2"], ..]
        flattened = sorted(value for item in content for value in item)

        self.assertEqual(flattened, ["policy", "software"])


class CreateEmptComponentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as file:
            catalog = File(file)
            Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
                version=Catalog.Version.CMS_ARS_3_1,
                impact_level="low",
            )
        title = "Empty Component"
        default_json = create_empty_component_json(
            title=title,
            catalog_version=Catalog.Version.CMS_ARS_3_1,
            impact_level=Catalog.ImpactLevel.LOW,
        )
        cls.default = Component(
            title=f"{title} private",
            description=f"{title} default system component",
            component_json=json.loads(default_json),
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            status=1,
        )
        cls.tools = ComponentTools(cls.default.component_json)

    def test_no_controls(self):
        components = self.tools.get_control_ids()
        self.assertFalse(components)

    def test_status_is_private(self):
        self.assertEqual(self.default.status, 1)


class ComponentImplementedRequirementViewTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        test_component = Component.objects.create(
            title="Cool Component",
            description="Probably the coolest component you ever did see. It's magical.",
            supported_catalog_versions=[Catalog.Version.CMS_ARS_3_1],
            controls=["ac-2.1", "ac-6.10", "ac-8", "au-6.1", "sc-2"],
            search_terms=["cool", "magic", "software"],
            type="software",
            component_json=TEST_COMPONENT_JSON_BLOB,
        )

        cls.url = f"/api/components/{test_component.id}/implemented-requirements/"

    def test_missing_fields_returns_400(self):
        test_cases = [
            {  # Missing catalog_version
                "action": "add",
                "controls": ["ac-1"],
                "description": "Missing catalog_version"
            },
            {  # Missing action
                "controls": ["ac-1"],
                "catalog_version": "CMS_ARS_3_1",
                "description": "Missing action"
            },
            {  # Missing controls
                "action": "add",
                "catalog_version": "CMS_ARS_3_1",
                "description": "Missing controls",
            }
        ]

        for test in test_cases:
            with self.subTest(request=test["description"]):
                response = self.client.patch(self.url, test)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_controls_list_returns_400(self):
        request_json = {
            "action": "add",
            "catalog_version": "CMS_ARS_3_1",
            "description": "Empty controls list",
            "controls": []
        }

        response = self.client.patch(self.url, request_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_controls_returns_400(self):
        request_json = {
            "action": "add",
            "catalog_version": "CMS_ARS_3_1",
            "description": "Multiple controls list",
            "controls": ["ac-1", "ac-2"]
        }

        response = self.client.patch(self.url, request_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adding_existing_control_returns_400(self):
        request_json = {
            "action": "add",
            "catalog_version": "CMS_ARS_3_1",
            "description": "Duplicate controls list",
            "controls": ["ac-1"]
        }

        response = self.client.patch(self.url, request_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_on_missing_control_returns_400(self):
        request_json = {
            "action": "update",
            "catalog_version": "CMS_ARS_3_1",
            "description": "Can't update missing control",
            "controls": ["ac-500"]
        }

        response = self.client.patch(self.url, request_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_control_description(self):
        test_control_id = "ac-1"
        test_description = "updated description of ac-1 narrative"
        resp = self.client.patch(self.url,
            {
                "action": "update",
                "catalog_version": "CMS_ARS_3_1",
                "controls": [test_control_id],
                "description": test_description,
            },
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.json()
        self.assertNotEqual(content.get("component_json"), TEST_COMPONENT_JSON_BLOB)
        original_length = len(
            TEST_COMPONENT_JSON_BLOB.get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        )
        new_length = len(
            content.get("component_json")
            .get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        )
        self.assertEqual(original_length, new_length)
        for implemented in (
            content.get("component_json")
            .get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        ):
            if implemented.get("control-id") == test_control_id:
                self.assertEqual(implemented.get("description"), test_description)
                self.assertEqual(implemented.get("control-id"), test_control_id)

    def test_add_control_description(self):
        test_control_id = "ac-3"
        test_description = "description of ac-3 narrative"

        response = self.client.patch(self.url,
            {
                "action": "add",
                "catalog_version": "CMS_ARS_3_1",
                "controls": [test_control_id],
                "description": test_description,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.json()

        self.assertNotEqual(content.get("component_json"), TEST_COMPONENT_JSON_BLOB)
        original_length = len(
            TEST_COMPONENT_JSON_BLOB.get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        )
        new_length = len(
            content.get("component_json")
            .get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        )
        self.assertEqual(original_length + 1, new_length)

        for implemented in (
            content.get("component_json")
            .get("component-definition")
            .get("components")[0]
            .get("control-implementations")[0]
            .get("implemented-requirements")
        ):
            if implemented.get("control-id") == test_control_id:
                self.assertEqual(implemented.get("description"), test_description)
                self.assertEqual(implemented.get("control-id"), test_control_id)


class LoadComponentsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_catalog", load_standard_catalogs=True)

    def test_load_test_components(self):
        call_command("load_components")

        expected_components = [
            "Amazon Web Services",
            "Blueprint", "Django",
            "Identity Management",
            "OCISO Inheritable Controls",
            "Splunk",
            "Tenable Nessus",
            "Trend Micro Deep Security"
        ]

        queryset = Component.objects.order_by("title")

        self.assertEqual(queryset.count(), 8)
        self.assertEqual(expected_components, [item.title for item in queryset])
        self.assertTrue(all(item.type == "software" for item in queryset))
        self.assertTrue(all(item.controls for item in queryset))
