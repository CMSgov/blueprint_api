import time

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

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
