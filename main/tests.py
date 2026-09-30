from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Graphic Designer & Photographer",
            description="Mengelola visual branding secara konsisten.",
            category="part-time",
            started_at=date.today(),
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Haikal Rafka A Rahman")
        self.assertContains(response, "2506553383")
        self.assertContains(response, "S1 Sistem Informasi")
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_model_logic(self):
        self.assertEqual(str(self.experience), "Graphic Designer & Photographer")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

        self.experience.ended_at = date.today()
        self.experience.save()
        self.assertFalse(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, "Haikal Rafka A Rahman")
        self.assertContains(response, f'href="{reverse("main:show_main")}#about"')


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Monte De Carlo",
            short_description="Desain identitas visual komprehensif.",
            full_description="Deskripsi lengkap mengenai manajemen proyek dan eksekusi.",
            image_url="/static/img/monte.png",
            category="fashion",
            tags="Event, Promotion, Business",
        )

        self.normal_user = User.objects.create_user(
            username="normal-user",
            password="StrongPassword123!",
        )
        self.editor_user = User.objects.create_user(
            username="editor-user",
            password="StrongPassword123!",
        )
        self.superuser = User.objects.create_superuser(
            username="owner",
            password="StrongPassword123!",
            email="owner@example.com",
        )

        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor_user.groups.add(editor_group)

    def test_project_page_uses_ajax_shell(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "project-search-form")
        self.assertContains(response, "loading")
        self.assertContains(response, "error")
        self.assertContains(response, "empty")
        self.assertContains(response, "fetchProjects")
        self.assertNotContains(response, self.project.title)

    def test_projects_json_returns_project_data(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.project.id))
        self.assertEqual(data[0]["fields"]["title"], self.project.title)
        self.assertEqual(data[0]["fields"]["star_count"], 0)
        self.assertFalse(data[0]["fields"]["is_starred"])
        self.assertNotIn("starred_by_names", data[0]["fields"])

    def test_projects_json_supports_title_search(self):
        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "Monte"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "Does Not Exist"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_star_status_is_user_specific(self):
        self.client.login(username="normal-user", password="StrongPassword123!")
        self.project.starred_by.add(self.normal_user)

        response = self.client.get(reverse("main:get_projects_json"))
        data = response.json()[0]["fields"]

        self.assertEqual(data["star_count"], 1)
        self.assertTrue(data["is_starred"])

    def test_create_project_ajax_requires_superuser(self):
        payload = {
            "title": "New Project",
            "category": "event",
            "image_url": "/static/img/monte.png",
            "short_description": "Short description",
            "full_description": "Full description",
            "tags": "Event, Business",
        }

        response = self.client.post(
            reverse("main:create_project_ajax"),
            payload,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

        self.client.login(username="normal-user", password="StrongPassword123!")
        response = self.client.post(
            reverse("main:create_project_ajax"),
            payload,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

        self.client.login(username="owner", password="StrongPassword123!")
        response = self.client.post(
            reverse("main:create_project_ajax"),
            payload,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 2)

    def test_create_project_ajax_rejects_html_only_title(self):
        self.client.login(username="owner", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "<img src=x onerror=alert(1)>",
                "category": "event",
                "image_url": "/static/img/monte.png",
                "short_description": "Short description",
                "full_description": "Full description",
                "tags": "Event",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIn("title", response.json()["errors"])

    def test_create_project_ajax_strips_html_from_text_fields(self):
        self.client.login(username="owner", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "Safe <b>Project</b>",
                "category": "event",
                "image_url": "/static/img/monte.png",
                "short_description": "Short <b>description</b>",
                "full_description": "Full <i>description</i>",
                "tags": "Event, <b>Business</b>",
            },
        )

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.json()["pk"])
        self.assertEqual(project.title, "Safe Project")
        self.assertEqual(project.short_description, "Short description")
        self.assertEqual(project.full_description, "Full description")
        self.assertEqual(project.tags, "Event, Business")

    def test_create_project_ajax_allows_only_post(self):
        self.client.login(username="owner", password="StrongPassword123!")
        response = self.client.get(reverse("main:create_project_ajax"))
        self.assertEqual(response.status_code, 405)

    def test_editor_cannot_create_or_delete_project(self):
        self.client.login(username="editor-user", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Blocked Create",
                "category": "event",
                "image_url": "/static/img/monte.png",
                "short_description": "Short",
                "full_description": "Full",
                "tags": "Event",
            },
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_editor_can_update_project(self):
        self.client.login(username="editor-user", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:update_project", args=[self.project.id]),
            {
                "title": "Edited By Editor",
                "category": "fashion",
                "image_url": "/static/img/monte.png",
                "short_description": "Edited short",
                "full_description": "Edited full",
                "tags": "Event, Business",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Edited By Editor")

    def test_superuser_can_delete_project(self):
        self.client.login(username="owner", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_dynamic_project_controls_preserve_editor_role(self):
        self.client.login(username="editor-user", password="StrongPassword123!")
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IS_EDITOR")
        self.assertContains(response, "update_project")
        self.assertNotContains(response, "project-add-button")

    def test_superuser_gets_project_modal_controls(self):
        self.client.login(username="owner", password="StrongPassword123!")
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "project-add-button")
        self.assertContains(response, "project-form")
        self.assertContains(response, "create_project_ajax")
