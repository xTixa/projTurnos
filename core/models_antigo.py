import pytest
from django.db import connections

@pytest.fixture(scope="module", autouse=True)
def setup_criar_docente(django_db_blocker):
    print("\n[DEBUG] Setup fixture está a executar")
    with django_db_blocker.unblock():
        cur = connections["default"].cursor()
        print("[DEBUG] Antes de criar procedure")
        cur.execute("""
            CREATE OR REPLACE PROCEDURE criar_docente(
                p_nome VARCHAR,
                p_email VARCHAR,
                p_cargo VARCHAR
            )
            LANGUAGE plpgsql
            AS $$
            BEGIN
                IF p_nome IS NULL OR p_email IS NULL OR p_cargo IS NULL THEN
                    RAISE EXCEPTION 'Nenhum dos parâmetros pode ser nulo!';
                END IF;
                IF EXISTS (SELECT 1 FROM docente WHERE email = p_email) THEN
                    RAISE EXCEPTION 'Já existe um docente com este email';
                END IF;
                INSERT INTO docente (nome, email, cargo)
                VALUES (p_nome, p_email, p_cargo);
            END;
            $$;
        """)
        print("[DEBUG] Procedure criado na BD de teste!")
