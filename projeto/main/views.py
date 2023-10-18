from django.shortcuts import render
from django.http import HttpResponse

from main.models import Topico


def index(request):
  return render(request, "index.html", {
      "topicos": Topico.get_topicos()
  })

def topico(request, topico):
  valid_topics = [
    "music",
    "movies",
    "games",
    "books",
    "theater",
    "dance",
    "sculpture",
    "painting",
    "photography",
    "meta"
  ]
  if topico in valid_topics:
    return render(request, "topico.html", {
      "topico": topico
    })
  else:
    return render(request, "404.html", status=404)

def handler404(request, exception):
  return render(request, "404.html")


def search_authors(request):
  return render(request, "search_authors.html")
def perfil(request):
  return render(request, "perfil.html")
