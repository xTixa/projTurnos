from django.db import connection
from django.shortcuts import redirect
from django.contrib import messages

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

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("home:login")

        if not request.user.is_staff:
            messages.error(request, "Acesso restrito ao administrador.")
            return redirect("home:index")

        return view_func(request, *args, **kwargs)
    return wrapper