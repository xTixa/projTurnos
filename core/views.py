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
    horarios_mock = {
        "1º Ano": [
            {"hora": "08:30 - 10:00", "segunda": "Programação I", "terca": "Matemática Discreta", "quarta": "Sistemas Digitais", "quinta": "Livre", "sexta": "Programação I"},
            {"hora": "10:00 - 11:30", "segunda": "Matemática Discreta", "terca": "Sistemas Digitais", "quarta": "Programação I", "quinta": "Livre", "sexta": "Matemática Discreta"},
        ],
        "2º Ano": [
            {"hora": "08:30 - 10:00", "segunda": "Bases de Dados I", "terca": "Engenharia Software", "quarta": "SO", "quinta": "Livre", "sexta": "Redes"},
            {"hora": "10:00 - 11:30", "segunda": "Redes", "terca": "SO", "quarta": "Bases de Dados I", "quinta": "Livre", "sexta": "Engenharia Software"},
        ],
        "3º Ano": [
            {"hora": "09:00 - 10:30", "segunda": "AI", "terca": "Segurança", "quarta": "Web Avançada", "quinta": "Livre", "sexta": "Projeto Final"},
        ],
    }
    return render(request, "home/horarios.html", {"horarios": horarios_mock})

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

def login_view(request):
    return render(request, "auth/login.html")

def inscricao_turno(request):
    unidades = [
        {
            "nome": "Programação I",
            "turnos": [
                {"nome": "Turno 1", "horario": "Segunda 08:30 - 10:00", "vagas": 5},
                {"nome": "Turno 2", "horario": "Quarta 10:00 - 11:30", "vagas": 2},
                {"nome": "Turno 3", "horario": "Sexta 14:00 - 15:30", "vagas": 0},
            ],
        },
        {
            "nome": "Matemática Discreta",
            "turnos": [
                {"nome": "Turno 1", "horario": "Terça 08:30 - 10:00", "vagas": 4},
                {"nome": "Turno 2", "horario": "Quinta 10:00 - 11:30", "vagas": 1},
            ],
        },
        {
            "nome": "Sistemas Digitais",
            "turnos": [
                {"nome": "Turno 1", "horario": "Segunda 10:00 - 12:00", "vagas": 8},
            ],
        },
    ]
    return render(request, "home/inscricao_turno.html", {"unidades": unidades})
