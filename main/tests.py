from datetime import date

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
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
        self.assertContains(response, "js/projects.js")
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

    def test_editor_cannot_bypass_projects_api_via_html_update(self):
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

        self.assertEqual(response.status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Monte De Carlo")

    def test_superuser_can_delete_project(self):
        self.client.login(username="owner", password="StrongPassword123!")

        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_project_api_controls_are_owner_only(self):
        self.client.login(username="editor-user", password="StrongPassword123!")
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'const IS_SUPERUSER = "false" === "true";')
        self.assertContains(response, reverse("api:project-list"))
        self.assertNotContains(response, "project-add-button")

    def test_superuser_gets_project_modal_controls(self):
        self.client.login(username="owner", password="StrongPassword123!")
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "project-add-button")
        self.assertContains(response, 'id="project-form"')
        self.assertContains(
            response,
            f'action="{reverse("api:project-list")}"',
        )


class ExperienceAjaxTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Graphic Designer & Photographer",
            location="Lombok, NTB",
            description="Mengelola visual branding secara konsisten.",
            category="part-time",
            started_at=date(2025, 1, 1),
        )

        self.normal_user = User.objects.create_user(
            username="normal-experience-user",
            password="StrongPassword123!",
        )
        self.editor_user = User.objects.create_user(
            username="editor-experience-user",
            password="StrongPassword123!",
        )
        self.superuser = User.objects.create_superuser(
            username="experience-owner",
            password="StrongPassword123!",
            email="experience-owner@example.com",
        )

        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor_user.groups.add(editor_group)

    def test_experience_page_uses_ajax_shell(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, "experience-search-form")
        self.assertContains(response, "experience-loading")
        self.assertContains(response, "experience-error")
        self.assertContains(response, "experience-empty")
        self.assertContains(response, "js/experiences.js")
        self.assertNotContains(response, self.experience.title)

    def test_experiences_json_returns_public_data(self):
        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["model"], "main.experience")
        self.assertEqual(data[0]["pk"], str(self.experience.id))
        self.assertEqual(data[0]["fields"]["title"], self.experience.title)
        self.assertEqual(data[0]["fields"]["category_display"], "Part-Time")
        self.assertTrue(data[0]["fields"]["is_ongoing"])

    def test_experiences_json_strips_html_from_existing_text(self):
        self.experience.description = "<ul><li>First item</li><li>Second item</li></ul>"
        self.experience.save(update_fields=["description"])

        response = self.client.get(reverse("main:get_experiences_json"))
        description = response.json()[0]["fields"]["description"]

        self.assertNotIn("<", description)
        self.assertNotIn(">", description)
        self.assertEqual(description, "- First item\n- Second item")

    def test_experiences_json_supports_title_and_category_search(self):
        Experience.objects.create(
            title="UI Research Assistant",
            location="Depok",
            description="Menganalisis kebutuhan pengguna.",
            category="research",
            started_at=date(2026, 2, 1),
        )

        response = self.client.get(
            reverse("main:get_experiences_json"),
            {"title": "Graphic"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            reverse("main:get_experiences_json"),
            {"category": "research"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["fields"]["category"], "research")

        response = self.client.get(
            reverse("main:get_experiences_json"),
            {"title": "Does Not Exist"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_experience_page_is_readable_by_all_roles(self):
        for username in [None, self.normal_user.username, self.editor_user.username, self.superuser.username]:
            self.client.logout()
            if username:
                password = "StrongPassword123!"
                self.client.login(username=username, password=password)

            response = self.client.get(reverse("main:show_experience"))
            self.assertEqual(response.status_code, 200)

        self.client.logout()
        self.client.login(username=self.superuser.username, password="StrongPassword123!")
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "add-experience-modal")

    def test_create_experience_ajax_requires_superuser(self):
        payload = {
            "title": "Campus Event Manager",
            "location": "Depok",
            "started_at": "2026-09-01",
            "category": "part-time",
            "description": "Mengelola kegiatan kampus.",
        }

        response = self.client.post(reverse("main:create_experience_ajax"), payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(response.json()["message"], "Hanya pemilik portofolio yang dapat menambahkan pengalaman.")

        self.client.login(username=self.normal_user.username, password="StrongPassword123!")
        response = self.client.post(reverse("main:create_experience_ajax"), payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

        self.client.login(username=self.editor_user.username, password="StrongPassword123!")
        response = self.client.post(reverse("main:create_experience_ajax"), payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

        self.client.login(username=self.superuser.username, password="StrongPassword123!")
        response = self.client.post(reverse("main:create_experience_ajax"), payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), 2)
        self.assertEqual(response.json()["message"], "Pengalaman berhasil ditambahkan.")

    def test_create_experience_ajax_returns_validation_errors(self):
        self.client.login(username=self.superuser.username, password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "<img src=x onerror=alert(1)>",
                "location": "Depok",
                "started_at": "2026-09-01",
                "category": "part-time",
                "description": "Description",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertEqual(Experience.objects.count(), 1)

    def test_create_experience_ajax_rejects_html_only_required_fields(self):
        self.client.login(username=self.superuser.username, password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Valid Title",
                "location": "<b></b>",
                "started_at": "2026-09-01",
                "category": "part-time",
                "description": "<img src=x onerror=alert(1)>",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("location", response.json()["errors"])
        self.assertIn("description", response.json()["errors"])
        self.assertEqual(Experience.objects.count(), 1)

    def test_create_experience_ajax_strips_html_from_text_fields(self):
        self.client.login(username=self.superuser.username, password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Safe <b>Experience</b>",
                "location": "Depok <i>Campus</i>",
                "started_at": "2026-09-01",
                "category": "part-time",
                "description": "Managed <b>event</b> operations.",
            },
        )

        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get(pk=response.json()["pk"])
        self.assertEqual(experience.title, "Safe Experience")
        self.assertEqual(experience.location, "Depok Campus")
        self.assertEqual(experience.description, "Managed event operations.")

    def test_create_experience_ajax_allows_only_post(self):
        self.client.login(username=self.superuser.username, password="StrongPassword123!")
        response = self.client.get(reverse("main:create_experience_ajax"))
        self.assertEqual(response.status_code, 405)

    def test_editor_can_update_but_cannot_create_or_delete_experience(self):
        self.client.login(username=self.editor_user.username, password="StrongPassword123!")

        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Blocked Create",
                "location": "Depok",
                "started_at": "2026-09-01",
                "category": "part-time",
                "description": "Should not be created.",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.id]),
            {
                "title": "Edited By Editor",
                "location": "Jakarta",
                "started_at": "2025-01-01",
                "category": "part-time",
                "description": "Updated experience.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited By Editor")

        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_superuser_can_delete_experience(self):
        self.client.login(username=self.superuser.username, password="StrongPassword123!")

        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_create_experience_ajax_enforces_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username=self.superuser.username, password="StrongPassword123!")

        page = csrf_client.get(reverse("main:show_experience"))
        self.assertIn("csrftoken", page.cookies)
        csrf_token = page.cookies["csrftoken"].value

        payload = {
            "title": "CSRF Protected Experience",
            "location": "Depok",
            "started_at": "2026-09-01",
            "category": "part-time",
            "description": "Protected by CSRF token.",
        }

        response = csrf_client.post(reverse("main:create_experience_ajax"), payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

        response = csrf_client.post(
            reverse("main:create_experience_ajax"),
            payload,
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), 2)


class InputValidationRegressionTest(TestCase):
    def test_experience_rejects_reversed_dates(self):
        from main.forms import ExperienceForm
        form = ExperienceForm(data={"title": "Designer", "location": "Depok",
            "category": "part-time", "description": "Design work",
            "started_at": "2026-09-01", "ended_at": "2026-08-01"})
        self.assertFalse(form.is_valid())
        self.assertIn("ended_at", form.errors)

    def test_project_rejects_unsafe_image_and_empty_markup(self):
        from main.forms import ProjectForm
        base = {"title": "Portfolio", "category": "design", "tags": "Django",
            "short_description": "Short", "full_description": "Full", "image_url": "/static/img/monte.png"}
        for image in ("javascript:alert(1)", "data:text/html,x", "http://[invalid", "//example.com/x", "/\\example.com/x"):
            with self.subTest(image=image):
                form = ProjectForm(data={**base, "image_url": image})
                self.assertFalse(form.is_valid())
                self.assertIn("image_url", form.errors)
        form = ProjectForm(data={**base, "short_description": "<b></b>"})
        self.assertFalse(form.is_valid())
        self.assertIn("short_description", form.errors)


class LoginRedirectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="redirect-user", password="test-password")

    def test_login_returns_to_portfolio_page(self):
        response = self.client.post(reverse("main:login"), {"username": "redirect-user", "password": "test-password", "next": "/project/"})
        self.assertRedirects(response, "/project/", fetch_redirect_response=False)

    def test_login_rejects_external_redirect(self):
        for target in ("https://example.com/", "//example.com/", "javascript:alert(1)"):
            with self.subTest(target=target):
                self.client.logout()
                response = self.client.post(reverse("main:login"), {"username": "redirect-user", "password": "test-password", "next": target})
                self.assertRedirects(response, "/", fetch_redirect_response=False)


    def test_login_form_renders_with_or_without_next(self):
        for params in ({}, {"next": "/project/"}):
            response = self.client.get(reverse("main:login"), params)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'id="id_username"')
        response = self.client.post(reverse("main:login"), {"username": "wrong", "password": "wrong", "next": "/project/"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="/project/"')
