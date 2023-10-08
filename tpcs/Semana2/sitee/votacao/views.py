from django.shortcuts import render,  get_object_or_404
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Questao, Opcao, Aluno, Voto
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
    return render(request, 'votacao/detalhe.html', {
        'questao': questao,
        'opcoes': questao.opcao_set.all(),
        'tem_opcoes': questao.opcao_set.count() > 0,
        'votos': Voto.get_votos_from_aluno(request.user)
    })

@login_required(login_url="/votacao/login/")
def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    try:
        opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': "Não escolheu uma opção", })
    else:
        opcao_seleccionada.add_voto(request.user)
        # Retorne sempre HttpResponseRedirect depois de
        # tratar os dados POST de um form
        # pois isso impede os dados de serem tratados
        # repetidamente se o utilizador
        # voltar para a página web anterior.
    return HttpResponseRedirect(reverse('votacao:resultados', args=(questao.id,)))

@login_required(login_url="/votacao/login/")
def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {
        'questao': questao,
        'opcoes_resultados': questao.get_resultados(),
        'votos': Voto.get_votos_from_aluno(request.user)
    })

@login_required(login_url="/votacao/login/")
def nova_questao(request):
    if request.method == 'POST':
        t = request.POST['nova_questao']
        nova_questao = Questao(questao_texto=t, pub_data=timezone.now())
        nova_questao.save()
        return HttpResponseRedirect(reverse('votacao:detalhe', args=(nova_questao.id,)))


    return render(request, 'votacao/nova_questao.html')

@login_required(login_url="/votacao/login/")
def criar_opcao(request,questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    if request.method == 'POST':
        t = request.POST['nova_opcao']
        nova_opcao = Opcao(questao=questao, opcao_texto=t)
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
        temAluno = Aluno.objects.filter(username=username1).first()

        if temAluno:
            return HttpResponse('JA existe esse nome de usuario')

        aluno = Aluno(username=username1, email=email1, curso=curso1, password=password1)
        ## aluno.save will not hash password which is bad
        Aluno.objects.create_user(username=username1, email=email1, curso=curso1, password=password1)
        return HttpResponse(fr'foi cadastradooo em:{aluno.curso} <br> <a href="..\login">Voltar login</a>')


def login(request):
    if request.method == "GET":
        return render(request, "usuarios/login.html")
    else:
        username1 = request.POST.get('user')
        senha = request.POST.get('passw')

        verifi = authenticate(request, username=username1, password=senha)
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
    if request.user.is_authenticated:
        username = request.user.username
        return username

@login_required(login_url="/votacao/login/")
def perfil(request):
    return render(request, "usuarios/perfil.html", {
        # 'username': showname(request),
        # 'email': request.user.email,
        # 'curso': Aluno.get_aluno(request.user).curso,
        'votos': Voto.get_votos_from_aluno(request.user)
    })

@login_required(login_url="/votacao/login/")
def eliminar_opcao(request, questao_id):
    if request.method == 'POST':
        # elimina a opcao
        opcao = get_object_or_404(Opcao, pk=request.POST['opcao'])
        opcao.delete()
        return HttpResponseRedirect(redirect_to=reverse('votacao:detalhe', args=(questao_id,)))
    elif request.method == 'GET':
        # vai para a pagina
        return render(request, 'votacao/eliminar_opcao.html', {'questao': get_object_or_404(Questao, pk=questao_id)})
@login_required(login_url="/votacao/login/")
def eliminar_questao(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    if request.method == 'POST':
        # elimina a questão
        questao = get_object_or_404(Questao, pk=request.POST['questao'])
        questao.delete()
        return HttpResponseRedirect(redirect_to=reverse('votacao:questoes'))
    elif request.method == 'GET':
        #return render(request, 'votacao/eliminar_questao.html', {'questao': get_object_or_404(Questao, pk=request.GET['questao'])})
        return render(request, 'votacao/eliminar_questao.html', context)
