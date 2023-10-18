from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  return render(request, "index.html")

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