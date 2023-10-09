from django.urls import include, path
from . import views
from django.contrib.auth.views import LogoutView
# (. significa que importa views da mesma directoria)
app_name = 'votacao'
urlpatterns = [
    path("", views.index, name="index"),
    path('questoes/', views.questoes, name='questoes'),
    path('<int:questao_id>', views.detalhe, name='detalhe'),
    path('<int:questao_id>/resultados', views.resultados, name='resultados'),
    path('<int:questao_id>/voto', views.voto, name='voto'),
    path('nova_questao/', views.nova_questao, name='nova_questao'),
    path('<int:questao_id>/criar_opcao/',views.criar_opcao,name='criar_opcao'),
    path('<int:questao_id>/eliminar_opcao/',views.eliminar_opcao,name='eliminar_opcao'),
    path('eliminar_questao/',views.eliminar_questao,name='eliminar_questao'),
    path('cadastro/', views.cadastro, name="cadastro"),
    path('login/', views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("perfil/", views.perfil, name="perfil"),

]
