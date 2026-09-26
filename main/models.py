import uuid
from django.db import models
from django.contrib.auth.models import User

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Lombok, NTB")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    
    started_at = models.DateField() 
    ended_at = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    full_description = models.TextField()
    image_url = models.CharField(max_length=255) 
    category = models.CharField(max_length=50) 
    tags = models.CharField(max_length=255) 
    created_at = models.DateField(auto_now_add=True)
    
    starred_by = models.ManyToManyField(User, related_name="starred_projects", blank=True) #
    
    def __str__(self):
        return self.title
    
    @property
    def tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []