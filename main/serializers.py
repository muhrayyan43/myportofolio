from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class ProjectSerializer(serializers.ModelSerializer):
    """JSON contract for Project, plus star info for the requesting user."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack", "year", "url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    """JSON contract for Experience """

    category_display = serializers.CharField(
        source="get_category_display", read_only=True,
    )
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "created_at", "updated_at", "star_count", "is_starred",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # -- Field validation (mirrors ExperienceForm.clean_<field>) ---------

    @staticmethod
    def _clean_text(value, label):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError(
                f"{label} tidak boleh kosong atau hanya berisi tag HTML."
            )
        return value

    def validate_title(self, value):
        return self._clean_text(value, "Posisi")

    def validate_description(self, value):
        return self._clean_text(value, "Deskripsi")

    def validate_thumbnail(self, value):
        # Store "no thumbnail" as NULL, like ExperienceForm does.
        return value or None

    def validate(self, attrs):
        """ended_at must not be before started_at.

        On PATCH only some fields arrive, so the missing one is read
        from the instance being updated.
        """
        instance = self.instance
        started = attrs.get("started_at", getattr(instance, "started_at", None))
        ended = attrs.get("ended_at", getattr(instance, "ended_at", None))
        if started and ended and ended < started:
            raise serializers.ValidationError({
                "ended_at": "Tanggal selesai tidak boleh sebelum tanggal mulai.",
            })
        return attrs

    def _current_user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_star_count(self, obj):
        annotated = getattr(obj, "star_total", None)
        return annotated if annotated is not None else obj.starred_by.count()

    def get_is_starred(self, obj):
        user = self._current_user()
        if user is None or not user.is_authenticated:
            return False
        annotated = getattr(obj, "user_starred", None)
        if annotated is not None:
            return annotated
        return obj.starred_by.filter(pk=user.pk).exists()