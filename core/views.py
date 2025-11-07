from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

def index(request):
    return render(request, "home/index.html")

def ingresso(request):
    return render(request, "home/ingresso.html")

def plano(request):
    plano_curricular = [
        {
            "ano": 1,
            "semestre": 1,
            "ucs": [
                {"nome": "Análise Matemática", "ects": 5.5, "tipo": "Obrigatória", "docente": "Cecília", "descricao": "Introdução à lógica, conjuntos e estruturas discretas."},
                {"nome": "Álgebra", "ects": 4.5, "tipo": "Obrigatória", "docente": "Lurdes Sousa", "descricao": "Conceitos básicos de programação em C."},
                {"nome": "Sistemas Digitais", "ects": 6, "tipo": "Obrigatória", "docente": "Francisco Francisco", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Algoritmos e Programação", "ects": 8, "tipo": "Obrigatória", "docente": "Joana Fialho", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Tecnologias dos Computadores", "ects": 6, "tipo": "Obrigatória", "docente": "Carlos Simoes", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 1,
            "semestre": 2,
            "ucs": [
                {"nome": "Arquiteturas de Computador", "ects": 5.5, "tipo": "Obrigatória", "docente": "Rita Pinto", "descricao": "Álgebra linear e cálculo diferencial."},
                {"nome": "Matemática Discreta", "ects": 5, "tipo": "Obrigatória", "docente": "Pedro Santos", "descricao": "Estruturas de dados e modularidade."},
                {"nome": "Matemática Aplicada", "ects": 5, "tipo": "Obrigatória", "docente": "Marta Dias", "descricao": "Gestão de processos e memória."},
                {"nome": "Redes de Comunicação I", "ects": 6.5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Estruturas de Dados", "ects": 8, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 2,
            "semestre": 1,
            "ucs": [
                {"nome": "Programação Orientada a Objetos", "ects": 6.5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Análise de Sistemas", "ects": 6.5, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Sistemas Operativos", "ects": 5.5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Aplicações para a Internet I", "ects": 6.5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Usabilidade", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 2,
            "semestre": 2,
            "ucs": [
                {"nome": "Engenharia de Software I", "ects": 4.5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Bases de Dados I", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Aplicações para a Internet II", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Redes de Comunicação II", "ects": 4.5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Programação para Dispositivos Móveis", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Projeto Integrado", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 3,
            "semestre": 1,
            "ucs": [
                {"nome": "Segurança Informática", "ects": 4.5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Redes de Comunicação III", "ects": 4.5, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Complementos de Sistemas Operativos", "ects": 5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Bases de Dados II", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Sistemas Embebidos", "ects": 5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Sistemas Distribuídos", "ects": 5, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
            ],
        },
        {
            "ano": 3,
            "semestre": 2,
            "ucs": [
                {"nome": "Inteligência Artificial", "ects": 5, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Engenharia de Software II", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Empreendedorismo e Gestão de Empresas", "ects": 3, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Projeto", "ects": 16, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
            ],
        },
    ]
    return render(request, "home/plano.html", {"plano": plano_curricular})

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
    return render(request, "home/contactos.html")

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
