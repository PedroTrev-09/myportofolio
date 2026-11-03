import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.validation import clean_experience_description


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
    """Render only the Experience page shell; data is loaded through AJAX."""
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "all").strip().lower() or "all"

    context = {
        "headerName": "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "title_query": title_query,
        "category_query": category_query,
        "form": ExperienceForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "experience.html", context)


def get_experiences_json(request):
    """Return public experience data for the AJAX Experience list."""
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "all").strip().lower()

    experiences = Experience.objects.all().order_by("-started_at")

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    if category_query and category_query != "all":
        experiences = experiences.filter(category=category_query)

    data = []
    for experience in experiences:
        description = clean_experience_description(experience.description)

        data.append(
            {
                "model": "main.experience",
                "pk": str(experience.id),
                "fields": {
                    "title": strip_tags(experience.title).strip(),
                    "location": strip_tags(experience.location).strip(),
                    "description": description.strip(),
                    "category": experience.category,
                    "category_display": experience.get_category_display(),
                    "started_at": experience.started_at.isoformat(),
                    "ended_at": experience.ended_at.isoformat() if experience.ended_at else None,
                    "is_ongoing": experience.is_ongoing,
                },
            }
        )

    return JsonResponse(data, safe=False)


def get_projects_json(request):
    """Return public project data for the AJAX project list."""
    title_query = request.GET.get("title", "").strip()

    projects = Project.objects.prefetch_related("starred_by").all().order_by("-created_at")
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        is_starred = request.user.is_authenticated and request.user in starred_users

        data.append(
            {
                "model": "main.project",
                "pk": str(project.id),
                "fields": {
                    "title": project.title,
                    "category": project.category,
                    "image_url": project.image_url,
                    "short_description": project.short_description,
                    "full_description": project.full_description,
                    "tags": project.tags,
                    "created_at": project.created_at.isoformat(),
                    "star_count": len(starred_users),
                    "is_starred": is_starred,
                },
            }
        )

    return JsonResponse(data, safe=False)


def show_project(request):
    """Render only the project page shell; project data is loaded through AJAX."""
    title_query = request.GET.get("title", "").strip()

    context = {
        "headerName": "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "title_query": title_query,
        "form": ProjectForm(),
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
        "headerName": "Haikal Rafka",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        next_url = request.POST.get("next", request.GET.get("next", ""))
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            next_url = ""
        response = redirect(next_url or "main:show_main")

        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return response

    context = {
        "name": "Haikal Rafka A Rahman",
        "headerName": "Haikal Rafka",
        "form": form,
        "next_url": request.POST.get("next", request.GET.get("next", "")),
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
        "headerName": "Haikal Rafka",
        "form": form,
        "is_edit": False,
    }

    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def update_project(request, id):
    if not can_manage_data(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=id)

    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated")
        return redirect("main:show_project")

    context = {
        "name": "Haikal Rafka A Rahman",
        "headerName": "Haikal Rafka",
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
        "headerName": "Haikal Rafka",
        "form": form,
        "is_edit": False,
    }

    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_experience(request, id):
    if not can_edit_data(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=id)

    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience updated")
        return redirect("main:show_experience")

    context = {
        "name": "Haikal Rafka A Rahman",
        "headerName": "Haikal Rafka",
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


@require_POST
def create_experience_ajax(request):
    """Create an Experience through AJAX; only the portfolio owner may do this."""
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pengalaman."},
            status=403,
        )

    form = ExperienceForm(request.POST)

    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {
                "message": "Pengalaman berhasil ditambahkan.",
                "pk": str(experience.id),
            },
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def create_project_ajax(request):
    """Create a project through AJAX; only the portfolio owner may do this."""
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)

    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
