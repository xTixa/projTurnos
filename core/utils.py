from django.db import connection
from django.shortcuts import redirect
from django.contrib import messages
from bd2_projeto.services.mongo_service import adicionar_log

def registar_log(request, operacao, entidade, chave, detalhes):
    username = request.session.get("user_nome") or request.session.get("user_email") or "anon"
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO log_eventos
            (data_hora, operacao, detalhes, utilizador_db, chave_primaria, entidade)
            VALUES (now(), %s, %s, %s, %s, %s)
        """, [
            operacao,
            detalhes,
            username,
            chave,
            entidade
        ])
    
    # Também guarda no MongoDB
    adicionar_log(operacao, {
        "utilizador": username,
        "entidade": entidade,
        "chave_primaria": chave,
        "detalhes": detalhes
    })

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("user_tipo") != "admin":
            messages.error(request, "É necessário iniciar sessão como administrador.")
            return redirect("home:login")

        return view_func(request, *args, **kwargs)
    return wrapper

def aluno_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Verifica se existe sessão ativa
        if "user_tipo" not in request.session:
            messages.error(request, "É necessário iniciar sessão como aluno.")
            return redirect("home:login")
        
        # Verifica se é aluno
        if request.session.get("user_tipo") != "aluno":
            messages.error(request, "Esta página é apenas para alunos.")
            return redirect("home:index")

        return view_func(request, *args, **kwargs)
    return wrapper

def docente_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Verifica se existe sessão ativa
        if "user_tipo" not in request.session:
            messages.error(request, "É necessário iniciar sessão como docente.")
            return redirect("home:login")
        
        # Verifica se é docente
        if request.session.get("user_tipo") != "docente":
            messages.error(request, "Esta página é apenas para docentes.")
            return redirect("home:index")

        return view_func(request, *args, **kwargs)
    return wrapper

def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        tem_sessao = "user_tipo" in request.session
        
        if not tem_sessao:
            messages.error(request, "É necessário iniciar sessão para aceder a esta página.")
            return redirect("home:login")

        return view_func(request, *args, **kwargs)
    return wrapper
