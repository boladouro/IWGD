from django.db import models
from django.db.models import Model
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
  date_created = models.DateTimeField(auto_now_add=True)
  signature = models.TextField(null=True)
  avatar = models.URLField(null=True)
  is_banned = models.BooleanField(default=False)
  is_timed_out = models.BooleanField(default=False)
  timeout_expires = models.DateTimeField(null=True)
  ban_or_timeout_reason = models.TextField(null=True)

  REQUIRED_FIELDS = ['username']


class Mod(Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
  date_turned_mod = models.DateTimeField(auto_now_add=True)

class ModPermissions(Model):
  mod = models.ForeignKey(Mod, on_delete=models.CASCADE)
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
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class Forum(Model):
  title = models.CharField(max_length=50)
  description = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True)
  latest_update = models.DateTimeField()


class Thread(Model):
  title = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True)
  latest_update = models.DateTimeField()
  follow_up_from = models.ForeignKey('Thread', on_delete=models.CASCADE, null=True, blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  is_sticky = models.BooleanField(default=False)

class Post(Model):
  date_created = models.DateTimeField(auto_now_add=True)
  thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  text = models.TextField()
class Emotes(Model): #TODO make better?
  name = models.CharField(max_length=50)
  def get_emote_path(self):
    return f"img/emotes/{self.name}.png"

class PostEmotes(Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  emote = models.ForeignKey(Emotes, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
