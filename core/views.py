from django.shortcuts import render

def index(request):
    return render(request, "home/index.html")

def ingresso(request):
    return render(request, "home/ingresso.html")

from django.shortcuts import render

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
                {"nome": "Bases de Dados I", "ects": 6, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Engenharia de Software", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 2,
            "semestre": 2,
            "ucs": [
                {"nome": "Bases de Dados I", "ects": 6, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Engenharia de Software", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
                {"nome": "Sistemas Digitais", "ects": 5, "tipo": "Obrigatória", "docente": "", "descricao": "Circuitos combinatórios e sequenciais."},
            ],
        },
        {
            "ano": 3,
            "semestre": 1,
            "ucs": [
                {"nome": "Bases de Dados I", "ects": 6, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Engenharia de Software", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
            ],
        },
        {
            "ano": 3,
            "semestre": 2,
            "ucs": [
                {"nome": "Bases de Dados I", "ects": 6, "tipo": "Obrigatória", "docente": "Fernando Silva", "descricao": "Modelo relacional e SQL."},
                {"nome": "Engenharia de Software", "ects": 6, "tipo": "Obrigatória", "docente": "Paulo Correia", "descricao": "Requisitos, UML e metodologias ágeis."},
            ],
        },
    ]
    return render(request, "home/plano.html", {"plano": plano_curricular})


def horarios(request):
    return render(request, "home/horarios.html")

def avaliacoes(request):
    return render(request, "home/avaliacoes.html")

def contactos(request):
    return render(request, "home/contactos.html")

def informacoes(request):
    return render(request, "home/informacoes.html")

def login_view(request):
    return render(request, "auth/login.html")