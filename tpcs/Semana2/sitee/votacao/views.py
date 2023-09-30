from django.shortcuts import render,  get_object_or_404
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Questao, Opcao
from django.http import Http404

# def index(request):
#  latest_question_list = Questao.objects.order_by('-pub_data')[:5]
#  template = loader.get_template('votacao/index.html')
#  context = {'latest_question_list': latest_question_list,}
#  return HttpResponse(template.render(context, request))


def index(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/index.html', context)


def detalhe(request, questao_id):
    return HttpResponse("Esta e a questao %s." % questao_id)


def resultados(request, questao_id):
    response = "Estes sao os resultados da questao %s."
    return HttpResponse(response % questao_id)


def voto(request, questao_id):
    return HttpResponse("Votacao na questao %s." % questao_id)

# def detalhe(request, questao_id):
#      try:
#        questao = Questao.objects.get(pk=questao_id)
#      except Questao.DoesNotExist:
#        raise Http404("A questao nao existe")
#      return render(request, 'votacao/detalhe.html', {'questao': questao})


def detalhe(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': questao})


def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    try:
        opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': "Não escolheu uma opção", })
    else:
        opcao_seleccionada.votos += 1
        opcao_seleccionada.save()
        # Retorne sempre HttpResponseRedirect depois de
        # tratar os dados POST de um form
        # pois isso impede os dados de serem tratados
        # repetidamente se o utilizador
        # voltar para a página web anterior.
    return HttpResponseRedirect(reverse('votacao:resultados', args=(questao.id,)))


def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao': questao})


def nova_questao(request):
    return render(request, 'votacao/nova_questao.html')


def guardar_questao(request):
    t = request.Post['nova_questao']
    q = Questao(questao_texto=t, pub_data=timezone.now())
    q.save()
    return HttpResponseRedirect(reverse('votacao:index'))
