from django.urls import include, path
from . import views
# (. significa que importa views da mesma directoria)
urlpatterns = [
 path("", views.index, name="index"),
 path("./htmls/index.html", views.home, name="home"),
]