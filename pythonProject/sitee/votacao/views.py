from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template import loader
from .models import Questao
from django.http import Http404

# def index(request):
#  latest_question_list = Questao.objects.order_by('-pub_data')[:5]
#  template = loader.get_template('votacao/index.html')
#  context = {'latest_question_list': latest_question_list,}
#  return HttpResponse(template.render(context, request))
def index(request):
 latest_question_list = Questao.objects.order_by('-pub_data')[:5]
 context = {'latest_question_list':latest_question_list}
 return render(request, 'votacao/index.html',context)


def detalhe(request, questao_id):
 return HttpResponse("Esta e a questao %s." %questao_id)
def resultados(request, questao_id):
  response = "Estes sao os resultados da questao %s."
  return HttpResponse(response % questao_id)
def voto(request, questao_id):
  return HttpResponse("Votacao na questao %s." %questao_id)

def detalhe(request, questao_id):
 try:
   questao = Questao.objects.get(pk=questao_id)
 except Questao.DoesNotExist:
   raise Http404("A questao nao existe")
 return render(request, 'votacao/detalhe.html', {'questao': questao})
