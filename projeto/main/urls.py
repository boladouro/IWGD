from django.urls import include, path
from django.views.generic import RedirectView

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
  path("", views.index, name="index"),
  path("t/<str:topico_name>/", views.topico, name="topico"),
  path("a/", views.search_authors, name="search_authors"),
  path("perfil/", views.perfil, name="perfil"),
  path("t/<str:topico_name>/<int:thread_id>/", views.thread, name="thread"),
  path("404/", views.handler404, name="404"),
  path("favicon.ico", RedirectView.as_view(url='/static/img/favicon.ico')),
  path("login/", views.login_view, name="login"),
  path("logout/", views.logout_view, name="logout"),
  path("register/", views.register_view, name="register"),
  path("favorite/<str:topico_str>/", views.favorite, name="favorite"),
  path("new_thread/<str:topico_name>", views.create_thread, name="create_thread"),
  path("del_thread/", views.delete_thread, name="delete_thread"),
  path("del_post/", views.delete_post, name="delete_post"),
  path('search/', include('haystack.urls')),
  path("admin/", views.admin, name="admin"),
  path("report/", views.report, name="report"),
  path("emote/", views.emote, name="emote"),
  path("handle_report/<int:ignore>/", views.handle_report, name="handle_report"),
  path("is_banned/", views.is_banned, name="is_banned"),
  path("sticky/", views.sticky, name="sticky"),
  path("lock/", views.lock, name="lock"),
  path("ban/", views.ban, name="ban"),
  path("timeout/", views.timeout, name="timeout"),
  path("author/<int:author_id>", views.author, name="author"),
]

handler404 = 'main.views.handler404'
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)