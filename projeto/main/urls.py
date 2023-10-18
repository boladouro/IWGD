from django.urls import include, path
from django.views.generic import RedirectView

from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index"),
    path("t/<str:topico>/", views.topico, name="topico"),
    path("a/", views.search_authors, name="search_authors"),
]

handler404 = 'main.views.handler404'