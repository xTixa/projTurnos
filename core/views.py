from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import UnidadeCurricular, Docente, Curso
from .db_views import UCMais4Ects, CadeirasSemestre, AlunosMatriculadosPorDia, AlunosPorOrdemAlfabetica, Turnos, Cursos
from django.http import JsonResponse

def index(request):
    return render(request, "home/index.html")

def ingresso(request):
    return render(request, "home/ingresso.html")

def plano_curricular(request):
    # Busca todas as unidades, com joins automáticos
    unidades = UnidadeCurricular.objects.select_related('id_anocurricular', 'id_semestre').order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "home/plano_curricular.html", {"plano": plano})

def horarios(request):
    horarios = {
        "1º Ano": [
            {"dia": "Segunda", "hora": "08:30 - 10:00", "uc": "Programação I", "sala": "Lab 1", "turno": "TP A"},
            {"dia": "Terça", "hora": "10:00 - 11:30", "uc": "Matemática Discreta", "sala": "A1.2", "turno": "T"},
            {"dia": "Quinta", "hora": "09:00 - 10:30", "uc": "Bases de Dados I", "sala": "A2.1", "turno": "T"},
        ],
        "2º Ano": [
            {"dia": "Segunda", "hora": "14:00 - 15:30", "uc": "Programação para Dispositivos Móveis", "sala": "Lab 2", "turno": "TP"},
            {"dia": "Quarta", "hora": "09:00 - 10:30", "uc": "Engenharia de Software", "sala": "A3.2", "turno": "T"},
        ],
        "3º Ano": [
            {"dia": "Terça", "hora": "08:30 - 10:00", "uc": "Sistemas Distribuídos", "sala": "Lab 5", "turno": "TP"},
            {"dia": "Sexta", "hora": "10:30 - 12:00", "uc": "Inteligência Artificial", "sala": "A4.1", "turno": "T"},
        ]
    }

    # Marcar conflitos dentro de cada ano
    for ano, lista in horarios.items():
        for i, h in enumerate(lista):
            h["conflito"] = any(
                i != j and h["dia"] == o["dia"] and h["hora"] == o["hora"]
                for j, o in enumerate(lista)
            )

    return render(request, "home/horarios.html", {"horarios_por_ano": horarios})


def avaliacoes(request):
    avaliacoes_docs = [
        {"ano": "1º Ano", "ficheiro": "avaliacoes_1ano.pdf"},
        {"ano": "2º Ano", "ficheiro": "avaliacoes_2ano.pdf"},
        {"ano": "3º Ano", "ficheiro": "avaliacoes_3ano.pdf"},
    ]
    return render(request, "home/avaliacoes.html", {"avaliacoes_docs": avaliacoes_docs})

def contactos(request):
    # Buscar todos os docentes
    docentes = Docente.objects.all().order_by('nome')

    # Buscar dados do curso principal (por exemplo Engenharia Informática)
    curso = Curso.objects.filter(nome__icontains="Engenharia Informática").first()

    contexto = {
        "curso": curso,
        "docentes": docentes
    }
    return render(request, "home/contactos.html", contexto)

def inscricao_turno(request):
    # Aqui podes colocar a lógica, por agora só mostra o template
    unidades = []  # Se tiveres dados, mete-os aqui
    return render(request, "home/inscricao_turno.html", {"unidades": unidades})

def informacoes(request):
    return render(request, "home/informacoes.html")

def perfil(request):
    return render(request, "profile/perfil.html")

def do_logout(request):
    auth_logout(request)                 # termina a sessão
    return redirect("home:index")        # redireciona para a home

@login_required
def inscrever_turno(request, turno_id):
    if request.method != "POST":
        messages.error(request, "Método inválido. Usa o botão para te inscreveres.")
        return redirect("home:perfil")

    # (futuro) lógica real de BD; por agora só feedback
    messages.success(request, f"Inscrição no turno #{turno_id} concluída com sucesso")
    return redirect("home:perfil")

#ficha 12
def uc_mais_4_ects(request):
    data = list(
        UCMais4Ects.objects
        .order_by('id_anocurricular', 'id_semestre', 'nome')
        .values('id_unidadecurricular', 'nome', 'ects', 'id_anocurricular', 'id_semestre')
    )
    return JsonResponse(data, safe=False)

def cadeiras_semestre(request):
    data = list(
        CadeirasSemestre.objects
        .order_by('semestre_id', 'nome')
        .values('id_unidadecurricular', 'nome', 'ects', 'semestre_id', 'semestre_nome')
    )
    return JsonResponse(data, safe=False)

def alunos_matriculados_por_dia(request):
    data = list(
        AlunosMatriculadosPorDia.objects
        .order_by('ano_matricula', 'dia_matricula', 'nome')
        .values('id_matricula', 'n_mecanografico', 'nome', 'email', 'estado', 'data_matricula', 'dia_matricula', 'ano_matricula')
    )
    return JsonResponse(data, safe=False)

def alunos_por_ordem_alfabetica(request):
    data = list(
        AlunosPorOrdemAlfabetica.objects
        .order_by('nome')
        .values('n_mecanografico', 'nome', 'email', 'id_anocurricular')
    )
    return JsonResponse(data, safe=False)

def turnos_list(request):
    data = list(
        Turnos.objects
        .order_by('id_turno')
        .values('id_turno', 'n_turno', 'capacidade', 'tipo')
    )
    return JsonResponse(data, safe=False)

def cursos_list(request):
    data = list(
        Cursos.objects
        .order_by('id_curso')
        .values('id_curso', 'nome', 'grau')
    )
    return JsonResponse(data, safe=False)
