from rest_framework.test import APITestCase


class UnauthenticatedAPITestCase(APITestCase):
    def test_unauthenticated_request_returns_403(self):
        test_cases = ('/api/projects/', '/api/users/')

        for test_case in test_cases:
            with self.subTest(url=test_case):
                response = self.client.get(test_case)

                self.assertEqual(response.status_code, 401)
