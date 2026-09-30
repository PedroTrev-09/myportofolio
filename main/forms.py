from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .models import Experience, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "category",
            "image_url",
            "short_description",
            "full_description",
            "tags",
        ]

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_category(self):
        return strip_tags(self.cleaned_data["category"]).strip()

    def clean_image_url(self):
        return strip_tags(self.cleaned_data["image_url"]).strip()

    def clean_short_description(self):
        return strip_tags(self.cleaned_data["short_description"]).strip()

    def clean_full_description(self):
        return strip_tags(self.cleaned_data["full_description"]).strip()

    def clean_tags(self):
        return strip_tags(self.cleaned_data["tags"]).strip()


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "category",
            "location",
            "started_at",
            "ended_at",
            "description",
        ]
        widgets = {
            "started_at": forms.DateInput(attrs={"type": "date"}),
            "ended_at": forms.DateInput(attrs={"type": "date"}),
        }
