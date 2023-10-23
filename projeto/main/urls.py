from django.urls import include, path
from django.views.generic import RedirectView

from . import views

app_name = 'main'

urlpatterns = [
  path("", views.index, name="index"),
  path("t/<str:topico_name>/", views.topico, name="topico"),
  path("a/", views.search_authors, name="search_authors"),
  path("perfil/", views.perfil, name="perfil"),
  path("<str:topico_name>/<int:thread_id>/", views.thread, name="thread"),
  path("404/", views.handler404, name="404"),
  path("favicon.ico", RedirectView.as_view(url='/static/img/favicon.ico')),
  path("login/", views.login_view, name="login"),
  path("logout/", views.logout_view, name="logout"),
  path("register/", views.register_view, name="register"),
  path("favorite/<str:topico_str>/", views.favorite, name="favorite"),
  path("new_thread/", views.create_thread, name="create_thread"),
  path("new_post/", views.create_post, name="create_post"),
  path("del_thread/", views.delete_thread, name="delete_thread"),
  path("del_post/", views.delete_post, name="delete_post"),
]

handler404 = 'main.views.handler404'
