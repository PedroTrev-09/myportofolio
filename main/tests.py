from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime

from main.models import Experience, Project

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Graphic Designer & Photographer",
            description="Mengelola visual branding secara konsisten.",
            category="part-time",
            started_at=timezone.now().date(), 
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
        
        self.experience.ended_at = timezone.now().date()
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
            tags="Event, Promotion, Business"
        )

    def test_project_url_and_template(self):
        response = self.client.get(reverse("main:show_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")

    def test_project_data_rendered(self):
        response = self.client.get(reverse("main:show_project"))
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.short_description)
        self.assertContains(response, "Event")

    def test_empty_project_state(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))
        self.assertContains(response, "Belum ada project yang ditambahkan.")