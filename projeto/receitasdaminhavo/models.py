from django.db import models
from django.db.models import Model
class Receita(Model):
  introducao = models.TextField()
  conclusao = models.TextField()
  preview = models.URLField()
class Passo(Model):
  pass

class Utilizador(Model):
  pass

class Review(Model):
  pass

class Moderator(Model):
  pass