-- ============================================================================
-- FUNÇÕES DE EXPORTAÇÃO (CSV, JSON, XML)
-- ============================================================================

-- Exportar alunos para CSV (texto)
CREATE OR REPLACE FUNCTION public.exportar_alunos_csv()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado TEXT := 'N_Mecanografico;Nome;Email;Curso;Ano_Curricular' || E'\n';
    v_linha TEXT;
BEGIN
    FOR v_linha IN
        SELECT 
            a.n_mecanografico || ';' ||
            a.nome || ';' ||
            a.email || ';' ||
            c.nome || ';' ||
            ac.ano_curricular
        FROM aluno a
        JOIN curso c ON a.id_curso = c.id_curso
        JOIN ano_curricular ac ON a.id_anocurricular = ac.id_anocurricular
        ORDER BY a.nome
    LOOP
        v_resultado := v_resultado || v_linha || E'\n';
    END LOOP;
    RETURN v_resultado;
END;
$$;

-- Exportar turnos de uma UC para CSV
CREATE OR REPLACE FUNCTION public.exportar_turnos_uc_csv(p_id_uc INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado TEXT := 'ID_Turno;Tipo;Docente;Sala;Dia;Horario;Capacidade;Inscritos' || E'\n';
    v_linha TEXT;
BEGIN
    FOR v_linha IN
        SELECT 
            t.id_turno || ';' ||
            t.tipo || ';' ||
            d.nome || ';' ||
            COALESCE(t.sala, 'N/A') || ';' ||
            COALESCE(t.dia_semana, 'N/A') || ';' ||
            COALESCE(t.hora_inicio::TEXT || '-' || t.hora_fim::TEXT, 'N/A') || ';' ||
            t.capacidade || ';' ||
            COUNT(it.n_mecanografico)
        FROM turno t
        JOIN docente d ON t.id_docente = d.id_docente
        LEFT JOIN inscricao_turno it ON t.id_turno = it.id_turno
        WHERE t.id_unidadecurricular = p_id_uc
        GROUP BY t.id_turno, t.tipo, d.nome, t.sala, t.dia_semana, t.hora_inicio, t.hora_fim, t.capacidade
        ORDER BY t.tipo, t.id_turno
    LOOP
        v_resultado := v_resultado || v_linha || E'\n';
    END LOOP;
    RETURN v_resultado;
END;
$$;

-- Exportar alunos para JSON
CREATE OR REPLACE FUNCTION public.exportar_alunos_json()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT json_agg(json_build_object(
        'n_mecanografico', a.n_mecanografico,
        'nome', a.nome,
        'email', a.email,
        'curso', json_build_object('id', c.id_curso, 'nome', c.nome),
        'ano_curricular', json_build_object('id', ac.id_anocurricular, 'ano', ac.ano_curricular)
    ))
    INTO v_resultado
    FROM aluno a
    JOIN curso c ON a.id_curso = c.id_curso
    JOIN ano_curricular ac ON a.id_anocurricular = ac.id_anocurricular
    ORDER BY a.nome;
    RETURN v_resultado;
END;
$$;

-- Exportar inscrições de um aluno para JSON
CREATE OR REPLACE FUNCTION public.exportar_inscricoes_aluno_json(p_n_mecanografico INTEGER)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT json_build_object(
        'aluno', json_build_object(
            'n_mecanografico', a.n_mecanografico,
            'nome', a.nome,
            'email', a.email
        ),
        'inscricoes', json_agg(json_build_object(
            'unidade_curricular', uc.nome,
            'turno', json_build_object(
                'id', t.id_turno,
                'tipo', t.tipo,
                'sala', t.sala,
                'dia_semana', t.dia_semana,
                'horario', t.hora_inicio::TEXT || ' - ' || t.hora_fim::TEXT
            ),
            'docente', d.nome,
            'data_inscricao', it.data_inscricao
        ))
    )
    INTO v_resultado
    FROM aluno a
    LEFT JOIN inscricao_turno it ON a.n_mecanografico = it.n_mecanografico
    LEFT JOIN turno t ON it.id_turno = t.id_turno
    LEFT JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
    LEFT JOIN docente d ON t.id_docente = d.id_docente
    WHERE a.n_mecanografico = p_n_mecanografico
    GROUP BY a.n_mecanografico, a.nome, a.email;
    RETURN v_resultado;
END;
$$;

-- Exportar turnos de uma UC para JSON
CREATE OR REPLACE FUNCTION public.exportar_turnos_uc_json(p_id_uc INTEGER)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT json_build_object(
        'unidade_curricular', json_build_object(
            'id', uc.id_unidadecurricular,
            'nome', uc.nome,
            'sigla', uc.sigla
        ),
        'turnos', json_agg(json_build_object(
            'id', t.id_turno,
            'tipo', t.tipo,
            'docente', d.nome,
            'sala', t.sala,
            'dia_semana', t.dia_semana,
            'horario', json_build_object('inicio', t.hora_inicio, 'fim', t.hora_fim),
            'capacidade', t.capacidade,
            'inscritos', (SELECT COUNT(*) FROM inscricao_turno it2 WHERE it2.id_turno = t.id_turno),
            'vagas_disponiveis', t.capacidade - (SELECT COUNT(*) FROM inscricao_turno it2 WHERE it2.id_turno = t.id_turno)
        ))
    )
    INTO v_resultado
    FROM unidade_curricular uc
    LEFT JOIN turno t ON uc.id_unidadecurricular = t.id_unidadecurricular
    LEFT JOIN docente d ON t.id_docente = d.id_docente
    WHERE uc.id_unidadecurricular = p_id_uc
    GROUP BY uc.id_unidadecurricular, uc.nome, uc.sigla;
    RETURN v_resultado;
END;
$$;

-- Exportar alunos para XML
CREATE OR REPLACE FUNCTION public.exportar_alunos_xml()
RETURNS XML
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado XML;
BEGIN
    SELECT xmlelement(name "alunos",
        xmlagg(
            xmlelement(name "aluno",
                xmlelement(name "n_mecanografico", a.n_mecanografico),
                xmlelement(name "nome", a.nome),
                xmlelement(name "email", a.email),
                xmlelement(name "curso", xmlelement(name "id", c.id_curso), xmlelement(name "nome", c.nome)),
                xmlelement(name "ano_curricular", xmlelement(name "id", ac.id_anocurricular), xmlelement(name "ano", ac.ano_curricular))
            )
        )
    )
    INTO v_resultado
    FROM aluno a
    JOIN curso c ON a.id_curso = c.id_curso
    JOIN ano_curricular ac ON a.id_anocurricular = ac.id_anocurricular
    ORDER BY a.nome;
    RETURN v_resultado;
END;
$$;

-- Exportar turnos de uma UC para XML
CREATE OR REPLACE FUNCTION public.exportar_turnos_uc_xml(p_id_uc INTEGER)
RETURNS XML
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado XML;
BEGIN
    SELECT xmlelement(name "unidade_curricular",
        xmlattributes(uc.id_unidadecurricular AS "id"),
        xmlelement(name "nome", uc.nome),
        xmlelement(name "sigla", uc.sigla),
        xmlelement(name "turnos",
            xmlagg(
                xmlelement(name "turno",
                    xmlattributes(t.id_turno AS "id"),
                    xmlelement(name "tipo", t.tipo),
                    xmlelement(name "docente", d.nome),
                    xmlelement(name "sala", t.sala),
                    xmlelement(name "dia_semana", t.dia_semana),
                    xmlelement(name "horario", xmlelement(name "inicio", t.hora_inicio), xmlelement(name "fim", t.hora_fim)),
                    xmlelement(name "capacidade", t.capacidade),
                    xmlelement(name "inscritos", (SELECT COUNT(*) FROM inscricao_turno it2 WHERE it2.id_turno = t.id_turno))
                )
            )
        )
    )
    INTO v_resultado
    FROM unidade_curricular uc
    LEFT JOIN turno t ON uc.id_unidadecurricular = t.id_unidadecurricular
    LEFT JOIN docente d ON t.id_docente = d.id_docente
    WHERE uc.id_unidadecurricular = p_id_uc
    GROUP BY uc.id_unidadecurricular, uc.nome, uc.sigla;
    RETURN v_resultado;
END;
$$;

-- ============================================================================
-- FUNÇÕES PARA EXPORTAÇÃO DO ADMIN PANEL (export_views.py)
-- ============================================================================

-- Função para exportar alunos com todas as informações
CREATE OR REPLACE FUNCTION fn_export_alunos()
RETURNS TABLE(n_mecanografico INTEGER, nome TEXT, email TEXT, curso TEXT, ano_curricular TEXT)
LANGUAGE sql
AS $$
    SELECT a.n_mecanografico, a.nome, a.email,
           c.nome AS curso,
           ac.ano_curricular
    FROM aluno a
    LEFT JOIN curso c ON a.id_curso = c.id_curso
    LEFT JOIN ano_curricular ac ON a.id_anocurricular = ac.id_anocurricular
    ORDER BY a.nome;
$$;

-- Função para exportar turnos com UCs
CREATE OR REPLACE FUNCTION fn_export_turnos()
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, tipo TEXT, capacidade INTEGER, uc_nome TEXT, hora_inicio TIME, hora_fim TIME)
LANGUAGE sql
AS $$
    SELECT t.id_turno, t.n_turno, t.tipo, t.capacidade,
           uc.nome AS uc_nome,
           tuc.hora_inicio, tuc.hora_fim
    FROM turno t
    LEFT JOIN turno_uc tuc ON t.id_turno = tuc.id_turno
    LEFT JOIN unidade_curricular uc ON tuc.id_unidadecurricular = uc.id_unidadecurricular
    ORDER BY t.id_turno;
$$;

-- Função para exportar inscrições
CREATE OR REPLACE FUNCTION fn_export_inscricoes()
RETURNS TABLE(id_inscricao INTEGER, data_inscricao DATE, n_mecanografico INTEGER, aluno_nome TEXT, uc_nome TEXT, turno_numero TEXT, turno_tipo TEXT)
LANGUAGE sql
AS $$
    SELECT it.id_inscricao, it.data_inscricao,
           a.n_mecanografico, a.nome AS aluno_nome,
           uc.nome AS uc_nome,
           t.n_turno, t.tipo
    FROM inscricao_turno it
    LEFT JOIN aluno a ON it.n_mecanografico = a.n_mecanografico
    LEFT JOIN turno t ON it.id_turno = t.id_turno
    LEFT JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
    ORDER BY it.id_inscricao;
$$;

-- Função para exportar UCs
CREATE OR REPLACE FUNCTION fn_export_ucs()
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, ects NUMERIC, curso TEXT, ano_curricular TEXT, semestre TEXT)
LANGUAGE sql
AS $$
    SELECT uc.id_unidadecurricular, uc.nome, uc.ects,
           c.nome AS curso,
           ac.ano_curricular,
           s.semestre
    FROM unidade_curricular uc
    LEFT JOIN curso c ON uc.id_curso = c.id_curso
    LEFT JOIN ano_curricular ac ON uc.id_anocurricular = ac.id_anocurricular
    LEFT JOIN semestre s ON uc.id_semestre = s.id_semestre
    ORDER BY uc.id_unidadecurricular;
$$;

-- Função para exportar estatísticas de turnos
CREATE OR REPLACE FUNCTION fn_export_mv_estatisticas_turno()
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, tipo TEXT, capacidade INTEGER, uc_nome TEXT, curso_nome TEXT, ano_curricular TEXT, total_inscritos BIGINT, vagas_disponiveis BIGINT, taxa_ocupacao_percent NUMERIC, turno_cheio BOOLEAN, hora_inicio TIME, hora_fim TIME)
LANGUAGE sql
AS $$
    SELECT id_turno, n_turno, tipo, capacidade, uc_nome, curso_nome,
           ano_curricular, total_inscritos, vagas_disponiveis,
           taxa_ocupacao_percent, turno_cheio, hora_inicio, hora_fim
    FROM mv_estatisticas_turno
    ORDER BY id_turno;
$$;

-- Função para exportar UCs mais procuradas
CREATE OR REPLACE FUNCTION fn_export_mv_ucs_procuradas()
RETURNS TABLE(id_unidadecurricular INTEGER, uc_nome TEXT, ects NUMERIC, curso_nome TEXT, ano_curricular TEXT, semestre TEXT, total_alunos_inscritos BIGINT, total_turnos_com_inscricoes BIGINT, total_inscricoes BIGINT, capacidade_total_turnos BIGINT, taxa_preenchimento_global_percent NUMERIC)
LANGUAGE sql
AS $$
    SELECT id_unidadecurricular, uc_nome, ects, curso_nome, ano_curricular,
           semestre, total_alunos_inscritos, total_turnos_com_inscricoes,
           total_inscricoes, capacidade_total_turnos, taxa_preenchimento_global_percent
    FROM mv_ucs_mais_procuradas
    ORDER BY total_inscricoes DESC;
$$;

-- Função para exportar resumo de inscrições de alunos
CREATE OR REPLACE FUNCTION fn_export_mv_resumo_alunos()
RETURNS TABLE(n_mecanografico INTEGER, aluno_nome TEXT, aluno_email TEXT, curso_nome TEXT, ano_curricular TEXT, total_ucs_inscritas BIGINT, total_turnos_inscritos BIGINT, total_ects NUMERIC, primeira_inscricao DATE, ultima_inscricao DATE, dias_com_atividade BIGINT)
LANGUAGE sql
AS $$
    SELECT n_mecanografico, aluno_nome, aluno_email, curso_nome,
           ano_curricular, total_ucs_inscritas, total_turnos_inscritos,
           total_ects, primeira_inscricao, ultima_inscricao, dias_com_atividade
    FROM mv_resumo_inscricoes_aluno
    ORDER BY aluno_nome;
$$;
