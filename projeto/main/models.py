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
  def create_user(username: str, password: str, email: str = None) -> User:
    return User.objects.create_user(username, email, password)

  @property
  def is_mod(self) -> bool:
    return Mod.is_mod(self)

  @property
  def is_admin(self) -> bool:
    return Admin.is_admin(self)

  def __str__(self):
    return self.username

  @staticmethod
  def get_user_by_id(user_id: int) -> "User":
    return User.objects.get(pk=user_id)


class Mod(Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="mod")
  date_turned_mod = models.DateTimeField(auto_now_add=True)

  @staticmethod
  def is_mod(user: User) -> bool:
    return Mod.objects.filter(user=user).exists() or Admin.is_admin(user)

  @staticmethod
  def create_mod(user: User):
    user.save()
    mod = Mod(user=user)
    mod.save()
    return mod


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

  @staticmethod
  def create_admin(user: User) -> Admin:
    user.save()
    admin = Admin(user=user)
    admin.save()
    return admin

  @staticmethod
  def is_admin(user: User) -> bool:
    return Admin.objects.filter(user=user).exists()

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
  # SET NULL HERE CAUSE THREADS BEING DELETED IS NOT GOOD
  user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="poster")
  is_sticky = models.BooleanField(default=False)
  topico = models.ForeignKey('Topico', on_delete=models.CASCADE, null=True, related_name="topico")

  def __str__(self):
    return self.title

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
  text = models.TextField()
  thread = models.ForeignKey(Thread, on_delete=models.DO_NOTHING, related_name="thread")
  user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="user")  # SAME THING HERE

  def __str__(self):
    return self.text

  @staticmethod
  def new_post(user: User, thread_id: Thread, text: str) -> "Post":
    post = Post(user=user, thread=thread_id, text=text)
    post.save()
    return post

  def is_post_from_op(self) -> bool:
    return self.user == self.thread.user

  def get_emotes(self) -> Iterable["Emotes"]:
    return Emotes.objects.filter(postemotes__post=self)

  def is_first_post(self) -> bool:
    return self.thread.get_posts().first() == self

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

  def __str__(self):
    return self.name

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


class Reports(Model):
  post_reported = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_report")
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_report")
  reason = models.TextField()
  mod_reason = models.TextField(null=True)
  date_created = models.DateTimeField(auto_now_add=True)
  accepted_report = models.BooleanField(default=False)
  accepted_by = models.ForeignKey(Mod, on_delete=models.DO_NOTHING, null=True, related_name="accepted_by", default=None)
  action = models.TextField()

  @staticmethod
  def get_reports() -> Iterable["Reports"]:
    return Reports.objects.all().filter(accepted_report=False)
