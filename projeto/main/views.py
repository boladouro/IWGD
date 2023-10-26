from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Topico, Thread, User, Post, Mod, Reports
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


def thread(request, thread_id: int, topico_name: str = None):
  if request.user.is_authenticated: #TODO move this cause thread id wont be known ahead of time
    if request.method == "POST":
      text_p = request.POST.get('textt')
      user_p = request.user
      thread_p = Thread.get_thread_by_id(thread_id)
      if text_p is not None:
        kkk = Post.new_post(user=user_p, text=text_p, thread_id=thread_p)
        return HttpResponseRedirect(f"{request.path}")
  t = Thread.get_thread_by_id(thread_id)
  if t is None:
    return render(request, "404.html", status=404)
  if t.topico.name != topico_name:  # type: ignore
    # redirect to correct url
    return HttpResponseRedirect(f"/t/{t.topico.name}/{t.id}/")  # type: ignore
  return render(request, "thread.html", {
    "topico_name": topico_name,
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
        "error": "Invalid username and/or password.",
        "username_inserted": username,
      })
  if request.user.is_authenticated:
    return HttpResponseRedirect("/")
  return render(request, "login.html")


def getUser(request) -> User | None:
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
        "error": "Username already exists.",
        "username_inserted": username,
        "email_inserted": email,
      })
    if User.objects.filter(email=email).exists():
      return render(request, "register.html", {
        "error": "Email already exists.",
        "username_inserted": username,
        "email_inserted": email,
      })
    user = User.create_user(username=username, password=password, email=email)
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


@login_required(login_url="login/")
def create_thread(request, topico_name):
  if request.method == 'POST':
    user_t = request.user
    topico_t = Topico.get_topico_by_name(topico_name)
    titulo_t = request.POST.get('title')

    if topico_t is not None and titulo_t is not None:
      kkk = Thread.new_thread(title=titulo_t, user=user_t, topico=topico_t)
      return topico(request, topico_name)
  return render(request, 'new_thread.html', {'topico_name': topico_name})


@login_required(login_url="login/")
def create_post(request):
  #   if request.method == 'POST':
  #     user_p = request.user
  #     topico_p = Topico.get_topico_by_name(topico_name)
  #     text_p = request.POST.get('text')
  #
  #     if topico_t is not None and titulo_t is not None:
  #       kkk = Thread.new_thread(title=titulo_t, user=user_t, topico=topico_t)
  #       return topico(request,topico_name)
  #   return render(request, 'new_post.html', {'topico_name': topico_name})
  pass


@login_required(login_url="login/")
def delete_post(request):
  raise NotImplementedError("TODO")


@login_required(login_url="login/")
def delete_thread(request):
  return render(request, 'del_thread.html')


@login_required(login_url="login/")
def admin(request):
  if Mod.is_mod(getUser(request)):
    r = Reports.get_reports()
    return render(request, "admin.html", {
      "n_reports": len(r),
      "reports": r,
    })
  else:
    return render(request, "401.html", status=401)


@login_required(login_url="login/")
@require_POST
def report(request):
  post_id = request.POST["post_id"]
  thread_id = request.POST["thread_id"]
  report_description = request.POST["report_description"]
  try:
    created = Reports.create_or_alter_report(Post.get_post_by_id(post_id), getUser(request), report_description)
  except Exception as e:
    return JsonResponse({
      "error": str(e),
      "error_object": e,
    }, status=500)
  if created:
    return JsonResponse({
      "success": True,
      "message": "Report created successfully."
    }, status=200)
  else:
    return JsonResponse({
      "success": True,
      "message": "Report altered successfully."
    }, status=200)