from django.test import TestCase

from projects.models import Project
from users.models import User

from guardian.shortcuts import get_perms


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        Project.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=1),
        )

    # Tests for field labels
    def test_title_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_acronym_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("acronym").verbose_name
        self.assertEqual(field_label, "acronym")

    def test_impact_level_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("impact_level").verbose_name
        self.assertEqual(field_label, "impact level")

    def test_location_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("location").verbose_name
        self.assertEqual(field_label, "location")

    def test_status_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("status").verbose_name
        self.assertEqual(field_label, "status")

    def test_creator_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("creator_id").verbose_name
        self.assertEqual(field_label, "creator")

    def test_created_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = Project.objects.get(id=1)
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_acronym_max_length(self):
        project = Project.objects.get(id=1)
        max_length = project._meta.get_field("acronym").max_length
        self.assertEqual(max_length, 20)

    def test_impact_level_max_length(self):
        project = Project.objects.get(id=1)
        max_length = project._meta.get_field("impact_level").max_length
        self.assertEqual(max_length, 20)

    def test_location_max_length(self):
        project = Project.objects.get(id=1)
        max_length = project._meta.get_field("location").max_length
        self.assertEqual(max_length, 100)

    def test_status_max_length(self):
        project = Project.objects.get(id=1)
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
            creator=User.objects.get(id=1),
        )

        # ensure project status defaults as expected
        expected_status = "active"
        project = Project.objects.get(title="Basic Project")
        status = project.status
        self.assertEqual(status, expected_status)
    

    def test_permission_group_on_creation(self):
        Project.objects.create(
            title="Test Project",
            acronym="TP",
            impact_level="low",
            location="other",
            creator=User.objects.get(id=1),
        )
        project = Project.objects.get(title="Test Project")
        user = User.objects.get(id=1)
        self.assertEqual('change_project' in get_perms(user, project), True)
        self.assertEqual('view_project' in get_perms(user, project), True)
        self.assertEqual('manage_project_users' in get_perms(user, project), True)
