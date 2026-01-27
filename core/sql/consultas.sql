-- Funcoes auxiliares para PostgreSQLConsultas
-- Executar este script na base de dados para criar/atualizar as funcoes usadas pelo backend.

CREATE OR REPLACE FUNCTION fn_cadeiras_semestre()
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, ects NUMERIC, semestre_id INTEGER, semestre_nome TEXT)
LANGUAGE sql
AS $$
    SELECT id_unidadecurricular, nome, ects, semestre_id, semestre_nome
    FROM cadeirassemestre
    ORDER BY semestre_id, nome;
$$;

CREATE OR REPLACE FUNCTION fn_alunos_por_ordem_alfabetica()
RETURNS TABLE(n_mecanografico INTEGER, nome TEXT, email TEXT, id_anocurricular INTEGER)
LANGUAGE sql
AS $$
    SELECT n_mecanografico, nome, email, id_anocurricular
    FROM vw_alunos_por_ordem_alfabetica
    ORDER BY nome;
$$;

CREATE OR REPLACE FUNCTION fn_turnos_list()
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, capacidade INTEGER, tipo TEXT)
LANGUAGE sql
AS $$
    SELECT id_turno, n_turno, capacidade, tipo
    FROM vw_turnos
    ORDER BY id_turno;
$$;

CREATE OR REPLACE FUNCTION fn_cursos_list()
RETURNS TABLE(id_curso INTEGER, nome TEXT, grau TEXT)
LANGUAGE sql
AS $$
    SELECT id_curso, nome, grau
    FROM vw_cursos
    ORDER BY id_curso;
$$;

CREATE OR REPLACE FUNCTION fn_dashboard_totais()
RETURNS TABLE(
    total_users BIGINT,
    total_turnos BIGINT,
    total_ucs BIGINT,
    total_cursos BIGINT,
    total_horarios BIGINT,
    total_avaliacoes BIGINT,
    vagas_total BIGINT,
    vagas_ocupadas BIGINT
)
LANGUAGE sql
AS $$
    SELECT
        (SELECT COUNT(*) FROM auth_user) AS total_users,
        (SELECT COUNT(*) FROM turno) AS total_turnos,
        (SELECT COUNT(*) FROM unidade_curricular) AS total_ucs,
        (SELECT COUNT(*) FROM curso) AS total_cursos,
        (SELECT COUNT(*) FROM core_horariopdf) AS total_horarios,
        (SELECT COUNT(*) FROM core_avaliacaopdf) AS total_avaliacoes,
        (SELECT COALESCE(SUM(capacidade), 0) FROM turno) AS vagas_total,
        (SELECT COUNT(*) FROM inscricao_turno) AS vagas_ocupadas;
$$;

CREATE OR REPLACE FUNCTION fn_alunos_por_uc_top10()
RETURNS TABLE(uc_nome TEXT, total BIGINT)
LANGUAGE sql
AS $$
    SELECT uc.nome AS uc_nome, COUNT(*) AS total
    FROM inscrito_uc iu
    JOIN unidade_curricular uc ON uc.id_unidadecurricular = iu.id_unidadecurricular
    WHERE iu.estado = TRUE
    GROUP BY uc.nome
    ORDER BY total DESC
    LIMIT 10;
$$;

CREATE OR REPLACE FUNCTION fn_anos_curriculares()
RETURNS TABLE(id_anocurricular INTEGER, ano_curricular TEXT)
LANGUAGE sql
AS $$
    SELECT id_anocurricular, ano_curricular
    FROM ano_curricular
    ORDER BY id_anocurricular;
$$;

CREATE OR REPLACE FUNCTION fn_docentes()
RETURNS TABLE(id_docente INTEGER, nome TEXT, email TEXT, cargo TEXT)
LANGUAGE sql
AS $$
    SELECT id_docente, nome, email, cargo
    FROM docente
    ORDER BY nome;
$$;

CREATE OR REPLACE FUNCTION fn_ucs_por_curso(p_id_curso INTEGER)
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, id_anocurricular INTEGER, id_semestre INTEGER, semestre TEXT)
LANGUAGE sql
AS $$
    SELECT uc.id_unidadecurricular, uc.nome, uc.id_anocurricular, uc.id_semestre, s.semestre
    FROM unidade_curricular uc
    JOIN semestre s ON s.id_semestre = uc.id_semestre
    WHERE uc.id_curso = p_id_curso
    ORDER BY uc.id_anocurricular, uc.id_semestre;
$$;

CREATE OR REPLACE FUNCTION fn_pdfs_por_ano_curso(p_model_table TEXT, p_id_curso INTEGER)
RETURNS TABLE(id_anocurricular INTEGER, ano_curricular TEXT, id INTEGER, nome TEXT, ficheiro TEXT, atualizado_em TIMESTAMP, id_curso INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    tbl TEXT;
BEGIN
    IF lower(p_model_table) = 'core_horariopdf' THEN
        tbl := 'core_horariopdf';
    ELSIF lower(p_model_table) = 'core_avaliacaopdf' THEN
        tbl := 'core_avaliacaopdf';
    ELSE
        RAISE EXCEPTION 'Tabela invalida: %', p_model_table;
    END IF;

    RETURN QUERY EXECUTE format(
        'SELECT ac.id_anocurricular, ac.ano_curricular, p.id, p.nome, p.ficheiro, p.atualizado_em, p.id_curso
         FROM %I p
         JOIN ano_curricular ac ON ac.id_anocurricular = p.id_anocurricular
         WHERE p.id_curso = $1 OR p.id_curso IS NULL
         ORDER BY ac.id_anocurricular DESC, p.atualizado_em DESC',
        tbl
    ) USING p_id_curso;
END;
$$;

CREATE OR REPLACE FUNCTION fn_users_combinado()
RETURNS TABLE(id TEXT, username TEXT, email TEXT, date_joined TIMESTAMP, is_active BOOLEAN, is_staff BOOLEAN, tipo TEXT)
LANGUAGE sql
AS $$
    SELECT u.id::text AS id, u.username, u.email, u.date_joined, u.is_active, u.is_staff, 'Admin' AS tipo
    FROM auth_user u
    UNION ALL
    SELECT a.n_mecanografico::text, a.nome, a.email, NULL::timestamp, TRUE, FALSE, 'Aluno'
    FROM aluno a
    UNION ALL
    SELECT d.id_docente::text, d.nome, d.email, NULL::timestamp, TRUE, FALSE, 'Docente'
    FROM docente d
    ORDER BY tipo, id;
$$;

CREATE OR REPLACE FUNCTION fn_get_user_by_id(p_user_id INTEGER)
RETURNS TABLE(id TEXT, username TEXT, email TEXT, is_staff BOOLEAN, is_active BOOLEAN, tipo TEXT, id_curso INTEGER, id_anocurricular INTEGER, cargo TEXT)
LANGUAGE sql
AS $$
    SELECT id::text, username, email, is_staff, is_active, 'Admin'::text AS tipo, NULL::integer, NULL::integer, NULL::text
    FROM auth_user
    WHERE id = p_user_id
    UNION ALL
    SELECT n_mecanografico::text, nome, email, FALSE, TRUE, 'Aluno'::text, id_curso, id_anocurricular, NULL::text
    FROM aluno
    WHERE n_mecanografico = p_user_id
    UNION ALL
    SELECT id_docente::text, nome, email, FALSE, TRUE, 'Docente'::text, NULL::integer, NULL::integer, cargo
    FROM docente
    WHERE id_docente = p_user_id
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION fn_update_user(p_user_id INTEGER, p_tipo TEXT, p_username TEXT, p_email TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF lower(p_tipo) = 'admin' THEN
        UPDATE auth_user SET username = p_username, email = p_email WHERE id = p_user_id;
    ELSIF lower(p_tipo) = 'aluno' THEN
        UPDATE aluno SET nome = p_username, email = p_email WHERE n_mecanografico = p_user_id;
    ELSIF lower(p_tipo) = 'docente' THEN
        UPDATE docente SET nome = p_username, email = p_email WHERE id_docente = p_user_id;
    ELSE
        RETURN FALSE;
    END IF;
    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION fn_delete_aluno_cascade(p_n_mecanografico INTEGER)
RETURNS TABLE(matriculas INTEGER, inscricoes_turno INTEGER, inscrito_uc INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM matricula WHERE n_mecanografico = p_n_mecanografico;
    GET DIAGNOSTICS matriculas = ROW_COUNT;

    DELETE FROM inscricao_turno WHERE n_mecanografico = p_n_mecanografico;
    GET DIAGNOSTICS inscricoes_turno = ROW_COUNT;

    DELETE FROM inscrito_uc WHERE n_mecanografico = p_n_mecanografico;
    GET DIAGNOSTICS inscrito_uc = ROW_COUNT;

    DELETE FROM aluno WHERE n_mecanografico = p_n_mecanografico;

    RETURN NEXT;
END;
$$;

CREATE OR REPLACE FUNCTION fn_delete_docente_cascade(p_id_docente INTEGER)
RETURNS TABLE(leciona_uc INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM leciona_uc WHERE id_docente = p_id_docente;
    GET DIAGNOSTICS leciona_uc = ROW_COUNT;

    DELETE FROM docente WHERE id_docente = p_id_docente;

    RETURN NEXT;
END;
$$;

CREATE OR REPLACE FUNCTION fn_delete_admin_user(p_user_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    DELETE FROM auth_user WHERE id = p_user_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_turnos_sem_uc()
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, capacidade INTEGER, tipo TEXT)
LANGUAGE sql
AS $$
    SELECT id_turno, n_turno, capacidade, tipo
    FROM turno
    WHERE id_turno NOT IN (SELECT DISTINCT id_turno FROM turno_uc)
    ORDER BY id_turno;
$$;

CREATE OR REPLACE FUNCTION fn_get_turno_by_id(p_turno_id INTEGER)
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, capacidade INTEGER, tipo TEXT)
LANGUAGE sql
AS $$
    SELECT id_turno, n_turno, capacidade, tipo
    FROM turno
    WHERE id_turno = p_turno_id;
$$;

CREATE OR REPLACE FUNCTION fn_create_turno(p_n_turno INTEGER, p_capacidade INTEGER, p_tipo TEXT)
RETURNS INTEGER
LANGUAGE sql
AS $$
    INSERT INTO turno (n_turno, capacidade, tipo) VALUES (p_n_turno, p_capacidade, p_tipo) RETURNING id_turno;
$$;

CREATE OR REPLACE FUNCTION fn_update_turno(p_turno_id INTEGER, p_n_turno INTEGER, p_capacidade INTEGER, p_tipo TEXT)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    UPDATE turno SET n_turno = p_n_turno, capacidade = p_capacidade, tipo = p_tipo WHERE id_turno = p_turno_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_delete_turno(p_turno_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    DELETE FROM turno WHERE id_turno = p_turno_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_get_horario_pdf_by_id(p_pdf_id INTEGER)
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_anocurricular INTEGER, id_curso INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
    FROM core_horariopdf
    WHERE id = p_pdf_id;
$$;

CREATE OR REPLACE FUNCTION fn_create_horario_pdf(p_nome TEXT, p_ficheiro TEXT, p_id_anocurricular INTEGER, p_id_curso INTEGER)
RETURNS INTEGER
LANGUAGE sql
AS $$
    INSERT INTO core_horariopdf (nome, ficheiro, id_anocurricular, id_curso)
    VALUES (p_nome, p_ficheiro, p_id_anocurricular, p_id_curso)
    RETURNING id;
$$;

CREATE OR REPLACE FUNCTION fn_update_horario_pdf(p_id INTEGER, p_nome TEXT, p_ficheiro TEXT, p_id_anocurricular INTEGER, p_id_curso INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    UPDATE core_horariopdf
    SET nome = p_nome, ficheiro = p_ficheiro, id_anocurricular = p_id_anocurricular, id_curso = p_id_curso
    WHERE id = p_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_delete_horario_pdf(p_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    DELETE FROM core_horariopdf WHERE id = p_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_list_horario_pdfs()
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_anocurricular INTEGER, id_curso INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
    FROM core_horariopdf
    ORDER BY atualizado_em DESC;
$$;

CREATE OR REPLACE FUNCTION fn_get_latest_horario_pdf()
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_anocurricular INTEGER, id_curso INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
    FROM core_horariopdf
    ORDER BY atualizado_em DESC
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION fn_get_avaliacao_pdf_by_id(p_pdf_id INTEGER)
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_anocurricular INTEGER, id_curso INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
    FROM core_avaliacaopdf
    WHERE id = p_pdf_id;
$$;

CREATE OR REPLACE FUNCTION fn_create_avaliacao_pdf(p_nome TEXT, p_ficheiro TEXT, p_id_anocurricular INTEGER, p_id_curso INTEGER)
RETURNS INTEGER
LANGUAGE sql
AS $$
    INSERT INTO core_avaliacaopdf (nome, ficheiro, id_anocurricular, id_curso)
    VALUES (p_nome, p_ficheiro, p_id_anocurricular, p_id_curso)
    RETURNING id;
$$;

CREATE OR REPLACE FUNCTION fn_update_avaliacao_pdf(p_id INTEGER, p_nome TEXT, p_ficheiro TEXT, p_id_anocurricular INTEGER, p_id_curso INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    UPDATE core_avaliacaopdf
    SET nome = p_nome, ficheiro = p_ficheiro, id_anocurricular = p_id_anocurricular, id_curso = p_id_curso
    WHERE id = p_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_delete_avaliacao_pdf(p_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    DELETE FROM core_avaliacaopdf WHERE id = p_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_list_avaliacao_pdfs()
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_anocurricular INTEGER, id_curso INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
    FROM core_avaliacaopdf
    ORDER BY atualizado_em DESC;
$$;

CREATE OR REPLACE FUNCTION fn_get_uc_by_id(p_uc_id INTEGER)
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, id_curso INTEGER, id_anocurricular INTEGER, id_semestre INTEGER, ects NUMERIC)
LANGUAGE sql
AS $$
    SELECT id_unidadecurricular, nome, id_curso, id_anocurricular, id_semestre, ects
    FROM unidade_curricular
    WHERE id_unidadecurricular = p_uc_id;
$$;

CREATE OR REPLACE FUNCTION fn_list_all_ucs()
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, id_curso INTEGER, id_anocurricular INTEGER, id_semestre INTEGER, ects NUMERIC)
LANGUAGE sql
AS $$
    SELECT id_unidadecurricular, nome, id_curso, id_anocurricular, id_semestre, ects
    FROM unidade_curricular
    ORDER BY id_unidadecurricular;
$$;

CREATE OR REPLACE FUNCTION fn_create_uc(p_nome TEXT, p_id_curso INTEGER, p_id_anocurricular INTEGER, p_id_semestre INTEGER, p_ects NUMERIC)
RETURNS INTEGER
LANGUAGE sql
AS $$
    INSERT INTO unidade_curricular (nome, id_curso, id_anocurricular, id_semestre, ects)
    VALUES (p_nome, p_id_curso, p_id_anocurricular, p_id_semestre, p_ects)
    RETURNING id_unidadecurricular;
$$;

CREATE OR REPLACE FUNCTION fn_update_uc(p_uc_id INTEGER, p_nome TEXT, p_id_curso INTEGER, p_id_anocurricular INTEGER, p_id_semestre INTEGER, p_ects NUMERIC)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    UPDATE unidade_curricular
    SET nome = p_nome, id_curso = p_id_curso, id_anocurricular = p_id_anocurricular, id_semestre = p_id_semestre, ects = p_ects
    WHERE id_unidadecurricular = p_uc_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_delete_uc(p_uc_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    DELETE FROM unidade_curricular WHERE id_unidadecurricular = p_uc_id RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_get_turnos_uc_by_uc_id(p_uc_id INTEGER)
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, tipo TEXT, capacidade INTEGER, hora_inicio TIME, hora_fim TIME)
LANGUAGE sql
AS $$
    SELECT tu.id_turno, t.n_turno, t.tipo, t.capacidade, tu.hora_inicio, tu.hora_fim
    FROM turno_uc tu
    JOIN turno t ON t.id_turno = tu.id_turno
    WHERE tu.id_unidadecurricular = p_uc_id
    ORDER BY t.n_turno;
$$;

CREATE OR REPLACE FUNCTION fn_delete_turnos_uc_by_uc_id(p_uc_id INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_rows INTEGER;
BEGIN
    DELETE FROM turno_uc WHERE id_unidadecurricular = p_uc_id;
    GET DIAGNOSTICS deleted_rows = ROW_COUNT;
    RETURN deleted_rows;
END;
$$;

CREATE OR REPLACE FUNCTION fn_create_turno_uc(p_id_turno INTEGER, p_id_uc INTEGER, p_hora_inicio TIME, p_hora_fim TIME)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    INSERT INTO turno_uc (id_turno, id_unidadecurricular, hora_inicio, hora_fim)
    VALUES (p_id_turno, p_id_uc, p_hora_inicio, p_hora_fim) RETURNING TRUE;
$$;

CREATE OR REPLACE FUNCTION fn_get_semestres()
RETURNS TABLE(id_semestre INTEGER, semestre TEXT)
LANGUAGE sql
AS $$
    SELECT id_semestre, semestre FROM semestre ORDER BY id_semestre;
$$;
