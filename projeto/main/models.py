from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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
  favorites = models.ManyToManyField('Topico', related_name="favorites")

  @staticmethod
  def get_user_by_id(user_id: int) -> "User":
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
  def get_thread_by_id(thread_id: int) -> "Thread" | None:
    return Thread.objects.get(pk=thread_id)

  def get_posts(self) -> Iterable["Post"]:
    return Post.objects.filter(thread=self).order_by('date_created')


class Post(Model):
  date_created = models.DateTimeField(auto_now_add=True)
  text = models.TextField(max_length=200)
  thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="thread")
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")


  @staticmethod
  def new_post(user: User, thread_id: Thread, text: str) -> "Post":
    post = Post(user=user, thread=thread_id, text=text)
    post.save()
    return post

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
  is_fav = 0

  @property
  def thread_count(self) -> int:
    return Thread.objects.filter(topico=self).count()

  @property
  def latest_thread(self) -> Thread | None:
    return Thread.objects.filter(topico=self).order_by('-date_created').first()

  @staticmethod
  def get_topicos(user: User | None) -> Iterable["Topico"]:
    ret: Iterable["Topico"] = Topico.objects.all()
    if user is not None:
      for i in ret:
        i.is_fav = 1 if i in user.favorites.all() else 0
      # order ret by if it's a favorite
      ret = sorted(ret, key=lambda x: x.is_fav == 1, reverse=True)
    return ret

  @staticmethod
  def get_topico_by_name(topico_name: str) -> "Topico":
    return Topico.objects.get(name=topico_name)

  @staticmethod
  def get_topico_by_id(topico_id: int) -> "Topico":
    return Topico.objects.get(pk=topico_id)

  def get_threads(self) -> Iterable[Thread]:
    # sort by if it's sticky, then date_created from earliest to latest
    return Thread.objects.filter(topico=self).order_by('-is_sticky', '-date_created')
