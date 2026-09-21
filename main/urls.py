from django.urls import path
from main.views import (
    show_main,
    show_experience,
    show_project,
    create_project,
    get_projects_json,
    delete_project,
    create_experience,
    update_experience,
    delete_experience,
    get_experiences_json,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    
    path("experience/", show_experience, name="show_experience"),
    path('experiences/add/', create_experience, name='create_experience'),
    path('experiences/<uuid:id>/edit/', update_experience, name='update_experience'),
    path('experiences/<uuid:id>/delete/', delete_experience, name='delete_experience'),        
    path('api/experiences/', get_experiences_json, name='get_experiences_json'),

    path("project/", show_project, name="show_project"),
    path('projects/add/', create_project, name='create_project'),
    path('api/projects/', get_projects_json, name='get_projects_json'),
    path('projects/<uuid:id>/delete/', delete_project, name='delete_project'),
    
]
