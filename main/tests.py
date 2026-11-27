import datetime

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Project


class ProjectViewTest(TestCase):
    def test_project_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")

    # Since Tutorial 07 the Projects page is an empty shell filled by
    # JavaScript from /api/v1/projects/, so data checks go to the API.

    def test_project_data_is_served_by_the_api(self):
        Project.objects.create(
            title="Website Company Profile PT. Kharisma Cipta Kreasi",
            description="Website company profile berfokus pada billboard.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2024,
            url="https://kharismacipta.com",
        )

        response = self.client.get(reverse("api:project-list"))

        self.assertContains(
            response,
            "Website Company Profile PT. Kharisma Cipta Kreasi",
        )
        self.assertEqual(response.json()[0]["year"], 2024)

    def test_page_has_empty_state_and_loads_from_api(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertContains(response, 'id="empty"')
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")
        self.assertContains(response, reverse("api:project-list"))

    def test_multiple_projects_are_all_returned(self):
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

        response = self.client.get(reverse("api:project-list"))

        titles = [item["title"] for item in response.json()]
        self.assertEqual(len(titles), 2)
        self.assertIn("Website Company Profile PT. Graha Arcadia Raya", titles)

    def test_project_tech_stack_field_is_returned(self):
        Project.objects.create(
            title="Website Company Profile PT. Graha Arcadia Raya",
            description="Berfokus pada signage dan visual branding.",
            tech_stack="React.js, JavaScript, Tailwind CSS",
            year=2025,
        )

        response = self.client.get(reverse("api:project-list"))

        self.assertEqual(
            response.json()[0]["tech_stack"], "React.js, JavaScript, Tailwind CSS",
        )

    def test_project_url_uses_named_route(self):
        response = self.client.get("/project/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "main:show_project")


class ProjectFormPageTest(TestCase):
    """Owner-only HTML create and edit pages for projects."""

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="pw-12345")
        self.editor = User.objects.create_user(username="editor", password="pw-12345")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_login(self.owner)
        self.project = Project.objects.create(
            title="Bot Pengingat Deadline", description="Bot Telegram.",
            tech_stack="Python", year=2025,
        )
        self.create_url = reverse("main:create_project")
        self.edit_url = reverse("main:update_project", args=[self.project.id])

    def test_create_page_renders_every_project_field(self):
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_form.html")
        self.assertContains(response, '<form method="post"')
        for name in ("title", "description", "tech_stack", "year", "url"):
            self.assertContains(response, f'name="{name}"')

    def test_create_page_saves_a_valid_project(self):
        response = self.client.post(self.create_url, {
            "title": "MyPortfolio Mobile", "description": "Aplikasi Flutter.",
            "tech_stack": "Flutter, Dart", "year": 2026, "url": "",
        })

        self.assertRedirects(response, reverse("main:show_project"))
        self.assertTrue(Project.objects.filter(title="MyPortfolio Mobile").exists())

    def test_edit_page_is_prefilled_and_saves_changes(self):
        response = self.client.get(self.edit_url)
        self.assertContains(response, 'value="Bot Pengingat Deadline"')
        self.assertContains(response, "Simpan Perubahan")

        response = self.client.post(self.edit_url, {
            "title": "Bot Pengingat Deadline Tugas", "description": "Bot Telegram.",
            "tech_stack": "Python", "year": 2025, "url": "",
        })

        self.assertRedirects(response, reverse("main:show_project"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Bot Pengingat Deadline Tugas")

    def test_invalid_edit_shows_the_error_and_keeps_the_data(self):
        response = self.client.post(self.edit_url, {
            "title": "<b></b>", "description": "Bot Telegram.",
            "tech_stack": "Python", "year": 2025, "url": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nama proyek tidak boleh hanya berisi tag HTML.")
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Bot Pengingat Deadline")

    def test_editor_gets_403_and_cannot_change_the_project(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.edit_url).status_code, 403)
        response = self.client.post(self.edit_url, {
            "title": "Diubah Editor", "description": "Bot Telegram.",
            "tech_stack": "Python", "year": 2025, "url": "",
        })

        self.assertEqual(response.status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Bot Pengingat Deadline")

    def test_edit_button_is_only_enabled_for_the_owner(self):
        for user, can_edit in [(self.owner, "true"), (self.editor, "false")]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("main:show_project"))
                self.assertContains(response, f'const CAN_EDIT = "{can_edit}"')


class ExperiencePageTest(TestCase):
    """The Experience page and the old HTML views follow the API's role rules."""

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="pw-12345")
        self.member = User.objects.create_user(username="member", password="pw-12345")
        self.editor = User.objects.create_user(username="editor", password="pw-12345")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.experience = Experience.objects.create(
            title="Staff MDC @ FUKI", description="Konten.", category="volunteer",
            started_at=datetime.date(2025, 1, 1),
        )
        self.page_url = reverse("main:show_experience")

    def test_page_points_to_drf_api_and_sets_csrf_cookie(self):
        self.client.force_login(self.member)
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("api:experience-list"))
        self.assertIn("csrftoken", response.cookies)

    def test_modal_is_only_rendered_for_editor_and_owner(self):
        for user, has_modal, has_add_button in [
            (self.member, False, False),
            (self.editor, True, False),
            (self.owner, True, True),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(self.page_url)
                self.assertEqual('id="experience-form-modal"' in response.content.decode(), has_modal)
                self.assertEqual('id="experience-add-button"' in response.content.decode(), has_add_button)

    def test_old_html_views_match_api_rules_for_editor(self):
        self.client.force_login(self.editor)
        edit_url = reverse("main:update_experience", args=[self.experience.id])
        self.assertEqual(self.client.get(edit_url).status_code, 200)
        delete_url = reverse("main:delete_experience", args=[self.experience.id])
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        create_url = reverse("main:create_experience")
        self.assertEqual(self.client.get(create_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_template_comments_stay_hidden(self):
        # {# #} only works on one line; a longer note leaks into the page as text.
        for user in (None, self.owner):
            with self.subTest(user=getattr(user, "username", "visitor")):
                if user is not None:
                    self.client.force_login(user)
                response = self.client.get(self.page_url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "{#")
                self.assertNotContains(response, "#}")