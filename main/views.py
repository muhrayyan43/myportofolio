from django.contrib import messages
from django.shortcuts import render, redirect

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