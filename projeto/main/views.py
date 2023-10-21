from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.models import Topico, Thread, User


def index(request):
  return render(request, "index.html", {
      "topicos": Topico.get_topicos()
  })

def topico(request, topico_name:str):
  if topico_name in [t.name for t in Topico.objects.all()]:
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


def thread(request, topico_name:str, thread_id:int):
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
    username = request.POST['username']
    password = request.POST['password']
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

def logout_view(request):
  auth.logout(request)
  return HttpResponseRedirect("/")

def register_view(request):
  if request.method == "POST":
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
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