from django.forms import (
    ModelForm,
    TextInput,
    Textarea,
    NumberInput,
    URLInput,
    Select,
    DateInput,
)

from main.models import Experience, Project


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
                attrs={"placeholder": "Portfolio Website", "maxlength": 255}
            ),
            "description": Textarea(
                attrs={"placeholder": "Ceritakan proyekmu", "rows": 3}
            ),
            "tech_stack": TextInput(
                attrs={"placeholder": "Django, Python, HTML, CSS"}
            ),
            "year": NumberInput(
                attrs={"placeholder": "2026", "min": 2000, "max": 2100}
            ),
            "url": URLInput(
                attrs={
                    "placeholder": "https://github.com/muhrayyan43/myportofolio"
                }
            ),
        }


class ExperienceForm(ModelForm):
    """
    ModelForm untuk Experience.

    Punya 6 field yang bisa diisi user dengan tipe data bervariasi
    (Char, Text, Choices, URL, Date, Date) — memenuhi syarat minimal
    3 field selain id & timestamp.

    Field yang sengaja TIDAK dimasukkan:
      - id (UUID, auto)
      - created_at / updated_at (auto-managed timestamps)
    """

    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Judul / Posisi",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "Thumbnail URL",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai (kosongkan jika masih berjalan)",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Software Engineer Intern @ Company",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan apa yang kamu kerjakan di sini",
                    "rows": 4,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={"placeholder": "https://.../logo.png"}
            ),
            "started_at": DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "ended_at": DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTML5 <input type="date"> mengirim & butuh format YYYY-MM-DD
        self.fields["started_at"].input_formats = ["%Y-%m-%d"]
        self.fields["ended_at"].input_formats = ["%Y-%m-%d"]

    def clean(self):
        """Validasi lintas-field: ended_at tidak boleh mendahului started_at."""
        cleaned = super().clean()
        started = cleaned.get("started_at")
        ended = cleaned.get("ended_at")
        if started and ended and ended < started:
            self.add_error(
                "ended_at",
                "Tanggal selesai tidak boleh sebelum tanggal mulai.",
            )
        return cleaned