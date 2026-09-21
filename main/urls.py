from django.urls import path

from main.views import (
    show_main,
    # auth
    register,
    login_user,
    logout_user,
    # experience
    show_experience,
    create_experience,
    update_experience,
    delete_experience,
    get_experience_json,
    get_experience_xml,
    # project
    show_project,
    create_project,
    update_project,
    delete_project,
    toggle_star,
    get_project_json,
    get_project_xml,
)


app_name = "main"


urlpatterns = [
    path("", show_main, name="show_main"),

    # Auth
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    # Experience
    path("experience/", show_experience, name="show_experience"),
    path("experience/create/", create_experience, name="create_experience"),
    path(
        "experience/<uuid:experience_id>/edit/",
        update_experience,
        name="update_experience",
    ),
    path(
        "experience/<uuid:experience_id>/delete/",
        delete_experience,
        name="delete_experience",
    ),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/experience/xml/", get_experience_xml, name="get_experience_xml"),

    # Project
    path("project/", show_project, name="show_project"),
    path("project/create/", create_project, name="create_project"),
    path(
        "project/<int:project_id>/edit/",
        update_project,
        name="update_project",
    ),
    path(
        "project/<int:project_id>/delete/",
        delete_project,
        name="delete_project",
    ),
    path(
        "project/<int:project_id>/star/",
        toggle_star,
        name="toggle_star",
    ),
    path("api/project/", get_project_json, name="get_project_json"),
    path("api/project/xml/", get_project_xml, name="get_project_xml"),
]