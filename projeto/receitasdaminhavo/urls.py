from django.template.defaulttags import url
from django.urls import path
from django.views.generic import RedirectView

from . import views
urlpatterns = [
  path("home/", views.index, name="default"),
  path("", RedirectView.as_view(url='home/'), name="redirectToDefault")
]