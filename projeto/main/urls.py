from django.urls import include, path
from . import views

app_name = 'main'

urlpatterns = [
  path("", views.index, name="index"),
]