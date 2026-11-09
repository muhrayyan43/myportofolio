import datetime
import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project

class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django", year=2026,
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "year": 2026, "url": "https://example.com/",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.project.id)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[self.project.id + 999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"url": "javascript:alert(1)"}, "url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class ExperienceAPITest(APITestCase):
    """Tugas 6: /api/v1/experiences/ for all four roles from Tugas 4."""

    PASSWORD = "test-password"

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password=self.PASSWORD, email="owner@example.com",
        )
        self.member = User.objects.create_user(
            username="member", password=self.PASSWORD, email="member@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password=self.PASSWORD)
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.experience = Experience.objects.create(
            title="Staff MDC @ FUKI",
            description="Membuat konten publikasi.",
            category="volunteer",
            started_at=datetime.date(2025, 1, 1),
            ended_at=datetime.date(2025, 12, 31),
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Intern @ Company",
            "description": "Membangun API.",
            "category": "internship",
            "thumbnail": "https://example.com/logo.png",
            "started_at": "2026-06-01",
            "ended_at": None,
        }

    def assert_experience_unchanged(self):
        """Rejected writes must leave the database exactly as it was."""
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Staff MDC @ FUKI")
        self.assertEqual(self.experience.description, "Membuat konten publikasi.")

    # -- Reading ------------------------------------------------------------

    def test_public_list_is_paginated_and_hides_account_data(self):
        self.experience.starred_by.add(self.member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        item = response.data["results"][0]
        self.assertEqual(item["id"], str(self.experience.id))
        self.assertEqual(item["category_display"], "Volunteer")
        self.assertEqual(item["star_count"], 1)
        self.assertFalse(item["is_starred"])
        for hidden in ("starred_by", "email", "password", "company"):
            self.assertNotIn(hidden, item)
        self.assertNotIn("member@example.com", response.content.decode())

    def test_public_detail_and_missing_experience(self):
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        missing = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, status.HTTP_404_NOT_FOUND)

    def test_search_by_title_query_param(self):
        response = self.client.get(self.list_url, {"title": "fuki"})
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(self.list_url, {"title": "tidak-ada"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_list_pages_of_five_with_next_link(self):
        for i in range(6):
            Experience.objects.create(
                title=f"Role {i}", description="x", category="freelance",
                started_at=datetime.date(2024, 1, i + 1),
            )
        first = self.client.get(self.list_url)
        self.assertEqual(first.data["count"], 7)
        self.assertEqual(len(first.data["results"]), 5)
        self.assertIsNotNone(first.data["next"])
        second = self.client.get(first.data["next"])
        self.assertEqual(len(second.data["results"]), 2)
        self.assertIsNone(second.data["next"])

    # -- Role rules ---------------------------------------------------------

    def test_visitor_and_member_cannot_write(self):
        for user in (None, self.member):
            self.client.force_authenticate(user=user)
            requests = [
                self.client.post(self.list_url, self.payload, format="json"),
                self.client.put(self.detail_url, self.payload, format="json"),
                self.client.patch(self.detail_url, {"title": "Hacked"}, format="json"),
                self.client.delete(self.detail_url),
            ]
            for response in requests:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_experience_unchanged()

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "Ketua MDC @ FUKI"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Ketua MDC @ FUKI")
        # PATCH keeps fields that were not sent.
        self.assertEqual(self.experience.description, "Membuat konten publikasi.")

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.category, "internship")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_experience_unchanged()

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())
        self.assertTrue(response.data["is_ongoing"])

        response = self.client.patch(self.detail_url, {"category": "part-time"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_put_requires_every_required_field(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.put(self.detail_url, {"title": "Only title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("description", "started_at"):
            self.assertIn(field, response.data)
        self.assert_experience_unchanged()

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # -- Validation ---------------------------------------------------------

    def test_invalid_input_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        cases = [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<script></script>"}, "description"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"category": "astronaut"}, "category"),
            ({"started_at": "bukan-tanggal"}, "started_at"),
            ({"started_at": "2026-06-01", "ended_at": "2026-01-01"}, "ended_at"),
        ]
        for changes, field in cases:
            with self.subTest(field=field, changes=changes):
                response = self.client.post(
                    self.list_url, {**self.payload, **changes}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_text_is_stripped_of_html_tags(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "title": "<b>Intern</b> @ Company",
            "description": "<i>Membangun</i> API.",
            "thumbnail": "",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Intern @ Company")
        self.assertEqual(created.description, "Membangun API.")
        self.assertIsNone(created.thumbnail)

    def test_patch_checks_dates_against_stored_start(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"ended_at": "2024-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.ended_at, datetime.date(2025, 12, 31))

    def test_computed_and_read_only_fields_cannot_be_written(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = str(uuid.uuid4())
        response = self.client.post(self.list_url, {
            **self.payload, "id": forged_id, "star_count": 99, "is_starred": True,
            "is_ongoing": False, "starred_by": [self.member.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], forged_id)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertTrue(response.data["is_ongoing"])
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.starred_by.count(), 0)

    # -- Star ---------------------------------------------------------------

    def test_star_rejects_visitor(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_star_toggles_for_every_logged_in_role(self):
        for user in (self.member, self.editor, self.owner):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.star_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data["is_starred"])
                self.assertTrue(self.experience.starred_by.filter(pk=user.pk).exists())
                response = self.client.post(self.star_url)
                self.assertFalse(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 0)

    def test_star_always_uses_request_user(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(self.star_url, {"user": self.owner.id, "user_id": self.owner.id}, format="json")
        self.assertEqual(list(self.experience.starred_by.all()), [self.member])

    def test_star_status_is_per_user_in_list(self):
        self.experience.starred_by.add(self.member)
        self.client.force_authenticate(user=self.member)
        self.assertTrue(self.client.get(self.list_url).data["results"][0]["is_starred"])
        self.client.force_authenticate(user=self.editor)
        item = self.client.get(self.list_url).data["results"][0]
        self.assertFalse(item["is_starred"])
        self.assertEqual(item["star_count"], 1)

    def test_star_only_accepts_post(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # -- CSRF with a real session (force_authenticate skips CSRF) ---------

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password=self.PASSWORD))
        response = client.patch(self.detail_url, {"title": "No token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("CSRF", str(response.data["detail"]))
        self.assert_experience_unchanged()

    def test_session_star_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="member", password=self.PASSWORD))
        response = client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password=self.PASSWORD))
        # The Experience page renders {% csrf_token %}, which sets the cookie.
        page = client.get(reverse("main:show_experience"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"title": "With token"}, format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "With token")