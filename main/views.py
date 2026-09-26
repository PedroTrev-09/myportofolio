import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from main.models import Experience, Project
from main.forms import ProjectForm, ExperienceForm


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'No login session yet') 
    
    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "npm": "2506553383",
        "study_program": "S1 Sistem Informasi",
        "bio": "Originally from Lombok. Currently balancing my third-semester coursework with building a B2B platform for campus event management. I enjoy crafting digital solutions from the ground up.",
        "about": "I am a versatile graphic designer and Information Systems student at Universitas Indonesia. With freelance experience in branding, visual communication, and photography, I thrive in both independent projects and team settings. I blend creative design with structured project management to deliver high-quality, impactful results tailored to client needs.",
        "last_login": last_login, 
    }
    return render(request, "index.html", context)

def show_experience(request):
    experiences = Experience.objects.all().order_by('-started_at')

    user_is_editor = False
    if request.user.is_authenticated:
        user_is_editor = is_editor(request.user)

    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "experience_list": experiences, 
        "is_editor": user_is_editor
    }
    return render(request, "experience.html", context)

def get_projects_json(request):
    projects = Project.objects.all().order_by('-created_at')
    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True) 
    return HttpResponse(projects_json, content_type="application/json")

def show_project(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize("json", json_response.content.decode("utf-8"))
    projects = [project.object for project in projects]

    user_is_editor = False
    if request.user.is_authenticated:
        user_is_editor = is_editor(request.user)

    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "project_list": projects,
        "is_editor": user_is_editor
    }
    return render(request, "project.html", context)

def register(request):
    form = UserCreationForm(request.POST or None) 
    if request.method == "POST" and form.is_valid():
        form.save() 
        messages.success(request, "Account successfully made. Login again") 
        return redirect("main:login") 
    context = {"name": "Haikal Rafka A Rahman", "form": form}
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None) 
    if request.method == "POST" and form.is_valid():
        user = form.get_user() 
        login(request, user) 
        response = redirect("main:show_main") 
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) 
        return response
    context = {"name": "Haikal Rafka A Rahman", "form": form}
    return render(request, "login.html", context)

def logout_user(request):
    logout(request) 
    response = redirect("main:show_main") 
    response.delete_cookie('last_login') 
    return response

@login_required(login_url="/login/")
def create_project(request):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_project")
    context = {"name": "Haikal Rafka A Rahman", "form": form}
    return render(request, "project_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted")
    return redirect("main:show_project")

@login_required(login_url="/login/") 
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST": 
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_project")

@login_required(login_url="/login/")
def create_experience(request):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_experience")

    context = {"name": "Haikal Rafka A Rahman", "form": form}
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_experience(request, id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Deleted experience!")
    return redirect("main:show_experience")

def is_editor(user):
    return user.groups.filter(name='Editor').exists()