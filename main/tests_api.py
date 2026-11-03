"""Tutorial 07's 13 Project API scenarios, adapted to existing portfolio fields."""
import uuid
from datetime import date

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project
from main.serializers import ProjectSerializer


class ProjectAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="owner", password="test-password", email="owner@example.com")
        cls.visitor = User.objects.create_user(username="visitor", password="test-password")
        cls.project = Project.objects.create(title="Portfolio", short_description="My website",
            full_description="Full description", tags="Django", category="design", image_url="/static/img/monte.png")

    def setUp(self):
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {"title": "New project", "short_description": "Useful app", "full_description": "An app",
                        "tags": "Python", "category": "design", "image_url": "https://example.com/image.png"}

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(self.client.get(self.detail_url).data["title"], self.project.title)
        self.assertEqual(ProjectSerializer(self.project).data["is_starred"], False)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": " PORT "})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.client.get(self.list_url, {"title": "not-found"}).data, [])

    def test_missing_project(self):
        missing = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.patch(missing, {"title": "X"}, format="json").status_code, 403)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(missing, {"title": "X"}, format="json").status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
        sanitized = self.client.post(self.list_url, {**self.payload, "title": "Safe <b>Project</b>",
            "short_description": "<i>Useful app</i>"}, format="json")
        self.assertEqual(sanitized.data["title"], "Safe Project")
        self.assertEqual(sanitized.data["short_description"], "Useful app")

    def test_validation(self):
        self.client.force_authenticate(self.owner)
        for changes, field in [({"title": "   "}, "title"), ({"title": '<img src="x" onerror="alert(1)"//>'}, "title"),
            ({"image_url": "javascript:alert(1)"}, "image_url"), ({"image_url": "//example.com/x"}, "image_url"),
            ({"image_url": "/\\example.com/x"}, "image_url"), ({"short_description": "<b></b>"}, "short_description")]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)
        malformed = self.client.post(self.list_url, '{"title":', content_type="application/json")
        self.assertEqual(malformed.status_code, 400)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.short_description, "My website")
        self.assertEqual(self.client.put(self.detail_url, {"title": "Incomplete"}, format="json").status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.client.get(self.star_url).status_code, 403)
        self.client.force_authenticate(self.visitor)
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")
        self.assertFalse(self.project.starred_by.filter(pk=self.owner.pk).exists())
        self.client.force_authenticate(self.owner)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])
        self.client.force_authenticate(self.visitor)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, {**self.payload, "id": str(self.project.pk), "star_count": 99,
            "is_starred": True, "starred_by_names": "forged", "starred_by": [self.visitor.id]}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], str(self.project.pk))
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertNotIn("password", response.data)
        self.assertNotIn("email", response.data)

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

    def test_wrong_method(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format="json").status_code, 405)
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.head(url).status_code, 200)
            self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        for method, url, payload in [("post", self.list_url, self.payload), ("patch", self.detail_url, {"title": "Changed"}),
                                    ("delete", self.detail_url, {}), ("post", self.star_url, {})]:
            self.assertEqual(getattr(client, method)(url, payload, format="json").status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)


class ExperienceAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="exp-owner", password="test-password", email="owner@example.com")
        cls.visitor = User.objects.create_user(username="exp-visitor", password="test-password")
        cls.editor = User.objects.create_user(username="exp-editor", password="test-password")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.experience = Experience.objects.create(title="Designer", location="Depok", description="<ul><li>Design work</li></ul>",
            category="part-time", started_at=date(2026, 1, 1))

    def setUp(self):
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.pk])
        self.payload = {"title": "Researcher", "location": "UI", "description": "Research work", "category": "research",
            "started_at": "2026-09-01", "ended_at": None}

    def test_public_list_detail_search_and_category(self):
        for user in (None, self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user)
            response = self.client.get(self.list_url, {"title": "DESIGN", "category": "part-time"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data[0]["description"], "- Design work")
            self.assertTrue(response.data[0]["is_ongoing"])
            self.assertEqual(self.client.get(self.detail_url).status_code, 200)
            self.assertEqual(self.client.get(self.list_url, {"category": "research"}).data, [])

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Edited"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Designer")

    def test_editor_updates_but_cannot_create_or_delete(self):
        self.client.force_authenticate(self.editor)
        response = self.client.patch(self.detail_url, {"title": "Senior Designer"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Senior Designer")
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_creates_updates_and_deletes(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, {**self.payload, "title": "<b>Researcher</b>"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Researcher")
        self.assertEqual(self.client.put(self.detail_url, {"title": "Incomplete"}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(self.detail_url, {"location": "Jakarta"}, format="json").status_code, 200)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_validation_and_partial_dates(self):
        self.client.force_authenticate(self.owner)
        for changes, field in [({"title": "<b></b>"}, "title"), ({"category": "invalid"}, "category"),
            ({"ended_at": "2026-08-01"}, "ended_at"), ({"started_at": "bad"}, "started_at")]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        response = self.client.patch(self.detail_url, {"ended_at": "2025-12-31"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.experience.ended_at = date(2026, 3, 1)
        self.experience.save()
        self.assertEqual(self.client.patch(self.detail_url, {"started_at": "2026-04-01"}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(self.detail_url, {"ended_at": None}, format="json").status_code, 200)

    def test_csrf_editor_and_safe_methods(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="exp-editor", password="test-password")
        self.assertEqual(client.patch(self.detail_url, {"title": "Updated"}, format="json").status_code, 403)
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.patch(self.detail_url, {"title": "Updated"}, format="json", HTTP_X_CSRFTOKEN=token).status_code, 200)
        for method in (client.head, client.options):
            self.assertEqual(method(self.detail_url).status_code, 200)
        self.assertEqual(Experience.objects.count(), 1)

    def test_unknown_object_and_wrong_method(self):
        missing = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format="json").status_code, 405)
