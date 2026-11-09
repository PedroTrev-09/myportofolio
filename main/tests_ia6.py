"""Assignment 6: prove the Experience API contract, including retained database state."""
from datetime import date

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient, APITestCase

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


    def test_denied_role_matrix_preserves_all_fields_and_star_relationships(self):
        self.experience.starred_by.add(self.visitor)
        attempts = [("post", self.list_url, self.payload), ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Unauthorized change"}), ("delete", self.detail_url, {})]
        for user in (None, self.visitor, self.editor):
            self.client.force_authenticate(user)
            for method, url, payload in attempts:
                if user == self.editor and method in ("patch", "put"):
                    continue
                with self.subTest(user=getattr(user, "username", "guest"), method=method):
                    before = self.snapshot()
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.snapshot(), before)

    def test_all_roles_read_list_detail_and_safe_methods_without_mutation(self):
        for user in (None, self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user)
            before = self.snapshot()
            for url in (self.list_url, self.detail_url):
                for method in (self.client.get, self.client.head, self.client.options):
                    self.assertEqual(method(url).status_code, 200)
            self.assertEqual(self.snapshot(), before)

    def test_editor_can_patch_and_put_but_retains_existing_stars(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(self.editor)
        response = self.client.patch(self.detail_url, {"title": "Senior Designer"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Senior Designer")
        self.assertEqual(self.experience.location, "Lombok")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        for field, value in self.payload.items():
            if field != "started_at":
                self.assertEqual(getattr(self.experience, field), value)
        self.assertEqual(self.experience.started_at, date(2026, 9, 1))
        self.assertEqual(list(self.experience.starred_by.values_list("pk", flat=True)), [self.visitor.pk])

    def test_owner_create_and_delete_have_correct_persisted_results(self):
        # The portfolio role is is_superuser, independent of Django admin is_staff.
        self.owner.is_staff = False
        self.client.force_authenticate(self.owner)
        count = Experience.objects.count()
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(Experience.objects.count(), count + 1)
        created.starred_by.add(self.visitor)
        url = reverse("api:experience-detail", args=[created.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=created.pk).exists())
        self.assertEqual(Experience.objects.count(), count)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(Experience.starred_by.through.objects.count(), 0)

    def test_staff_without_editor_group_cannot_change_experience(self):
        self.visitor.is_staff = True
        self.client.force_authenticate(self.visitor)
        before = self.snapshot()
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_star_identity_and_public_response_never_expose_sensitive_accounts(self):
        self.client.force_authenticate(self.visitor)
        response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), set(ExperienceSerializer.Meta.fields))
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertFalse(self.experience.starred_by.filter(pk=self.owner.pk).exists())
        for user in (None, self.editor, self.owner):
            self.client.force_authenticate(user)
            data = self.client.get(self.detail_url).data
            self.assertFalse(data["is_starred"])
            self.assertEqual(data["star_count"], 1)
            for forbidden in ("password", "email", "is_superuser", "starred_by"):
                self.assertNotIn(forbidden, data)
        self.client.force_authenticate(self.visitor)
        self.assertFalse(self.client.post(self.star_url).data["is_starred"])
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_computed_fields_and_uuid_are_read_only_on_update(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(self.editor)
        import uuid
        response = self.client.patch(self.detail_url, {"id": str(uuid.uuid4()), "star_count": 99,
            "is_starred": True, "starred_by": [self.owner.pk], "starred_by_names": "forged"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.experience.pk))
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], self.visitor.username)
        self.assertEqual(list(self.experience.starred_by.values_list("pk", flat=True)), [self.visitor.pk])

    def test_session_csrf_blocks_every_unsafe_method_without_database_changes(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="ia6-owner", password="test-password"))
        client.get(reverse("main:show_experience"))
        attempts = [("post", self.list_url, self.payload), ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Blocked"}), ("delete", self.detail_url, {}), ("post", self.star_url, {})]
        for method, url, payload in attempts:
            for token in (None, "incorrect-token"):
                with self.subTest(method=method, url=url, token=token):
                    before = self.snapshot()
                    headers = {"HTTP_X_CSRFTOKEN": token} if token else {}
                    response = getattr(client, method)(url, payload, format="json", **headers)
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.snapshot(), before)

    def test_real_editor_session_patch_with_token_and_forbidden_create_delete(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="ia6-editor", password="test-password"))
        page = client.get(reverse("main:show_experience"))
        self.assertEqual(page.status_code, 200)
        headers = {"HTTP_X_CSRFTOKEN": client.cookies["csrftoken"].value}
        response = client.patch(self.detail_url, {"title": "Session edit"}, format="json", **headers)
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Session edit")
        before = self.snapshot()
        self.assertEqual(client.post(self.list_url, self.payload, format="json", **headers).status_code, 403)
        self.assertEqual(client.delete(self.detail_url, **headers).status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_search_combines_title_and_category_and_returns_empty_list(self):
        Experience.objects.create(**{**self.payload, "title": "Designer at UI", "started_at": date(2026, 9, 1)})
        response = self.client.get(self.list_url, {"title": " DESIGNER ", "category": " RESEARCH "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["title"] for row in response.data], ["Designer at UI"])
        response = self.client.get(self.list_url, {"title": "not found"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_browsable_api_and_json_formats_render(self):
        for user in (None, self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user)
            for url in (self.list_url, self.detail_url):
                response = self.client.get(url, HTTP_ACCEPT="text/html")
                self.assertEqual(response.status_code, 200)
                self.assertIn("text/html", response["Content-Type"])
                self.assertContains(response, "Django REST framework")
                response = self.client.get(url, {"format": "json"})
                self.assertEqual(response.status_code, 200)
                self.assertIn("application/json", response["Content-Type"])

    def test_legacy_html_routes_cannot_bypass_editor_limits(self):
        self.client.force_login(self.editor)
        before = self.snapshot()
        for name, args in (("main:create_experience", []), ("main:delete_experience", [self.experience.pk])):
            response = self.client.post(reverse(name, args=args), {**self.payload, "ended_at": ""})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.client.get(reverse("main:update_experience", args=[self.experience.pk])).status_code, 200)

    def test_prefetched_star_data_does_not_add_a_query_per_experience(self):
        self.client.force_authenticate(self.visitor)
        self.experience.starred_by.add(self.visitor, self.editor)
        with CaptureQueriesContext(connection) as small:
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
        for index in range(7):
            experience = Experience.objects.create(**{**self.payload, "title": f"Research {index}"})
            experience.starred_by.add(self.visitor)
        with CaptureQueriesContext(connection) as large:
            response = self.client.get(self.list_url)
            self.assertEqual(len(response.data), 8)
        self.assertLessEqual(len(large), len(small) + 1)
        self.assertLessEqual(len(large), 3)
