from django import forms
from .models import Experience, Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'image_url', 'short_description', 'full_description', 'tags']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'category', 'location', 'started_at', 'ended_at', 'description']
        widgets = {
            'started_at': forms.DateInput(attrs={'type': 'date'}),
            'ended_at': forms.DateInput(attrs={'type': 'date'}),
        }