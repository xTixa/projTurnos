from django.db import connection
from django.shortcuts import redirect
from django.contrib import messages
from bd2_projeto.services.mongo_service import adicionar_log

def registar_log(request, operacao, entidade, chave, detalhes):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO log_eventos
            (data_hora, operacao, detalhes, utilizador_db, chave_primaria, entidade)
            VALUES (now(), %s, %s, %s, %s, %s)
        """, [
            operacao,
            detalhes,
            request.user.username,
            chave,
            entidade
        ])
    
    # Também guarda no MongoDB
    adicionar_log(operacao, {
        "utilizador": request.user.username,
        "entidade": entidade,
        "chave_primaria": chave,
        "detalhes": detalhes
    })

# ==========================================
# DECORADOR PARA ROTAS DE ADMIN
# ==========================================
def admin_required(view_func):
    """
    Decorador para proteger rotas de administração
    Verifica se o utilizador está autenticado e é staff
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "É necessário iniciar sessão como administrador.")
            return redirect("home:login")

        if not request.user.is_staff:
            messages.error(request, "Acesso restrito ao administrador.")
            return redirect("home:index")

        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# DECORADOR PARA ROTAS DE ALUNOS
# ==========================================
def aluno_required(view_func):
    """
    Decorador para proteger rotas que requerem sessão de aluno
    Verifica se existe uma sessão ativa com user_tipo = "aluno"
    """
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


# ==========================================
# DECORADOR PARA ROTAS DE DOCENTES
# ==========================================
def docente_required(view_func):
    """
    Decorador para proteger rotas que requerem sessão de docente
    Verifica se existe uma sessão ativa com user_tipo = "docente"
    """
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


# ==========================================
# DECORADOR PARA ROTAS DE UTILIZADORES AUTENTICADOS (ALUNO OU DOCENTE)
# ==========================================
def user_required(view_func):
    """
    Decorador para proteger rotas que requerem qualquer tipo de autenticação
    (aluno, docente ou admin)
    """
    def wrapper(request, *args, **kwargs):
        # Verifica se existe sessão ativa (aluno/docente) ou user Django autenticado
        tem_sessao = "user_tipo" in request.session
        tem_user_django = request.user.is_authenticated
        
        if not tem_sessao and not tem_user_django:
            messages.error(request, "É necessário iniciar sessão para aceder a esta página.")
            return redirect("home:login")

        return view_func(request, *args, **kwargs)
    return wrapper
