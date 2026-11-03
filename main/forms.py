from django import forms
from django.core.exceptions import ValidationError
from .validation import experience_dates, image_url, plain_text

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
        return plain_text(self.cleaned_data["title"])

    def clean_category(self):
        return plain_text(self.cleaned_data["category"])

    def clean_image_url(self):
        return image_url(self.cleaned_data["image_url"])

    def clean_short_description(self):
        return plain_text(self.cleaned_data["short_description"])

    def clean_full_description(self):
        return plain_text(self.cleaned_data["full_description"])

    def clean_tags(self):
        return plain_text(self.cleaned_data["tags"])


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

    def clean_title(self):
        return plain_text(self.cleaned_data["title"])

    def clean_location(self):
        return plain_text(self.cleaned_data["location"])

    def clean_description(self):
        return plain_text(self.cleaned_data["description"])

    def clean(self):
        data = super().clean()
        try:
            experience_dates(data.get("started_at"), data.get("ended_at"))
        except ValidationError as error:
            self.add_error("ended_at", error)
        return data
