from dataclasses import dataclass

from django.db import models
from django.db.models import Model
from django.contrib.auth.models import AbstractUser

DATABASE_READY = False


class User(AbstractUser):
  date_created = models.DateTimeField(auto_now_add=True)
  signature = models.TextField(null=True, default=None)
  avatar = models.ImageField(default='default.png', upload_to='avatars')
  is_banned = models.BooleanField(default=False)
  is_timed_out = models.BooleanField(default=False)
  timeout_expires = models.DateTimeField(null=True)
  ban_or_timeout_reason = models.TextField(null=True)

  def get_user_by_id(user_id: int):
    return User.objects.get(pk=user_id)



class Mod(Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="mod")
  date_turned_mod = models.DateTimeField(auto_now_add=True)


class ModPermissions(Model):
  mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name="permissions")
  permission = models.CharField(max_length=50, choices=[
    ('ban', "Ban users"),
    ('timeout', "Timeout users"),
    ('delete', "Delete posts & threads"),
    ('hide', "Hide posts & threads"),
    ('unhide', "Unhide posts & threads"),
    ('edit', "Edit posts & threads"),
    ('sticky', "Sticky threads"),
    ('lock', "Lock threads"),
    ('unlock', "Unlock threads"),
    ('move', "Move threads to other forums"),
    ('create', "Create new forums"),
  ])


class Admin(Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="admin")


class Forum(Model):
  title = models.CharField(max_length=50)
  description = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True)
  latest_update = models.DateTimeField()


class Thread(Model):
  title = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True)
  latest_update = models.DateTimeField(auto_now_add=True)
  follow_up_from = models.ForeignKey('Thread', on_delete=models.CASCADE, null=True, related_name="follow_ups")
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")
  is_sticky = models.BooleanField(default=False)
  topico = models.ForeignKey('Topico', on_delete=models.CASCADE, null=True, related_name="topico")
  @staticmethod
  def new_thread(title: str, user: User, topico: "Topico", is_sticky: bool = False) -> "Thread":
    thread = Thread(title=title, user=user, topico=topico, is_sticky=is_sticky)
    thread.save()
    return thread

  @staticmethod
  def get_thread_by_id(thread_id: int) -> "Thread":
    return Thread.objects.get(pk=thread_id)

  def get_posts(self) -> list["Post"]:
    return Post.objects.filter(thread=self).order_by('date_created')


class Post(Model):
  date_created = models.DateTimeField(auto_now_add=True)
  thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="thread")
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
  text = models.TextField()

class Emotes(Model):  # TODO make better?
  name = models.CharField(max_length=50)

  def get_emote_path(self):
    return f"img/emotes/{self.name}.png"


class PostEmotes(Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
  emote = models.ForeignKey(Emotes, on_delete=models.CASCADE, related_name="emote")
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emote_user")


class Topico(Model):
  name = models.CharField(max_length=50)

  @dataclass
  class TopicoData:
    nome: str
    thread_count: int
    latest_thread: Thread | None = None

  @staticmethod
  def get_topicos() -> list[TopicoData]: #TODO rewrite
    topicos = []
    for topico in Topico.objects.all():
      topicos.append(Topico.TopicoData(topico.name, Thread.objects.filter(topico=topico).count()))
      topicos[-1].latest_thread = Thread.objects.filter(topico=topico).order_by('-date_created').first()
    return topicos

  @staticmethod
  def get_topico_by_name(topico_name: str) -> "Topico":
    return Topico.objects.get(name=topico_name)

  @staticmethod
  def get_topico_by_id(topico_id: int) -> "Topico":
    return Topico.objects.get(pk=topico_id)

  def get_threads(self) -> list[Thread]:
    # sort by if it's sticky, then date_created from earliest to latest
    return Thread.objects.filter(topico=self).order_by('-is_sticky', '-date_created')
