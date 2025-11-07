import pytest
from django.db import connections

@pytest.mark.django_db
def test_criar_docente():
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    cur.execute("CALL criar_docente(%s, %s, %s);", ["Teste Pytest", "pytest_teste@escola.pt", "Professor"])
    cur.execute("SELECT COUNT(*) FROM docente WHERE email = %s;", ["pytest_teste@escola.pt"])
    count = cur.fetchone()[0]
    assert count == 1, "O docente não foi criado corretamente pelo procedimento!"
    cur.execute("ROLLBACK")

@pytest.mark.django_db
def test_atualizar_docente():
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    cur.execute("CALL criar_docente(%s, %s, %s);", ["NomeOriginal", "atualizar@teste.pt", "Assistente"])
    cur.execute("SELECT id_docente FROM docente WHERE email = %s;", ["atualizar@teste.pt"])
    id_docente = cur.fetchone()[0]
    cur.execute("CALL atualizar_docente(%s, %s, %s, %s);", [id_docente, "Novo Nome", "novoemail@teste.pt", "Professor"])
    cur.execute("SELECT nome, email, cargo FROM docente WHERE id_docente = %s;", [id_docente])
    nome, email, cargo = cur.fetchone()
    assert nome == "Novo Nome"
    assert email == "novoemail@teste.pt"
    assert cargo == "Professor"
    cur.execute("ROLLBACK")

@pytest.mark.django_db
def test_apagar_docente():
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    cur.execute("CALL criar_docente(%s, %s, %s);", ["NomeDelete", "apagar@teste.pt", "Assistente"])
    cur.execute("SELECT id_docente FROM docente WHERE email = %s;", ["apagar@teste.pt"])
    id_docente = cur.fetchone()[0]
    cur.execute("CALL apagar_docente(%s);", [id_docente])
    cur.execute("SELECT COUNT(*) FROM docente WHERE id_docente = %s;", [id_docente])
    count = cur.fetchone()[0]
    assert count == 0, "O docente não foi removido corretamente pelo procedimento!"
    cur.execute("ROLLBACK")


    
    

