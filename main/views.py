from django.shortcuts import render, redirect, get_object_or_404
from main.models import Experience, Project
from main.forms import ProjectForm
from django.core import serializers
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages

def show_main(request):
    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "npm": "2506553383",
        "study_program": "S1 Sistem Informasi",
        "bio": "Originally from Lombok. Currently balancing my third-semester coursework with building a B2B platform for campus event management. I enjoy crafting digital solutions from the ground up.",
        "about": (
            "I am a versatile graphic designer and Information Systems student at Universitas Indonesia. With freelance experience in branding, visual communication, and photography, I thrive in both independent projects and team settings. I blend creative design with structured project management to deliver high-quality, impactful results tailored to client needs."
        )
    }
    return render(request, "index.html", context)


def show_experience(request):
    experiences = Experience.objects.all().order_by('-started_at')
    
    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "experience_list": experiences, 
    }
    return render(request, "experience.html", context)


def get_projects_json(request):
    projects = Project.objects.all().order_by('-created_at')
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def show_project(request):
    json_response = get_projects_json(request)
    
    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    
    context = {
        "headerName" : "Haikal Rafka",
        "name": "Haikal Rafka A Rahman",
        "project_list": projects,
    }
    return render(request, "project.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST":
        secret_code = request.POST.get('secret_code')

        if secret_code == settings.PORTFOLIO_SECRET:
            if form.is_valid():
                form.save()
                return redirect("main:show_project")
        else:
            messages.error(request, "bukan admin ya?, hahay.")

    context = {"headerName": "Haikal Rafka", "name": "Haikal Rafka A Rahman", "form": form}
    return render(request, "project_form.html", context)

def delete_project(request, id):
    project = get_object_or_404(Project, pk=id)
    if request.method == "POST":
        secret_code = request.POST.get('secret_code')
        if secret_code == settings.PORTFOLIO_SECRET.strip():
            project.delete()
            messages.success(request, "Proyek berhasil dihapus!")
        else:
            messages.error(request, "bukan admin ya?, hahay.")
            
    return redirect("main:show_project")