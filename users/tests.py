import json

from django.urls import reverse
from rest_framework import status

from testing_utils import AuthenticatedAPITestCase, prevent_request_warnings

from .models import User
from .serializers import UserSerializer


class GetAllUsersTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tester = User.objects.create(
            username="tester",
            first_name="Testy",
            last_name="Testerson",
            email="testing4lyfe@theworldisatest.com",
        )
        cls.muggle = User.objects.create(
            username="muggle",
            first_name="Boring",
            last_name="Person",
            email="normie@lamezers.com",
        )

    def test_get_all_users(self):
        response = self.client.get(reverse("user-list"))
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleUserTest(AuthenticatedAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tester = User.objects.create(
            username="tester",
            first_name="Testy",
            last_name="Testerson",
            email="testing4lyfe@theworldisatest.com",
        )

    def test_get_valid_single_user(self):
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.tester.pk}))
        user = User.objects.get(pk=self.tester.pk)
        serializer = UserSerializer(user)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @prevent_request_warnings
    def test_get_invalid_single_user(self):
        invalid_id = 0
        response = self.client.get(reverse("user-detail", kwargs={"pk": invalid_id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewUserTest(AuthenticatedAPITestCase):
    def test_create_valid_user(self):
        self.valid_payload = {
            "username": "tester",
            "password": "awesomepassword",
            "first_name": "Testy",
            "last_name": "Testerson",
            "email": "testing4lyfe@theworldisatest.com",
        }

        response = self.client.post(
            reverse("user-list"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @prevent_request_warnings
    def test_create_invalid_user(self):
        # note that username is required for valid post
        self.invalid_payload = {
            "username": "",
            "first_name": "Testy",
            "last_name": "Testerson",
            "email": "testing4lyfe@theworldisatest.com",
        }

        response = self.client.post(
            reverse("user-list"),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateSingleUserTest(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()

        self.tester = User.objects.create(
            username="tester",
            first_name="Testy",
            last_name="Testerson",
            email="testing4lyfe@theworldisatest.com",
        )

    def test_valid_update_user(self):
        self.valid_payload = {
            "username": "tester",
            "first_name": "Sleepy",
            "last_name": "Sleeper",
            "email": "naps4ever@iluvnaps.com",
        }
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.tester.pk}),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @prevent_request_warnings
    def test_invalid_update_user(self):
        self.invalid_payload = {
            "username": "",
            "first_name": "Sleepy",
            "last_name": "Sleeper",
            "email": "naps4ever@iluvnaps.com",
        }
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.tester.pk}),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
