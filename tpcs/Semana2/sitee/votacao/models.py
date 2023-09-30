from django.db import models
from django.utils import timezone
from six import string_types
import datetime


class Questao(models.Model):
    def __str__(self):
        return self.questao_texto

    def foi_publicada_recentemente(self):
        return self.pub_data >= timezone.now() - datetime.timedelta(days=1)
    questao_texto = models.CharField(max_length=200)
    pub_data = models.DateTimeField('data de publicacao')


class Opcao(models.Model):
    def __str__(self):
        return self.opcao_texto
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    opcao_texto = models.CharField(max_length=200)
    votos = models.IntegerField(default=0)
