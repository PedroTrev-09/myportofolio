import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def show_main(request):
    last_login = request.COOKIES.get("last_login", "No login session yet")

    context = {
        "headerName": "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "npm": "2506553383",
        "study_program": "S1 Sistem Informasi",
        "bio": "Originally from Lombok. Currently balancing my third-semester coursework with building a B2B platform for campus event management. I enjoy crafting digital solutions from the ground up.",
        "about": "I am a versatile graphic designer and Information Systems student at Universitas Indonesia. With freelance experience in branding, visual communication, and photography, I thrive in both independent projects and team settings. I blend creative design with structured project management to deliver high-quality, impactful results tailored to client needs.",
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def can_edit_data(user):
    return user.is_superuser or is_editor(user)


def can_manage_data(user):
    return user.is_superuser


def show_experience(request):
    experiences = Experience.objects.all().order_by("-started_at")

    context = {
        "headerName": "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "experience_list": experiences,
        "is_editor": is_editor(request.user),
    }
    return render(request, "experience.html", context)


def get_projects_json(request):
    projects = Project.objects.all().order_by("-created_at")

    projects_json = [
        {
            "model": "main.project",
            "pk": str(project.pk),
            "fields": {
                "title": project.title,
                "short_description": project.short_description,
                "full_description": project.full_description,
                "image_url": project.image_url,
                "category": project.category,
                "tags": project.tags,
                "created_at": project.created_at.isoformat(),
                "star_count": project.starred_by.count(),
            },
        }
        for project in projects
    ]

    return JsonResponse(projects_json, safe=False)


def show_project(request):
    projects = (
        Project.objects
        .prefetch_related("starred_by")
        .all()
        .order_by("-created_at")
    )

    context = {
        "headerName": "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "project_list": projects,
        "is_editor": is_editor(request.user),
    }
    return render(request, "project.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account successfully made. Login again")
        return redirect("main:login")

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect("main:show_main")

        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return response

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)

    response = redirect("main:show_main")
    response.delete_cookie("last_login")

    return response


@login_required(login_url="/login/")
def create_project(request):
    if not can_manage_data(request.user):
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project created")
        return redirect("main:show_project")

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form,
        "is_edit": False,
    }

    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def update_project(request, id):
    if not can_edit_data(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=id)

    form = ProjectForm(
        request.POST or None,
        instance=project
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated")
        return redirect("main:show_project")

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form,
        "project": project,
        "is_edit": True,
    }

    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def delete_project(request, id):
    if not can_manage_data(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted")

    return redirect("main:show_project")


@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.user in project.starred_by.all():
        project.starred_by.remove(request.user)
        messages.success(request, "Project unstarred")
    else:
        project.starred_by.add(request.user)
        messages.success(request, "Project starred")

    return redirect("main:show_project")


@login_required(login_url="/login/")
def create_experience(request):
    if not can_manage_data(request.user):
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience created")
        return redirect("main:show_experience")

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form,
        "is_edit": False,
    }

    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_experience(request, id):
    if not can_edit_data(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=id)

    form = ExperienceForm(
        request.POST or None,
        instance=experience
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience updated")
        return redirect("main:show_experience")

    context = {
        "name": "Haikal Rafka A Rahman",
        "form": form,
        "experience": experience,
        "is_edit": True,
    }

    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def delete_experience(request, id):
    if not can_manage_data(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Deleted experience!")

    return redirect("main:show_experience")