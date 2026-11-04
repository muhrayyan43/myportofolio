from django.urls import path

from contacts import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="contact_list"),
    path("add/", views.contact_add, name="contact_add"),
    path("search/", views.contact_search, name="contact_search"),
    path("<int:pk>/delete/", views.contact_delete, name="contact_delete"),
]