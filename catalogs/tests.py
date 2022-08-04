from django.core.files import File
from django.urls import reverse
from rest_framework import status

from testing_utils import AuthenticatedAPITestCase, prevent_request_warnings

from .catalogio import CatalogTools as Tools
from .models import Catalog


class CatalogModelTest(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            self.cat = Catalog.objects.create(
                name="NIST Test Catalog",
                file_name=catalog,
            )

    def test_load_catalog(self):
        catalog = Tools(self.cat.file_name.path)
        self.assertIsInstance(catalog, Tools)

    def test_catalog_title(self):
        catalog = Tools(self.cat.file_name.path)
        title = "NIST SP 800-53 Rev 5 Controls Test Catalog"
        cat_title = catalog.catalog_title
        self.assertEqual(cat_title, title)

    def test_get_control_by_id(self):
        cid = self.cat.id
        response = self.client.get(
            reverse("get_control_by_id", kwargs={"catalog": cid, "control_id": "ac-1"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @prevent_request_warnings
    def test_post_control_by_id(self):
        cid = self.cat.id
        response = self.client.post(
            reverse("get_control_by_id", kwargs={"catalog": cid, "control_id": "ac-1"})
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CatalogEndpointTest(AuthenticatedAPITestCase):
    def test_valid_catalog(self):
        with open("blueprintapi/testdata/NIST_SP-800-53_rev5_test.json", "rb") as f:
            catalog = File(f)
            resp = self.client.post(
                "/api/catalogs/",
                {"name": "Test Catalog", "file_name": catalog},
            )
            self.assertEqual(resp.status_code, 201)
