import logging

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import User


def prevent_request_warnings(original_function):
    """
    If we need to test for 400s or 404s this decorator can prevent
    the request class from throwing warnings.
    """

    def new_function(*args, **kwargs):
        # raise logging level to ERROR
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        user, _ = User.objects.get_or_create(username='test', is_superuser=True)
        token, _ = Token.objects.get_or_create(user=user)
        self.client.force_authenticate(user=user, token=token)
