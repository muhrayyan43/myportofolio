from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


AUTHOR_NAME = "Muhammad Rayyan Basalamah"


def show_main(request):
    context = {
        "name": AUTHOR_NAME,
        "npm": "2406496372",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I am highly interested in Machine Learning, specifically "
            "in how data-driven models can solve complex real-world "
            "problems and optimize business systems."
        ),
    }
    return render(request, "index.html", context)


# ------------------------------------------------------------------
# Experience: list + CRUD + JSON / XML
# ------------------------------------------------------------------
def show_experience(request):
    """List page — data diambil dari DB & dirender ke template."""
    context = {
        "name": AUTHOR_NAME,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": AUTHOR_NAME,
        "form": form,
        "form_title": "Tambah Experience",
        "submit_label": "Tambah Experience",
    }
    return render(request, "experience_form.html", context)


def update_experience(request, experience_id):
    """
    Update pakai instance existing → form.save() akan UPDATE, bukan INSERT.
    Ini menggabungkan pengambilan data by id + penyimpanan form
    seperti hint di soal.
    """
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": AUTHOR_NAME,
        "form": form,
        "form_title": f"Edit Experience — {experience.title}",
        "submit_label": "Simpan Perubahan",
    }
    return render(request, "experience_form.html", context)


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
    return redirect("main:show_experience")


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
    payload = serializers.serialize("json", experiences)
    return HttpResponse(payload, content_type="application/json")


def get_experience_xml(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
    payload = serializers.serialize("xml", experiences)
    return HttpResponse(payload, content_type="application/xml")


# ------------------------------------------------------------------
# Project: list + CRUD + JSON / XML  (update view menyusul di commit #5)
# ------------------------------------------------------------------
def show_project(request):
    context = {
        "name": AUTHOR_NAME,
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
        "name": AUTHOR_NAME,
        "form": form,
    }
    return render(request, "project_form.html", context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")
        return redirect("main:show_project")
    return redirect("main:show_project")


def get_project_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    payload = serializers.serialize("json", projects)
    return HttpResponse(payload, content_type="application/json")


def get_project_xml(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    payload = serializers.serialize("xml", projects)
    return HttpResponse(payload, content_type="application/xml")