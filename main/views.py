from django.shortcuts import render
from main.models import Experience


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
