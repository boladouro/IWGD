from django.shortcuts import render,  get_object_or_404
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Questao, Opcao, Aluno
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_kar
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as bye
from django.shortcuts import redirect
# def index(request):
#  latest_question_list = Questao.objects.order_by('-pub_data')[:5]
#  template = loader.get_template('votacao/index.html')
#  context = {'latest_question_list': latest_question_list,}
#  return HttpResponse(template.render(context, request))


def index(request):
    return render(request, 'votacao/index.html')

@login_required(login_url="/votacao/login/")
def detalhe(request, questao_id):
    return HttpResponse("Esta e a questao %s." % questao_id)

@login_required(login_url="/votacao/login/")
def resultados(request, questao_id):
    response = "Estes sao os resultados da questao %s."
    return HttpResponse(response % questao_id)

@login_required(login_url="/votacao/login/")
def voto(request, questao_id):
    return HttpResponse("Votacao na questao %s." % questao_id)

# def detalhe(request, questao_id):
#      try:
#        questao = Questao.objects.get(pk=questao_id)
#      except Questao.DoesNotExist:
#        raise Http404("A questao nao existe")
#      return render(request, 'votacao/detalhe.html', {'questao': questao})

@login_required(login_url="/votacao/login/")
def detalhe(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': questao})

@login_required(login_url="/votacao/login/")
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

@login_required(login_url="/votacao/login/")
def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao': questao})

@login_required(login_url="/votacao/login/")
def nova_questao(request):
    if request.method == 'POST':
        t = request.POST['nova_questao']
        nova_questao = Questao(questao_texto=t, pub_data=timezone.now())
        nova_questao.save()

    return render(request, 'votacao/nova_questao.html')

@login_required(login_url="/votacao/login/")
def criar_opcao(request,questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    if request.method == 'POST':
        t = request.POST['nova_opcao']
        nova_opcao = Opcao(questao=questao, opcao_texto=t, votos=0)
        nova_opcao.save()
    return render(request, 'votacao/nova_opcao.html', {'questao': questao})

def cadastro(request):
    if request.method == "GET":
        return render(request, "usuarios/cadastro.html")
    else:
        username1 = request.POST.get('user')
        email1 = request.POST.get('email')
        curso1 = request.POST.get('curses')
        password1 = request.POST.get('passw')
        u = User.objects.filter(username=username1).first()

        if u:
            return HttpResponse('JA existe esse nome de usuario')

        u = User.objects.create_user(username=username1,email=email1,password=password1)
        ut = Aluno(user=u, curso=curso1)
        u.save()
        return HttpResponse(f'foi cadastradooo {u.aluno.curso}')


def login(request):
    if request.method == "GET":
        return render(request, "usuarios/login.html")
    else:
        username1 = request.POST.get('user')
        senha = request.POST.get('passw')

        verifi = authenticate(username=username1,password=senha)

        if verifi:
            login_kar(request, verifi)
            return questoes(request)
        else:
            return HttpResponse("senha ou usarname invalidos")

@login_required(login_url="/votacao/login/")
def questoes(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, "votacao/questoes.html",context)

def logout(request):
 bye(request)
 return redirect('/votacao')


def showname(request):
    if request.user.is_authenticated():
        username = request.user.username
        return username



