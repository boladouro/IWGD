from django.contrib import auth
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST

from .models import Topico, Thread, User
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def index(request):
  return render(request, "index.html", {
    "topicos": Topico.get_topicos(user=getUser(request))
  })


def topico(request, topico_name: str):
  if topico_name in [t.name for t in Topico.get_topicos(user=getUser(request))]:
    return render(request, "topico.html", {
      "topico": topico_name,
      "threads": Topico.get_topico_by_name(topico_name).get_threads()
    })
  else:
    return render(request, "404.html", status=404)


def handler404(request, exception):
  return render(request, "404.html")


def search_authors(request):
  return render(request, "search_authors.html")


def perfil(request):
  return render(request, "perfil.html")


def thread(request, topico_name: str, thread_id: int):
  t = Thread.get_thread_by_id(thread_id)
  if t.topico.name != topico_name:
    # redirect to correct url
    return HttpResponseRedirect(f"/t/{t.topico.name}/{t.id}/")
  return render(request, "thread.html", {
    "thread": t,
    "posts": t.get_posts()
  })


def login_view(request):
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
      auth.login(request, user)
    else:
      return render(request, "login.html", {
        "error": "Invalid username and/or password."
      })
  if request.user.is_authenticated:
    return HttpResponseRedirect("/")
  return render(request, "login.html")

def getUser(request):
  if request.user.is_authenticated:
    return request.user
  else:
    return None

def logout_view(request):
  auth.logout(request)
  return HttpResponseRedirect("/")


def register_view(request):
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    if User.objects.filter(username=username).exists():
      return render(request, "register.html", {
        "error": "Username already exists."
      })
    if User.objects.filter(email=email).exists():
      return render(request, "register.html", {
        "error": "Email already exists."
      })
    user = User.objects.create_user(username, email, password)
    user.save()
    auth.login(request, user)
    return HttpResponseRedirect("/")
  if request.user.is_authenticated:
    return HttpResponseRedirect("/")
  return render(request, "register.html")


@require_POST
def favorite(request, topico_str: str):
  if not request.user.is_authenticated:
    return JsonResponse({
      "error": "User is not authenticated."
    }, status=401)
  if topico_str not in [t.name for t in Topico.get_topicos(user=getUser(request))]:
    return render(request, "404.html", status=404)
  user: User = request.user
  topico_ = Topico.get_topico_by_name(topico_str)
  exists = user.favorites.filter(pk=topico_.id).exists()
  if exists:
    user.favorites.remove(topico_)
  else:
    user.favorites.add(topico_)
  user.save()
  return JsonResponse({
    "added": not exists,
  }, status=200)
