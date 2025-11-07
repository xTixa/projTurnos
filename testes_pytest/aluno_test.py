import pytest
from django.db import connections

@pytest.mark.django_db
def test_criar_aluno():
    """Testa a criação de um aluno via procedure"""
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    
    # Garantir que existem dados de FK antes de criar aluno
    cur.execute("INSERT INTO curso (id_curso, nome, grau) VALUES (1, 'Engenharia Informática', 'Licenciatura') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO ano_curricular (id_anocurricular, ano_curricular) VALUES (1, '1º Ano') ON CONFLICT DO NOTHING;")
    
    # Criar aluno usando procedure
    cur.execute(
        "CALL criar_aluno(%s, %s, %s, %s, %s, %s);",
        [12345, 1, 1, "Teste Aluno", "aluno@teste.pt", "senha123"]
    )
    
    # Verificar que foi criado
    cur.execute("SELECT COUNT(*) FROM aluno WHERE n_mecanografico = %s;", [12345])
    count = cur.fetchone()[0]
    assert count == 1, "O aluno não foi criado corretamente pelo procedimento!"
    
    cur.execute("ROLLBACK")

@pytest.mark.django_db
def test_atualizar_aluno():
    """Testa a atualização de um aluno via procedure"""
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    
    # Criar dados de FK e aluno inicial
    cur.execute("INSERT INTO curso (id_curso, nome, grau) VALUES (1, 'Eng. Informática', 'Licenciatura') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO curso (id_curso, nome, grau) VALUES (2, 'Eng. Civil', 'Licenciatura') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO ano_curricular (id_anocurricular, ano_curricular) VALUES (1, '1º Ano') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO ano_curricular (id_anocurricular, ano_curricular) VALUES (2, '2º Ano') ON CONFLICT DO NOTHING;")
    
    cur.execute(
        "CALL criar_aluno(%s, %s, %s, %s, %s, %s);",
        [99999, 1, 1, "Aluno Original", "original@teste.pt", "senha"]
    )
    
    # Atualizar aluno
    cur.execute(
        "CALL atualizar_aluno(%s, %s, %s, %s, %s, %s);",
        [99999, 2, 2, "Aluno Atualizado", "novo@teste.pt", "novasenha"]
    )
    
    # Verificar atualização
    cur.execute(
        "SELECT nome, email, id_curso, id_anocurricular FROM aluno WHERE n_mecanografico = %s;",
        [99999]
    )
    nome, email, id_curso, id_anocurricular = cur.fetchone()
    assert nome == "Aluno Atualizado"
    assert email == "novo@teste.pt"
    assert id_curso == 2
    assert id_anocurricular == 2
    
    cur.execute("ROLLBACK")

@pytest.mark.django_db
def test_apagar_aluno():
    """Testa a eliminação de um aluno via procedure"""
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    
    # Criar dados de FK e aluno
    cur.execute("INSERT INTO curso (id_curso, nome, grau) VALUES (1, 'Eng. Informática', 'Licenciatura') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO ano_curricular (id_anocurricular, ano_curricular) VALUES (1, '1º Ano') ON CONFLICT DO NOTHING;")
    
    cur.execute(
        "CALL criar_aluno(%s, %s, %s, %s, %s, %s);",
        [88888, 1, 1, "Aluno Delete", "delete@teste.pt", "senha"]
    )
    
    # Apagar aluno
    cur.execute("CALL apagar_aluno(%s);", [88888])
    
    # Verificar que foi apagado
    cur.execute("SELECT COUNT(*) FROM aluno WHERE n_mecanografico = %s;", [88888])
    count = cur.fetchone()[0]
    assert count == 0, "O aluno não foi removido corretamente pelo procedimento!"
    
    cur.execute("ROLLBACK")

@pytest.mark.django_db
def test_listar_alunos():
    """Testa a listagem de alunos"""
    cur = connections["default"].cursor()
    cur.execute("BEGIN")
    
    # Criar dados de FK e alunos
    cur.execute("INSERT INTO curso (id_curso, nome, grau) VALUES (1, 'Eng. Informática', 'Licenciatura') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO ano_curricular (id_anocurricular, ano_curricular) VALUES (1, '1º Ano') ON CONFLICT DO NOTHING;")
    
    cur.execute("CALL criar_aluno(%s, %s, %s, %s, %s, %s);", [11111, 1, 1, "Aluno1", "al1@teste.pt", "s1"])
    cur.execute("CALL criar_aluno(%s, %s, %s, %s, %s, %s);", [22222, 1, 1, "Aluno2", "al2@teste.pt", "s2"])
    
    # Listar alunos
    cur.execute("SELECT * FROM aluno;")
    alunos = cur.fetchall()
    assert len(alunos) >= 2, "A leitura dos alunos está incorreta!"
    
    cur.execute("ROLLBACK")
