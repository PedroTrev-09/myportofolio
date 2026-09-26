from django.urls import path
from main.views import (
    show_main, show_experience, show_project, create_project, get_projects_json, 
    delete_project, register, login_user, logout_user, toggle_star, 
    create_experience, delete_experience
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("project/", show_project, name="show_project"),
    path('projects/add/', create_project, name='create_project'),
    path('api/projects/', get_projects_json, name='get_projects_json'),
    path('projects/<uuid:id>/delete/', delete_project, name='delete_project'),
    
    path("register/", register, name="register"), 
    path("login/", login_user, name="login"), 
    path("logout/", logout_user, name="logout"), 
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"), 
    path('experience/add/', create_experience, name='create_experience'),
    path('experience/<uuid:id>/delete/', delete_experience, name='delete_experience'),
]