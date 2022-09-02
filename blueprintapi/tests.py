import json
import os
import tempfile
import time

from django.test import SimpleTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from blueprintapi.oscal.component import Model
from users.models import User


class UnauthenticatedAPITestCase(APITestCase):
    def test_unauthenticated_request_returns_403(self):
        test_cases = ('/api/projects/', '/api/users/')

        for test_case in test_cases:
            with self.subTest(url=test_case):
                response = self.client.get(test_case)

                self.assertEqual(response.status_code, 401)

    def test_expired_token_returns_401(self):
        user, _ = User.objects.get_or_create(username="test-expired", is_superuser=True)
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"TOKEN {token.key}")

        time.sleep(1)

        with self.settings(AUTH_TOKEN_TTL=1 / 60**2):  # 1s
            response = self.client.get('/api/catalogs/')

            self.assertEqual(response.status_code, 401)
            with self.assertRaises(Token.DoesNotExist):
                Token.objects.get(user=user)


COMPONENT_DATA = {
  "component-definition": {
    "uuid": "4bc1953c-d201-43d9-8d49-70bb6a1c4327",
    "metadata": {
      "title": "TestComponent",
      "published": "2022-08-01T21:05:10.806928+00:00",
      "last-modified": "2022-08-01T21:05:10.806935+00:00",
      "version": "unknown",
      "oscal-version": "1.0.0"
    },
    "components": [
      {
        "uuid": "d42844ee-50a3-40f5-8a02-ccc351e2a95a",
        "type": "software",
        "title": "Test",
        "description": "testing testing",
        "control-implementations": [
          {
            "uuid": "8a89220e-c679-4970-904a-e319f92cb8ca",
            "source": "https://raw.githubusercontent.com/CMSgov/ars-machine-readable/main/3.1/oscal/json/CMS_ARS_3_1_catalog.json",
            "description": "CMS_ARS_3_1",
            "implemented-requirements": [
              {
                "uuid": "809e54d5-1670-45d5-a852-8a34e03d5e95",
                "control-id": "ac-3",
                "description": "The Django web framework implements role-based access control to enforce logical access to its information and services.",
                "props": [
                  {
                    "name": "security_control_type",
                    "value": "Hybrid",
                    "uuid": "925c9e7b-9f60-41f6-bffd-82bcbd882d65"
                  }
                ]
              },
              {
                "uuid": "c6f3a55d-e6aa-4ea1-9892-43336a665b6a",
                "control-id": "ac-7",
                "description": "Django can be configured to lock an account after a specified number of invalid login attempts within a specified time period. These values have been configured in accordance with CMS ARS guidance to lock the account automatically after three (3) invalid login attempts during a 120-minute time window.",
                "props": [
                  {
                    "name": "security_control_type",
                    "value": "Inherited",
                    "uuid": "5d43cfe4-d0cf-44eb-abaf-ee5be464e820"
                  }
                ]
              },
              {
                "uuid": "3ccd9823-cc86-4604-a0cf-083628066524",
                "control-id": "ac-11",
                "description": "The Django web framework has built-in session management that includes locking and terminating a session after a specific duration of inactivity. The duration of a session is set by configuring the `SESSION_COOKIE_AGE` in `settings.py`.",
                "props": [
                  {
                    "name": "security_control_type",
                    "value": "Inherited",
                    "uuid": "48aaf444-76c4-47e8-86b1-665b48a6ffd3"
                  }
                ]
              },
            ]
          }
        ]
      }
    ]
  }
}


class ComponentModelTestCase(SimpleTestCase):

    def test_from_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "test_json.json")

            with open(path, "w") as test_file:
                test_file.write(json.dumps(COMPONENT_DATA))

            component = Model.from_json(path)

            # Test a couple of items to confirm content.
            self.assertEqual(component.component_definition.metadata.title, "TestComponent")
            self.assertEqual(len(component.component_definition.components), 1)
            self.assertEqual(
                str(component.component_definition.components[0].uuid), "d42844ee-50a3-40f5-8a02-ccc351e2a95a"
            )

    def test_control_ids(self):
        component = Model(**COMPONENT_DATA)
        self.assertEqual(sorted(component.component_definition.components[0].control_ids), ['ac-11', 'ac-3', 'ac-7'])