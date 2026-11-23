from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from main.management.commands.seed_portfolio import EXPERIENCES, PROJECTS
from main.models import Experience, Project
from main.serializers import ExperienceSerializer, ProjectSerializer


class SeedPortfolioCommandTest(TestCase):
    def run_seed(self):
        output = StringIO()
        call_command("seed_portfolio", stdout=output)
        return output.getvalue()

    def test_creates_every_entry_and_the_editor_group(self):
        output = self.run_seed()
        self.assertEqual(Experience.objects.count(), len(EXPERIENCES))
        self.assertEqual(Project.objects.count(), len(PROJECTS))
        self.assertTrue(Group.objects.filter(name="Editor").exists())
        self.assertIn(f"Ditambahkan {len(EXPERIENCES)} experience", output)

    def test_running_twice_adds_nothing(self):
        self.run_seed()
        output = self.run_seed()
        self.assertEqual(Experience.objects.count(), len(EXPERIENCES))
        self.assertEqual(Project.objects.count(), len(PROJECTS))
        self.assertIn("Ditambahkan 0 experience dan 0 project", output)

    def test_existing_entries_are_left_unchanged(self):
        title = PROJECTS[0]["title"]
        Project.objects.create(
            title=title, description="Versi saya sendiri", tech_stack="Django", year=2026,
        )
        self.run_seed()
        self.assertEqual(Project.objects.filter(title=title).count(), 1)
        self.assertEqual(Project.objects.get(title=title).description, "Versi saya sendiri")

    def test_seed_data_passes_the_api_validation(self):
        # The command writes straight to the models, so every row is checked
        # against the same rules the API applies to user input.
        for serializer_class, rows in (
            (ExperienceSerializer, EXPERIENCES),
            (ProjectSerializer, PROJECTS),
        ):
            for row in rows:
                with self.subTest(title=row["title"]):
                    serializer = serializer_class(data=row)
                    self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_api_pages_through_the_seeded_experiences(self):
        self.run_seed()
        response = self.client.get(reverse("api:experience-list"))
        self.assertEqual(response.data["count"], len(EXPERIENCES))
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])