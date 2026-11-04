from django.db import models


class Contact(models.Model):
    """Address-book entry managed by the HTMX contacts page (Tutorial 06)."""

    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name