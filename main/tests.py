from django.test import TestCase
from django.urls import reverse
from main.models import Project


class ProjectViewTest(TestCase):
    def test_project_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")

    def test_project_data_appears_on_page_when_data_exists(self):
        Project.objects.create(
            title="Website Company Profile PT. Kharisma Cipta Kreasi",
            description="Website company profile berfokus pada billboard.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2024,
            url="https://kharismacipta.com",
        )

        response = self.client.get(reverse("main:show_project"))

        self.assertContains(
            response,
            "Website Company Profile PT. Kharisma Cipta Kreasi",
        )
        self.assertContains(response, "2024")

    def test_empty_state_shown_when_no_project_data(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertContains(response, "Belum ada project")
        self.assertNotContains(response, "project-card\"")

    def test_multiple_projects_are_all_displayed(self):
        Project.objects.create(
            title="Website Company Profile PT. Kharisma Cipta Kreasi",
            description="Berfokus pada billboard dan media outdoor advertising.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2024,
            url="https://kharismacipta.com",
        )
        Project.objects.create(
            title="Website Company Profile PT. Graha Arcadia Raya",
            description="Berfokus pada signage dan visual branding.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2025,
            url="https://arcadiaraya.com",
        )

        response = self.client.get(reverse("main:show_project"))

        self.assertContains(
            response,
            "Website Company Profile PT. Kharisma Cipta Kreasi",
        )
        self.assertContains(
            response,
            "Website Company Profile PT. Graha Arcadia Raya",
        )
        self.assertEqual(response.context["project_list"].count(), 2)

    def test_project_tech_stack_field_is_displayed(self):
        Project.objects.create(
            title="Website Company Profile PT. Graha Arcadia Raya",
            description="Berfokus pada signage dan visual branding.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2025,
        )

        response = self.client.get(reverse("main:show_project"))

        self.assertContains(response, "React.js, JavaScript, Tailwind CSS")

    def test_project_url_uses_named_route(self):
        response = self.client.get("/project/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "main:show_project")