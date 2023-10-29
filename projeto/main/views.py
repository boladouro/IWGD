from django.contrib import auth
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from .models import Topico, Thread, User, Post, Mod, Reports, PostEmotes
from django.contrib.auth.decorators import login_required


def login_required_json(function):
  def wrapper(request, *args, **kwargs):
    if not request.user.is_authenticated:
      return JsonResponse({
        "error": "User is not authenticated."
      }, status=401)
    return function(request, *args, **kwargs)

  return wrapper


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

@login_required(login_url="/login/")
def perfil(request):
  if request.user.is_authenticated:
    if request.method == "POST":
      imaeee = request.FILES.get("image_perfil")
      username = request.POST.get("username")
      bio = request.POST.get("bio")
      senha1 = request.POST.get("password1")
      senha2 = request.POST.get("password2")
      signatu = request.POST.get("signatu")
      if imaeee is not None and imaeee != "":
        useer = request.user
        useer.avatar = imaeee
        useer.save()
      if username is not None and username != "" and username != request.user:
        useer = request.user
        useer.username = username
        useer.save()
      if bio is not None and bio != "":
        useer = request.user
        useer.bio = bio
        useer.save()
      if senha1 is not None and senha1 != "" and senha2 is not None and senha2 != "" and senha2 == senha1:
        useer = request.user
        useer.set_password(f"{senha1}")
        useer.save()
        return redirect('/')
      if signatu is not None and signatu != "":
        useer = request.user
        useer.signature = signatu
        useer.save()
  return render(request, "perfil.html", {
    "threads": Topico.get_threads_user(user=getUser(request)),
    "posts": Thread.get_posts_user(user=getUser(request)),
    "image": ("" if request.user.avatar == "" else request.user.get_avatar_url),
    "bios": (request.user.bio if request.user.bio != "Null" else "Clique no lapis para escrever uma bio"),
    "n_p": len(Thread.get_posts_user(user=getUser(request))),
    "n_tre": len(Topico.get_threads_user(user=getUser(request))),
    "n_top": len(Thread.get_posts_user(user=getUser(request))),
    "signature": (request.user.get_signature() if request.user.get_signature() != None else "Clique no lapis para Colocar uma assinatura"),
    "topico_principal": Topico.get_topico_principal(user=getUser(request))
  })


def thread(request, thread_id: int, topico_name: str = None):
  if request.user.is_authenticated:  # TODO move this cause thread id wont be known ahead of time
    if request.method == "POST":
      text_p = request.POST.get('textt')
      user_p = request.user
      thread_p = Thread.get_thread_by_id(thread_id)
      if not thread_p.is_locked and text_p is not None and text_p != "":
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
    "posts": t.get_posts(request.user),
    "emotes": PostEmotes.get_emotes_possible(),
    "emotes_user": PostEmotes.get_emotes_in_thread(t, request.user),
    "user_is_mod": User.is_mod_or_admin(request.user)
  })


def login_view(request):
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
      is_timed_out, timedout_until = user.is_timed_out
      if is_timed_out:
        return render(request, "login.html", {
          "error": f"User is timed out until {user.timedout_until.strftime('%d/%m/%Y %H:%M:%S')}. Reason: {user.ban_or_timeout_reason}",
          "username_inserted": username,
        })
      if user.is_banned:
        return render(request, "login.html", {
          "error": f"User is banned. Reason: {user.ban_or_timeout_reason}",
          "username_inserted": username,
        })
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
        "error": "Username ja está sendo usando.",
        "username_inserted": username,
        "email_inserted": email,
      })
    if User.objects.filter(email=email).exists():
      return render(request, "register.html", {
        "error": "Email ja está sendo usando.",
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
      "error": "Usuario não logando."
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


@login_required_json
def create_thread(request, topico_name):
  if request.method == 'POST':
    user_t = request.user
    topico_t = Topico.get_topico_by_name(topico_name)
    titulo_t = request.POST.get('title')
    text_t = request.POST.get('texxt')

    if topico_t is not None and titulo_t is not None:
      kkk1 = Thread.new_thread(title=titulo_t, user=user_t, topico=topico_t)
      thread_p = Thread.get_thread_by_id(kkk1.id)
      if text_t is not None:
        kkk = Post.new_post(user=user_t, text=text_t, thread_id=thread_p)
        return HttpResponseRedirect(f"/t/{topico_name}/{kkk1.id}")
  return render(request, 'new_thread.html', {'topico_name': topico_name})


@login_required_json
@require_POST
def delete_post(request):
  post_id = request.POST["post_id"]
  post = Post.get_post_by_id(post_id)
  if post.user == request.user or request.user.is_mod or request.user.is_admin:
    Post.delete_post(Post.get_post_by_id(post_id))
    return JsonResponse({
      "success": True,
      "message": "Apagado com sucesso."
    }, status=200)
  return JsonResponse({
    "error": "No auth"
  } ,status=401)


@login_required_json
def delete_thread(request):
  return render(request, 'del_thread.html')


@login_required_json
def admin(request):
  if Mod.is_mod(getUser(request)):
    r = Reports.get_reports()
    return render(request, "admin.html", {
      "n_reports": len(r),
      "reports": r,
    })
  else:
    return render(request, "401.html", status=401)


@login_required_json
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
      "message": "Report criado com sucesso."
    }, status=200)
  else:
    return JsonResponse({
      "success": True,
      "message": "Report alterado com sucesso."
    }, status=200)


@login_required_json
@require_POST
def emote(request):
  post = Post.get_post_by_id(int(request.POST["post_id"]))
  emote = request.POST["emote"]
  removing = bool(int(request.POST["removing"]))  # idiotic but it works

  if emote not in PostEmotes.get_emotes_possible():
    return JsonResponse({
      "error": "Emote indisponivel."
    }, status=400)
  if post is None:
    return JsonResponse({
      "error": "Post não encontrado."
    }, status=404)
  try:
    added = PostEmotes.toggle_emote(post, getUser(request), emote, adding_or_removing="remove" if removing else "add")
  except Exception as e:
    return JsonResponse({
      "error": str(e),
      "error_object": e,
    }, status=500)
  return JsonResponse({
    "success": True,
    "message": "Emote adicionado com sucesso." if added else "Emote removido com sucesso."
  }, status=200)


def searchs(request):
  return render(request, "search.html")


@login_required_json
def handle_report(request, ignore: int | bool):
  report = Reports.get_report_by_id(request.POST["report_id"])
  if ignore:
    report.ignore()
    return JsonResponse({
      "success": True,
      "message": "Report ignorado com sucesso."
    }, status=200)
  action = request.POST["action"]
  reason = request.POST["reason"]
  try:
    match action:
      case "delete":
        Post.delete_post(report.post_reported)
        message = "Apagado com sucesso."
      case "ban":
        report.post_reported.user.ban(auth=request.user, reason=reason)
        message = "Usuario banido com sucesso."
      case "delete_ban":
        Post.delete_post(report.post_reported)
        report.post_reported.user.ban(auth=request.user, reason=reason)
        message = "Apagado é usuario banido com sucesso."
      case "timeout":
        report.post_reported.user.timeout(auth=request.user, reason=reason)
        message = "User timed out successfully."
      case "delete_timeout":
        Post.delete_post(report.post_reported)
        report.post_reported.user.timeout(auth=request.user, reason=reason)
        message = "Deleted and user timed out successfully."
      case "lock":
        report.post_reported.thread.lock()
        message = "Thread locked successfully."
      case _:
        return JsonResponse({
          "error": "Invalid action."
        }, status=400)

    report.delete()
    return JsonResponse({
      "success": True,
      "message": message
    }, status=200)
  except Exception as e:
    return JsonResponse({
      "error": str(e),
      "error_object": e,
    }, status=500)


def is_banned(request):
  if request.user.is_authenticated:
    if request.user.is_banned or request.user.is_timed_out[0]:
      return JsonResponse({
        "banned": True,
        "reason": request.user.ban_or_timeout_reason,
        "until": request.user.timedout_until.strftime("%d/%m/%Y %H:%M:%S") if request.user.is_timed_out[0] else None,
      }, status=200)
  return JsonResponse({
    "banned": False,
  }, status=200)


@login_required_json
@require_POST
def sticky(request):
  thread = Thread.get_thread_by_id(request.POST["thread_id"])
  removing = bool(int(request.POST["removing"]))  # idiotic but it works
  if thread is None:
    return JsonResponse({
      "error": "Thread não encontrado."
    }, status=404)
  if not Mod.is_mod(getUser(request)):
    return JsonResponse({
      "error": "Usuario não tem permissão de administrador."
    }, status=401)
  if removing:
    thread.unsticky()
    return JsonResponse({
      "success": True,
      "message": "Thread unstickied successfully."
    }, status=200)
  else:
    thread.sticky()
    return JsonResponse({
    "success": True,
    "message": "Thread stickied successfully."
  }, status=200)


@login_required_json
@require_POST
def lock(request):
  thread = Thread.get_thread_by_id(request.POST["thread_id"])
  removing = bool(int(request.POST["removing"]))  # idiotic but it works
  if thread is None:
    return JsonResponse({
      "error": "Thread not found."
    }, status=404)
  if not Mod.is_mod(getUser(request)):
    return JsonResponse({
      "error": "User is not a mod."
    }, status=401)
  if removing:
    thread.unlock()
    return JsonResponse({
      "success": True,
      "message": "Thread unlocked successfully."
    }, status=200)
  else:
    thread.lock()
    return JsonResponse({
      "success": True,
      "message": "Thread locked successfully."
    }, status=200)

@login_required_json
@require_POST
def ban(request):
  user = User.get_user_by_id(request.POST["user_id"])
  if user is None:
    return JsonResponse({
      "error": "User not found."
    }, status=404)
  if not Mod.is_mod(getUser(request)):
    return JsonResponse({
      "error": "User is not a mod."
    }, status=401)
  wasBanned = user.ban(request.user, request.POST["reason"])
  if wasBanned:
    return JsonResponse({
      "success": True,
      "message": "User banned successfully."
    }, status=200)
  else:
    return JsonResponse({
      "sucess": True,
      "message": "User already banned."
    }, status=200)

@login_required_json
@require_POST
def timeout(request):
  user = User.get_user_by_id(request.POST["user_id"])
  if user is None:
    return JsonResponse({
      "error": "User not found."
    }, status=404)
  if not Mod.is_mod(getUser(request)):
    return JsonResponse({
      "error": "User is not a mod."
    }, status=401)
  wasTimedOut = user.timeout(request.user, request.POST["reason"])
  if wasTimedOut:
    return JsonResponse({
      "success": True,
      "message": "User timed out successfully."
    }, status=200)
  else:
    return JsonResponse({
      "sucess": True,
      "message": "User already timed out or banned."
    }, status=200)

@login_required_json
def charge_img_avatar(request):
  if request.user.is_authenticated:
    imaeee = request.FILES.get("image_perfil")
    if imaeee is not None or imaeee != "":
      useer = request.user
      useer.avatar = imaeee
      useer.save()
    return JsonResponse({
      "success": True,
      "message": "Deleted successfully."
    }, status=200)
  return JsonResponse({
    "error": "No auth"
  }, status=401)


def getAuthor(author_name) -> User | None:
    autor = User.get_user_by_id(author_name)
    return autor



def author(request,author_id):
  autoor = User.get_user_by_id(author_id)
  if(request.user == autoor):
    return HttpResponseRedirect("/perfil/")
  return render(request, "author.html",{
    "threads": Topico.get_threads_user(user=autoor),
    "posts": Thread.get_posts_user(user=autoor),
    "image": ("" if autoor.avatar == "" else autoor.get_avatar_url),
    "bios": autoor.bio,
    "n_p": len(Thread.get_posts_user(user=autoor)),
    "n_tre": len(Topico.get_threads_user(user=autoor)),
    "n_top": len(Thread.get_posts_user(user=autoor)),
    "name": autoor.username,
    "signature": autoor.signature,
    "author_id": author_id,
    "topico_principal": Topico.get_topico_principal(user=getUser(request))

  })

