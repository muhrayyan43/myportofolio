from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from contacts.forms import ContactForm
from contacts.models import Contact
from main.permissions import can_create_or_delete
from main.views import AUTHOR_NAME


def _plain_text(message, status):
    """Short text response for errors; the page shows it via textContent."""
    return HttpResponse(
        message, status=status, content_type="text/plain; charset=utf-8"
    )


def _render_rows(request, contacts):
    """Render only the table rows: the fragment HTMX swaps into #contact-rows."""
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


def contact_list(request):
    """Full page: portfolio layout, add form (owner only) and the contact table."""
    context = {"name": AUTHOR_NAME, "contacts": Contact.objects.all()}
    return render(request, "contacts/index.html", context)


@require_POST
def contact_add(request):
    """Create a contact and return the refreshed rows fragment.

    Non-owners get 403 and invalid input gets 400 with a readable message.
    HTMX does not swap 4xx responses, so the table stays unchanged and the
    form keeps what the user typed.
    """
    if not can_create_or_delete(request.user):
        return _plain_text("Kamu tidak punya akses untuk menambah kontak.", 403)

    form = ContactForm(request.POST)
    if not form.is_valid():
        messages = [msg for errors in form.errors.values() for msg in errors]
        return _plain_text(" ".join(messages), 400)

    form.save()
    return _render_rows(request, Contact.objects.all())