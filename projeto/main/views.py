from django.shortcuts import render
from django.http import HttpResponse

from main.models import Topico


def index(request):
    return render(request, "index.html", {
        "topicos": Topico.get_topicos()
    })
