from django.db import models
from django.utils import timezone
from six import string_types
from django.contrib.auth.models import User, AbstractUser
import datetime


class Questao(models.Model):
  def __str__(self):
    return self.questao_texto

  def foi_publicada_recentemente(self):
    return self.pub_data >= timezone.now() - datetime.timedelta(days=1)

  def get_resultados(self) -> dict["Opcao", int]:
    resultados = {}
    for opcao in self.opcao_set.all():
      resultados[opcao] = opcao.get_votos()
    return resultados

  questao_texto = models.CharField(max_length=200)
  pub_data = models.DateTimeField('data de publicacao')


class Opcao(models.Model):
  def __str__(self):
    return self.opcao_texto

  questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
  opcao_texto = models.CharField(max_length=200)

  def get_votos(self):
    return self.voto_set.count()
  def add_voto(self, aluno):
    voto = Voto(opcao=self, aluno=aluno)
    voto.save()


class Aluno(AbstractUser):
  # user = models.OneToOneField(User, on_delete=models.CASCADE)
  # *email = models.EmailField(max_length=254)
  curso = models.CharField(max_length=100)
  # @staticmethod
  # def get_aluno(user):
  #   return Aluno.objects.filter(user=user).first()
  # REQUIRED_FIELDS = ['email', 'curso']


class Voto(models.Model):
  opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE)
  aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)

  @staticmethod
  def get_votos_from_aluno(aluno):
    return Voto.objects.filter(aluno=aluno).count()