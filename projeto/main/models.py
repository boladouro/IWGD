from django.db import models
from django.db.models import Model
from django.contrib.auth.models import AbstractUser


class User(AbstractUser)
  date_created = models.DateTimeField(auto_now_add=True)
  
  REQUIRED_FIELDS = ['username']

class Mod(Model)
  # mods can add other mods and can remove mods they added
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
  date_turned_mod = models.DateTimeField(auto_now_add=True)
  mods_added = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

class Admin(Model)
  # admins can add and remove mods at their will