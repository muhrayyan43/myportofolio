import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.permissions import require_can_edit, require_owner


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
    context = {
        "name": AUTHOR_NAME,
        "query": request.GET.get("q", "").strip(),
    }
    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    require_owner(request.user)

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
    require_can_edit(request.user)


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
    require_owner(request.user)

    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
    return redirect("main:show_experience")


# ------------------------------------------------------------------
# Experience: JSON helpers (shared by the list and create endpoints)
# ------------------------------------------------------------------
def _iso_date(value):
    """Return a date as 'YYYY-MM-DD', or None when empty."""
    return value.isoformat() if value else None


def get_experience_queryset(query=""):
    """Return experiences annotated with ``star_count``, optionally filtered.

    ``annotate(Count(...))`` computes every star count inside the main
    SQL query, so listing N experiences costs one query instead of
    N + 1. ``distinct=True`` keeps the count correct if more joins are
    ever chained onto this queryset.
    """
    experiences = Experience.objects.annotate(
        star_count=Count("starred_by", distinct=True)
    )
    if query:
        experiences = experiences.filter(
            Q(title__icontains=query) | Q(company__icontains=query)  # FIELD: title, company
        )
    return experiences


def get_starred_experience_ids(user):
    """Return the ids of experiences starred by ``user`` in one query.

    Anonymous users get an empty set without touching the database.
    """
    if not user.is_authenticated:
        return frozenset()
    return frozenset(user.starred_experiences.values_list("id", flat=True))


def serialize_experience(experience, starred_ids=frozenset()):
    """Convert one Experience into a JSON-safe dict.

    Built by hand (no serializers / model_to_dict) so the payload can
    carry viewer-specific data such as ``is_starred``. ``star_count``
    comes from the queryset annotation; a freshly created object has
    no annotation, so it falls back to 0.
    """
    return {
        "id": experience.id,
        # FIELD: adjust the keys below to match your Experience model.
        "title": experience.title,
        "company": experience.company,
        "category": experience.category,
        "category_display": experience.get_category_display(),
        "description": experience.description,
        "started_at": _iso_date(experience.started_at),
        "ended_at": _iso_date(experience.ended_at),
        "star_count": getattr(experience, "star_count", 0),
        "is_starred": experience.id in starred_ids,
    }


def get_experience_json(request):
    query = request.GET.get("q", "").strip()
    experiences = get_experience_queryset(query)
    starred_ids = get_starred_experience_ids(request.user)
    results = [serialize_experience(item, starred_ids) for item in experiences]
    return JsonResponse({
        "query": query,
        "count": len(results),
        "results": results,
    })


@require_POST
def toggle_experience_star(request, experience_id):
    """Star or unstar an experience for the current user (AJAX, JSON).

    No @login_required: its redirect would be followed by fetch() and
    hand JavaScript a 200 HTML login page. An explicit 401 JSON reply
    is something the front-end can act on.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Silakan login untuk memberi bintang."},
            status=401,
        )

    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        is_starred = False
    else:
        experience.starred_by.add(request.user)
        is_starred = True

    return JsonResponse({
        "success": True,
        "is_starred": is_starred,
        "star_count": experience.starred_by.count(),
    })

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
        "title_query": request.GET.get("title", "").strip(),
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)


@login_required(login_url="/login/")
def create_project(request):
    require_owner(request.user)

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
    require_can_edit(request.user)

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
    require_owner(request.user)

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        wants_json = "application/json" in request.headers.get("Accept", "")
        if wants_json:
            return JsonResponse({"deleted": True, "pk": str(project_id)})
        messages.success(request, "Proyek berhasil dihapus!")
        return redirect("main:show_project")
    return redirect("main:show_project")


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
            is_starred = False
        else:
            project.starred_by.add(request.user)
            is_starred = True

        wants_json = "application/json" in request.headers.get("Accept", "")
        if wants_json:
            return JsonResponse({
                "is_starred": is_starred,
                "star_count": project.starred_by.count(),
            })

    return redirect("main:show_project")

@login_required(login_url="/login/")
def show_starred_projects(request):
    context = {
        "name": AUTHOR_NAME,
        "project_list": request.user.starred_projects.all(),
    }
    return render(request, "starred.html", context)


@require_POST
def create_project_ajax(request):
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


def get_project_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("starred_by").all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    is_authenticated = request.user.is_authenticated
    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        is_starred = (
            is_authenticated and request.user in starred_users
        )
        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "year": project.year,
                "url": project.url or "",
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": ", ".join(
                    u.username for u in starred_users
                ),
            },
        })
    return JsonResponse(data, safe=False)


def get_project_xml(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    payload = serializers.serialize(
        "xml", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(payload, content_type="application/xml")