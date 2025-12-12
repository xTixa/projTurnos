from django.db import connection

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
