from django.urls import include, path
from django.views.generic import RedirectView

from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:topico_name>/", views.topico, name="topico"),
    path("a/", views.search_authors, name="search_authors"),
    path("perfil/", views.perfil, name="perfil"),
    path("<str:topico_name>/<int:thread_id>/", views.thread, name="thread"),

    path("404/", views.handler404, name="404"),
    path("favicon.ico", RedirectView.as_view(url='/static/img/favicon.ico')),

]

handler404 = 'main.views.handler404'
