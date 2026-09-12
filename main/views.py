from django.shortcuts import render
from main.models import Experience

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

