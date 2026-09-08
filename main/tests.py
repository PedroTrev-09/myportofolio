from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Graphic Designer & Photographer",
            description="Mengelola visual branding secara konsisten.",
            category="part-time",
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
        
        self.experience.ended_at = timezone.now()
        self.experience.save()
        self.assertFalse(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        
        self.assertContains(response, "Haikal Rafka A Rahman")
        
        self.assertContains(response, "VERTURA")
        self.assertContains(response, "LOKA ORGANIZER")
        self.assertContains(response, "PT SASTRA BARRA TOGA")
        
        self.assertContains(response, f'href="{reverse("main:show_main")}#about"')