from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from contacts.forms import ContactForm
from contacts.models import Contact
from main.permissions import can_create_or_delete, can_edit
from main.views import AUTHOR_NAME


def _plain_text(message, status):
    """Short text response for errors; the page shows it via textContent."""
    return HttpResponse(
        message, status=status, content_type="text/plain; charset=utf-8"
    )


def _render_rows(request, contacts):
    """Render only the table rows: the fragment HTMX swaps into #contact-rows."""
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


def _render_row(request, contact):
    """Render one display row (the normal, non-editing version)."""
    return render(request, "contacts/_contact_row.html", {"contact": contact})


def _render_edit_row(request, contact, form):
    """Render one row as an inline edit form, with errors when ``form`` has any."""
    return render(
        request,
        "contacts/_contact_edit_row.html",
        {"contact": contact, "form": form},
    )


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


@require_GET
def contact_search(request):
    """Return the rows whose name or email contains ``q`` (all rows if empty)."""
    query = request.GET.get("q", "").strip()
    contacts = Contact.objects.all()
    if query:
        contacts = contacts.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )
    return _render_rows(request, contacts)


@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    """Delete a contact and reply 200 with an empty body.

    hx-swap="outerHTML" replaces the <tr> with that empty body, which removes
    the row. The status must stay 200: HTMX skips the swap for 204 No
    Content, so the row would stay on screen.
    """
    if not can_create_or_delete(request.user):
        return _plain_text("Kamu tidak punya akses untuk menghapus kontak.", 403)

    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse("")


@require_GET
def contact_edit(request, pk):
    """Return the row as an inline edit form (editors and owners only)."""
    if not can_edit(request.user):
        return _plain_text("Kamu tidak punya akses untuk mengubah kontak.", 403)

    contact = get_object_or_404(Contact, pk=pk)
    return _render_edit_row(request, contact, ContactForm(instance=contact))


@require_GET
def contact_row(request, pk):
    """Return the normal display row; the Batal button uses it to cancel."""
    contact = get_object_or_404(Contact, pk=pk)
    return _render_row(request, contact)


@require_http_methods(["PUT"])
def contact_update(request, pk):
    """Save an inline edit sent with hx-put and return the display row.

    Django fills request.POST only for POST requests, so the PUT body (for
    example ``name=Ani&email=ani%40example.com``) is parsed with QueryDict.
    Invalid input re-renders the edit row with its errors. That reply is a
    200 on purpose, because HTMX only swaps successful responses.
    """
    if not can_edit(request.user):
        return _plain_text("Kamu tidak punya akses untuk mengubah kontak.", 403)

    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(QueryDict(request.body), instance=contact)
    if not form.is_valid():
        return _render_edit_row(request, contact, form)

    form.save()
    return _render_row(request, contact)