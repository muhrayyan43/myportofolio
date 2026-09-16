from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.http import HttpResponse

from main.models import Experience, Project
from main.forms import ProjectForm


def show_main(request):
    context = {
        "name": "Muhammad Rayyan Basalamah",
        "npm": "2406496372",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I am highly interested in Machine Learning, specifically "
            "in how data-driven models can solve complex real-world "
            "problems and optimize business systems."
        ),
    }

    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Rayyan Basalamah",
        "experience_list": Experience.objects.all(),
    }

    return render(request, "experience.html", context)


def show_project(request):
    context = {
        "name": "Muhammad Rayyan Basalamah",
        "project_list": Project.objects.all(),
    }

    return render(request, "project.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")

    context = {
        "name": "Muhammad Rayyan Basalamah",
        "form": form,
    }

    return render(request, "project_form.html", context)

def get_project_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def get_project_xml(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_xml = serializers.serialize("xml", projects)
    return HttpResponse(projects_xml, content_type="application/xml")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")
        return redirect("main:show_project")

    return redirect("main:show_project")