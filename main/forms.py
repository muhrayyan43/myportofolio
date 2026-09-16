from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput

from main.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "year",
            "url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "year": "Tahun",
            "url": "URL Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "year": NumberInput(
                attrs={
                    "placeholder": "2026",
                    "min": 2000,
                    "max": 2100,
                }
            ),
            "url": URLInput(
                attrs={
                    "placeholder": "https://github.com/muhrayyan43/myportofolio",
                }
            ),
        }