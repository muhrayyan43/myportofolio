from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact


class ContactPageTest(TestCase):
    """Tutorial 06: the HTMX contact manager, checked against the roles from Tugas 4."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.member = User.objects.create_user(username="member", password="test-password")
        self.contact = Contact.objects.create(name="Ani", email="ani@example.com")

    def test_page_lists_contacts_for_visitors(self):
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contacts/index.html")
        self.assertContains(response, "ani@example.com")
        # Visitors see the table but not the add form.
        self.assertNotContains(response, "contact-add-form")

    def test_empty_state(self):
        Contact.objects.all().delete()
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertContains(response, "Tidak ada kontak.")

    def test_search_matches_name_or_email(self):
        Contact.objects.create(name="Budi", email="budi@kampus.id")
        response = self.client.get(reverse("contacts:contact_search"), {"q": "KAMPUS"})
        self.assertContains(response, "budi@kampus.id")
        self.assertNotContains(response, "ani@example.com")

    def test_only_owner_can_add(self):
        url = reverse("contacts:contact_add")
        data = {"name": "Citra", "email": "citra@example.com"}
        self.assertEqual(self.client.post(url, data).status_code, 403)
        self.client.force_login(self.editor)
        self.assertEqual(self.client.post(url, data).status_code, 403)
        self.assertFalse(Contact.objects.filter(email="citra@example.com").exists())

        self.client.force_login(self.owner)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "citra@example.com")
        self.assertTrue(Contact.objects.filter(email="citra@example.com").exists())

    def test_invalid_input_is_rejected_with_400(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("contacts:contact_add"), {"name": "   ", "email": "bukan-email"},
        )
        self.assertContains(response, "Nama wajib diisi.", status_code=400)
        self.assertEqual(Contact.objects.count(), 1)

    def test_editor_can_update_but_not_delete(self):
        self.client.force_login(self.editor)
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.contact.pk]),
            "name=Ani+Wijaya&email=ani%40example.com",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Ani Wijaya")

        response = self.client.delete(reverse("contacts:contact_delete", args=[self.contact.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Contact.objects.filter(pk=self.contact.pk).exists())

    def test_member_cannot_open_the_edit_row(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("contacts:contact_edit", args=[self.contact.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.delete(reverse("contacts:contact_delete", args=[self.contact.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Contact.objects.exists())