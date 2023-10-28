from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Mapping, Literal

import emoji
from django.db import models
from django.db.models import Model
from django.contrib.auth.models import AbstractUser
from emoji import emojize, demojize
# from django.utils.translation import gettext_lazy as _
DATABASE_READY = False


class User(AbstractUser):
  date_created = models.DateTimeField(auto_now_add=True)
  signature = models.TextField(null=True, default=None)
  avatar = models.ImageField(default='default.png', upload_to='avatars')
  is_banned = models.BooleanField(default=False)
  timeout_expires = models.DateTimeField(null=True)
  ban_or_timeout_reason = models.TextField(null=True)
  favorites = models.ManyToManyField('Topico', related_name="favorites")

  def get_avatar_url(self) -> str:
    # or self.avatar.url
    return self.avatar.path

  @staticmethod
  def create_user(username: str, password: str, email: str | None = None) -> User:
    return User.objects.create_user(username, email, password)

  @property
  def is_mod(self) -> bool:
    return Mod.is_mod(self)

  @property
  def is_admin(self) -> bool:
    return Admin.is_admin(self)

  @staticmethod
  def is_mod_or_admin(user) -> bool:
    return user.is_authenticated and (user.is_mod or user.is_admin)

  def __str__(self):
    return self.username

  @staticmethod
  def get_user_by_id(user_id: int|str) -> "User":
    return User.objects.get(pk=user_id)

  def ban(self, auth: User, reason: str) -> bool:
    # returns true if banned, false if it was already banned
    if not auth.is_mod or not auth.is_admin:
      raise PermissionError("User has no permission to ban")
    if self.is_banned:
      return False
    self.is_banned = True
    self.ban_or_timeout_reason = reason
    self.save()
    return True

  def timeout(self, auth: User, reason: str, timeout: timedelta = timedelta(days=1)):
    # returns true if timedout, false if it was timedout or banned
    if not auth.is_mod or not auth.is_admin:
      raise PermissionError("User has no permission to timeout")
    if self.is_banned or self.is_timed_out:
      return False
    self.timeout_expires = datetime.now() + timeout
    self.ban_or_timeout_reason = reason
    self.save()
    return True



  @property
  def is_timed_out(self) -> tuple[bool, datetime]:
    if self.timeout_expires is None:
      return False, datetime.now()
    return self.timeout_expires > datetime.now(), self.timeout_expires

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
  is_removed = models.BooleanField(default=False)
  is_locked = models.BooleanField(default=False)

  def __str__(self):
    return self.title

  @staticmethod
  def new_thread(title: str, user: User, topico: "Topico", is_sticky: bool = False) -> "Thread":
    thread = Thread(title=title, user=user, topico=topico, is_sticky=is_sticky)
    thread.save()
    return thread

  @staticmethod
  def get_thread_by_id(thread_id: int|str) -> "Thread" | None:
    return Thread.objects.get(pk=thread_id, is_removed=False)

  def get_posts(self, user: User | None) -> Iterable["Post"]:
    if user is not None and user.is_authenticated and (user.is_mod or user.is_admin):
      return Post.objects.filter(thread=self).order_by('date_created')
    return Post.objects.filter(thread=self, is_removed=False).order_by('date_created')

  def delete_thread(self):
    self.is_removed = True
    self.save()

  def lock(self):
    self.is_locked = True
    self.save()

  def sticky(self):
    self.is_sticky = True
    self.save()

  def unsticky(self):
    self.is_sticky = False
    self.save()

  def unlock(self):
    self.is_locked = False
    self.save()


class Post(Model):
  date_created = models.DateTimeField(auto_now_add=True)
  text = models.TextField()
  thread = models.ForeignKey(Thread, on_delete=models.DO_NOTHING, related_name="thread")
  user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="user")  # SAME THING HERE
  is_removed = models.BooleanField(default=False)

  def __str__(self):
    return self.text

  @staticmethod
  def new_post(user: User, thread_id: Thread, text: str) -> "Post":
    post = Post(user=user, thread=thread_id, text=text)
    post.save()
    return post

  def is_post_from_op(self) -> bool:
    return self.user == self.thread.user

  @dataclass
  class GetEmotesResult:
    count: int
    is_emoted_by_user: bool

  def get_emotes(self, user) -> Mapping[str, GetEmotesResult]:
    # emote: {post_id: is_emoted_by_user}
    return {i: result for i in PostEmotes.Emotes.get_emotes_possible() if (result := Post.GetEmotesResult(
      count=PostEmotes.objects.filter(post=self, emote=i).count(),
      is_emoted_by_user=PostEmotes.objects.filter(post=self, emote=i, user=user).exists(),
    )).count > 0}

  def emotes(self) -> Mapping[str, int]:
    return {
      i: PostEmotes.objects.filter(post=self, emote=emoji.demojize(i)).count()
      for i in PostEmotes.get_emotes_possible()
    }

  def is_first_post(self) -> bool:
    return self.thread.get_posts(None).first() == self

  @staticmethod
  def get_post_by_id(post_id: int) -> "Post":
    return Post.objects.get(pk=post_id, is_removed=False)

  @staticmethod
  def delete_post(post: Post) -> "Post":
    post.is_removed = True
    post.save()
    return post


class PostEmotes(Model):
  class Emotes(models.TextChoices):
    LIKE = emoji.demojize("👍")
    DISLIKE = emoji.demojize("👎")
    LOVE = emoji.demojize("❤️")
    WARNING = emoji.demojize("⚠️")
    PARTY = emoji.demojize("🎉")
    EYES = emoji.demojize("👀")
    SAD = emoji.demojize("😕")
    ROLLING_EYES = emoji.demojize("🙄")

    @staticmethod
    def get_emotes_possible() -> Iterable[str]:
      # this method is for backend (it's not emojis)
      # Maybe better names would help but whtv
      return PostEmotes.Emotes.values

  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emote_user")
  emote = models.CharField(
    choices=Emotes.choices,
    max_length=24,
  )

  @staticmethod
  def toggle_emote(post: Post, user: User, emote: str,
                   adding_or_removing: Literal["add", "remove", None] = None) -> bool:
    # returns true if added, false if removed
    emote = demojize(emote)
    if emote not in PostEmotes.Emotes.get_emotes_possible():
      raise ValueError("Invalid emote")
    if adding_or_removing is None:
      if PostEmotes.objects.filter(post=post, user=user, emote=emote).exists():
        adding_or_removing = "remove"
      else:
        adding_or_removing = "add"
    if adding_or_removing == "remove":
      PostEmotes.objects.filter(post=post, user=user, emote=emote).delete()
      return False
    elif adding_or_removing == "add":
      PostEmotes(post=post, user=user, emote=emote).save()
      return True
    else:
      raise ValueError("Invalid adding_or_removing")

  @staticmethod
  def get_emotes_possible() -> Iterable[str]:
    # this method is for frontend (it's emojis)
    return [emoji.emojize(i[0]) for i in PostEmotes.Emotes.choices]

  @staticmethod
  def get_emotes_from_user(post: Post, user: User) -> Iterable[str]:
    return [emoji.emojize(i.emote) for i in PostEmotes.objects.filter(post=post, user=user)]

  @staticmethod
  def get_emotes_in_thread(thread: Thread, user: User) -> Mapping[int, Iterable[str]]:
    if not user.is_authenticated: return {}
    return {
      i.post.id: PostEmotes.get_emotes_from_user(i.post, user)
      for i in PostEmotes.objects.filter(post__thread=thread, user=user)
    }


class Topico(Model):
  name = models.CharField(max_length=50)
  is_fav = 0

  def __str__(self):
    return self.name

  @property
  def thread_count(self) -> int:
    return Thread.objects.filter(topico=self, is_removed=False).count()

  @property
  def latest_thread(self) -> Thread | None:
    return Thread.objects.filter(topico=self, is_removed=False).order_by('-date_created').first()

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
    return Thread.objects.filter(topico=self, is_removed=False).order_by('-is_sticky', '-date_created')


class Reports(Model):
  post_reported = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_report")
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_report")
  reason = models.TextField()
  mod_reason = models.TextField(null=True, default=None)
  date_created = models.DateTimeField(auto_now_add=True)
  accepted_report = models.BooleanField(default=False)
  accepted_by = models.ForeignKey(Mod, on_delete=models.DO_NOTHING, null=True, related_name="accepted_by", default=None)
  action = models.TextField(null=True, default=None)

  @staticmethod
  def get_reports() -> Iterable["Reports"]:
    return Reports.objects.all().filter(accepted_report=False)

  @staticmethod
  def create_report(post: Post, user: User, reason: str) -> Reports:
    report = Reports(post_reported=post, created_by=user, reason=reason)
    report.save()
    return report

  @staticmethod
  def does_report_exist(post: Post, user: User) -> bool:
    return Reports.objects.filter(post_reported=post, created_by=user).exists()

  @staticmethod
  def create_or_alter_report(post: Post, user: User, reason: str) -> bool:
    # returns true if created, false if substituted
    report = Reports.objects.filter(post_reported=post, created_by=user).first()
    if report is None:
      Reports.create_report(post, user, reason)
      return True
    report.reason = reason
    report.save()
    return False

  @staticmethod
  def get_report_by_id(report_id: int) -> Reports:
    return Reports.objects.get(pk=report_id)

  def ignore(self):
    self.delete()