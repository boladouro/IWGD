from django.shortcuts import render
from django.http import HttpResponse

from main.models import Topico, Thread


def index(request):
  return render(request, "index.html", {
      "topicos": Topico.get_topicos()
  })

def topico(request, topico_name:str):
  if topico_name in [t.name for t in Topico.objects.all()]:
    return render(request, "topico.html", {
      "topico": topico_name,
      "threads": Topico.get_topico(topico_name).get_threads()
    })
  else:
    return render(request, "404.html", status=404)

def handler404(request, exception):
  return render(request, "404.html")


def search_authors(request):
  return render(request, "search_authors.html")
def perfil(request):
  return render(request, "perfil.html")
