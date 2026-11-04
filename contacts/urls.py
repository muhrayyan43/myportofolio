from django.urls import path

from contacts import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="contact_list"),
    path("add/", views.contact_add, name="contact_add"),
]