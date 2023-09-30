from votacao.models import Questao, Opcao
# 1
i = 0
for opcao in Opcao.objects.all():
    i = i + int(opcao.votos)
print(i)

# 2
for questao in Questao.objects.all():
    n = 0
    f = questao.opcao_set.all()
    for i in f:
        if i.votos > n:
            n = i.votos
            of = i.opcao_texto
    print('\n'+str(questao) + '\nOpcao escolhida : ' + str(of))
