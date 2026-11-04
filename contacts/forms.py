from django import forms

from contacts.models import Contact


class ContactForm(forms.ModelForm):
    """Validate contact input for the add (POST) and update (PUT) views.

    Form CharFields strip surrounding whitespace by default, so a name made
    only of spaces counts as empty and is rejected; EmailField checks the
    address format. Templates auto-escape output, so no extra sanitising is
    needed here.
    """

    class Meta:
        model = Contact
        fields = ["name", "email"]
        error_messages = {
            "name": {
                "required": "Nama wajib diisi.",
                "max_length": "Nama maksimal 100 karakter.",
            },
            "email": {
                "required": "Email wajib diisi.",
                "invalid": "Format email tidak valid.",
            },
        }