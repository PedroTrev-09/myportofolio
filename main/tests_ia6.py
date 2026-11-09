"""Assignment 6: prove the Experience API contract, including retained database state."""
from datetime import date

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APITestCase

from main.models import Experience
from main.serializers import ExperienceSerializer


class ExperienceAssignmentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser("ia6-owner", "owner@example.com", "test-password")
        cls.visitor = User.objects.create_user("ia6-visitor", password="test-password")
        cls.editor = User.objects.create_user("ia6-editor", password="test-password")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.experience = Experience.objects.create(title="Graphic Designer", location="Lombok",
            description="Visual branding and photography", category="freelance", started_at=date(2025, 1, 1))

    def setUp(self):
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.pk])
        self.star_url = reverse("api:experience-star", args=[self.experience.pk])
        self.payload = {"title": "Research Assistant", "location": "Depok", "description": "User research",
            "category": "research", "started_at": "2026-09-01", "ended_at": None}

    def snapshot(self):
        """Include every persisted field and star relation, not just a row count."""
        rows = list(Experience.objects.order_by("pk").values())
        stars = list(Experience.starred_by.through.objects.order_by("pk").values())
        return rows, stars

    def test_text_hooks_sanitize_each_field_before_saving(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, {**self.payload, "title": "  <b>Research Assistant</b>  ",
            "location": "<i>Depok</i>", "description": "<p>User research</p>"}, format="json")
        self.assertEqual(response.status_code, 201)
        saved = Experience.objects.get(pk=response.data["id"])
        for field in ("title", "location", "description"):
            self.assertEqual(getattr(saved, field), self.payload[field])

    def test_html_only_fields_report_all_errors_and_leave_database_untouched(self):
        self.client.force_authenticate(self.owner)
        before = self.snapshot()
        response = self.client.post(self.list_url, {**self.payload, "title": "<b></b>",
            "location": "<i></i>", "description": '<img src="x" onerror="alert(1)">'}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {"title", "location", "description"})
        self.assertEqual(self.snapshot(), before)

    def test_invalid_patch_is_atomic_and_does_not_save_valid_fields_either(self):
        self.client.force_authenticate(self.editor)
        before = self.snapshot()
        response = self.client.patch(self.detail_url, {"title": "Changed title", "description": "<b></b>"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.assertEqual(self.snapshot(), before)

    def test_text_limits_whitespace_and_invalid_choices_do_not_create_records(self):
        self.client.force_authenticate(self.owner)
        before = self.snapshot()
        for changes, field in [({"title": "x" * 256}, "title"), ({"location": "x" * 256}, "location"),
            ({"title": "   "}, "title"), ({"description": "   "}, "description"), ({"category": "unknown"}, "category")]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(self.snapshot(), before)

    def test_unicode_and_plain_text_survive_validation(self):
        candidate = ExperienceSerializer(data={**self.payload, "title": "Desainer — Riset UI/UX",
            "description": "Riset & desain\nKolaborasi tim"})
        self.assertTrue(candidate.is_valid(), candidate.errors)
        self.assertEqual(candidate.validated_data["title"], "Desainer — Riset UI/UX")
        self.assertEqual(candidate.validated_data["description"], "Riset & desain\nKolaborasi tim")

    def test_invalid_dates_are_field_errors_and_do_not_change_stored_data(self):
        self.client.force_authenticate(self.editor)
        before = self.snapshot()
        for payload in ({"ended_at": "2024-12-31"}, {"started_at": "invalid-date"}):
            response = self.client.patch(self.detail_url, payload, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(self.snapshot(), before)
