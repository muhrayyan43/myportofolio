import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


AUTHOR_NAME = "Muhammad Rayyan Basalamah"


# ------------------------------------------------------------------
# Auth: register, login, logout
# ------------------------------------------------------------------
def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": AUTHOR_NAME,
        "form": form,
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
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": AUTHOR_NAME,
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_main(request):
    last_login = request.COOKIES.get(
        "last_login", "Belum ada sesi login / Cookie tidak ditemukan"
    )
    context = {
        "name": AUTHOR_NAME,
        "npm": "2406496372",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I am highly interested in Machine Learning, specifically "
            "in how data-driven models can solve complex real-world "
            "problems and optimize business systems."
        ),
        "last_login": last_login,
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


@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    """
    Update pakai instance existing → form.save() akan UPDATE, bukan INSERT.
    Menggabungkan pengambilan data by id + penyimpanan form seperti hint di soal.
    """
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

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
# Project: list + CRUD + JSON / XML
# ------------------------------------------------------------------
def show_project(request):
    context = {
        "name": AUTHOR_NAME,
        "project_list": Project.objects.all(),
    }
    return render(request, "project.html", context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")

    context = {
        "name": AUTHOR_NAME,
        "form": form,
        "form_title": "Tambah Proyek",
        "submit_label": "Tambah Proyek",
    }
    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_project")

    context = {
        "name": AUTHOR_NAME,
        "form": form,
        "form_title": f"Edit Proyek — {project.title}",
        "submit_label": "Simpan Perubahan",
    }
    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")
        return redirect("main:show_project")
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


def get_project_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    # use_natural_foreign_keys=True renders starred_by as [["username"], ...]
    # instead of [1, 2] so we don't leak internal DB ids through the
    # public API and the payload stays human-readable.
    payload = serializers.serialize(
        "json", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(payload, content_type="application/json")


def get_project_xml(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    payload = serializers.serialize(
        "xml", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(payload, content_type="application/xml")