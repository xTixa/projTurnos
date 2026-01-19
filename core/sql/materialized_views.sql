-- ==========================================
-- VISTAS MATERIALIZADAS - Projeto BD2 Turnos
-- ==========================================
-- Este ficheiro contém as vistas materializadas para otimizar consultas frequentes
-- Execute este script na base de dados PostgreSQL após criar as tabelas base

-- Vista 1: Estatísticas de Ocupação por Turno
-- Mostra cada turno com capacidade, inscritos e taxa de ocupação
DROP MATERIALIZED VIEW IF EXISTS mv_estatisticas_turno CASCADE;

CREATE MATERIALIZED VIEW mv_estatisticas_turno AS
SELECT 
    t.id_turno,
    t.n_turno,
    t.tipo,
    t.capacidade,
    uc.id_unidadecurricular,
    uc.nome AS uc_nome,
    uc.ects,
    c.nome AS curso_nome,
    ac.ano_curricular,
    COUNT(DISTINCT it.id_inscricao) AS total_inscritos,
    t.capacidade - COUNT(DISTINCT it.id_inscricao) AS vagas_disponiveis,
    ROUND(
        (COUNT(DISTINCT it.id_inscricao)::numeric / NULLIF(t.capacidade, 0)::numeric) * 100, 
        2
    ) AS taxa_ocupacao_percent,
    CASE 
        WHEN COUNT(DISTINCT it.id_inscricao) >= t.capacidade THEN true
        ELSE false
    END AS turno_cheio,
    tu.hora_inicio,
    tu.hora_fim
FROM turno t
INNER JOIN turno_uc tu ON t.id_turno = tu.id_turno
INNER JOIN unidade_curricular uc ON tu.id_unidadecurricular = uc.id_unidadecurricular
INNER JOIN curso c ON uc.id_curso = c.id_curso
INNER JOIN ano_curricular ac ON uc.id_anocurricular = ac.id_anocurricular
LEFT JOIN inscricao_turno it ON t.id_turno = it.id_turno
GROUP BY 
    t.id_turno, t.n_turno, t.tipo, t.capacidade,
    uc.id_unidadecurricular, uc.nome, uc.ects,
    c.nome, ac.ano_curricular, tu.hora_inicio, tu.hora_fim
ORDER BY uc.nome, t.n_turno;

CREATE INDEX idx_mv_estatisticas_turno_uc ON mv_estatisticas_turno(id_unidadecurricular);
CREATE INDEX idx_mv_estatisticas_turno_cheio ON mv_estatisticas_turno(turno_cheio);
CREATE INDEX idx_mv_estatisticas_turno_ocupacao ON mv_estatisticas_turno(taxa_ocupacao_percent);

-- Vista 2: Resumo de Inscrições por Aluno
-- Mostra cada aluno com suas estatísticas de inscrição
DROP MATERIALIZED VIEW IF EXISTS mv_resumo_inscricoes_aluno CASCADE;

CREATE MATERIALIZED VIEW mv_resumo_inscricoes_aluno AS
SELECT 
    a.n_mecanografico,
    a.nome AS aluno_nome,
    a.email AS aluno_email,
    c.nome AS curso_nome,
    ac.ano_curricular,
    COUNT(DISTINCT it.id_unidadecurricular) AS total_ucs_inscritas,
    COUNT(DISTINCT it.id_turno) AS total_turnos_inscritos,
    SUM(uc.ects) AS total_ects,
    MIN(it.data_inscricao) AS primeira_inscricao,
    MAX(it.data_inscricao) AS ultima_inscricao,
    COUNT(DISTINCT DATE(it.data_inscricao)) AS dias_com_atividade
FROM aluno a
INNER JOIN curso c ON a.id_curso = c.id_curso
INNER JOIN ano_curricular ac ON a.id_anocurricular = ac.id_anocurricular
LEFT JOIN inscricao_turno it ON a.n_mecanografico = it.n_mecanografico
LEFT JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
GROUP BY 
    a.n_mecanografico, a.nome, a.email, 
    c.nome, ac.ano_curricular
ORDER BY a.nome;

CREATE INDEX idx_mv_resumo_aluno_nmec ON mv_resumo_inscricoes_aluno(n_mecanografico);
CREATE INDEX idx_mv_resumo_aluno_curso ON mv_resumo_inscricoes_aluno(curso_nome);

-- Vista 3: Unidades Curriculares Mais Procuradas
-- Top UCs por número de inscrições
DROP MATERIALIZED VIEW IF EXISTS mv_ucs_mais_procuradas CASCADE;

CREATE MATERIALIZED VIEW mv_ucs_mais_procuradas AS
SELECT 
    uc.id_unidadecurricular,
    uc.nome AS uc_nome,
    uc.ects,
    c.nome AS curso_nome,
    ac.ano_curricular,
    s.semestre,
    COUNT(DISTINCT it.n_mecanografico) AS total_alunos_inscritos,
    COUNT(DISTINCT it.id_turno) AS total_turnos_com_inscricoes,
    COUNT(DISTINCT it.id_inscricao) AS total_inscricoes,
    SUM(t.capacidade) AS capacidade_total_turnos,
    ROUND(
        (COUNT(DISTINCT it.n_mecanografico)::numeric / NULLIF(SUM(t.capacidade), 0)::numeric) * 100,
        2
    ) AS taxa_preenchimento_global_percent
FROM unidade_curricular uc
INNER JOIN curso c ON uc.id_curso = c.id_curso
INNER JOIN ano_curricular ac ON uc.id_anocurricular = ac.id_anocurricular
INNER JOIN semestre s ON uc.id_semestre = s.id_semestre
LEFT JOIN inscricao_turno it ON uc.id_unidadecurricular = it.id_unidadecurricular
LEFT JOIN turno t ON it.id_turno = t.id_turno
GROUP BY 
    uc.id_unidadecurricular, uc.nome, uc.ects,
    c.nome, ac.ano_curricular, s.semestre
ORDER BY total_alunos_inscritos DESC, uc.nome;

CREATE INDEX idx_mv_ucs_procuradas_uc ON mv_ucs_mais_procuradas(id_unidadecurricular);
CREATE INDEX idx_mv_ucs_procuradas_total ON mv_ucs_mais_procuradas(total_alunos_inscritos);

-- Vista 4: Docentes e Carga Horária
-- Estatísticas de carga de trabalho por docente
DROP MATERIALIZED VIEW IF EXISTS mv_carga_docentes CASCADE;

CREATE MATERIALIZED VIEW mv_carga_docentes AS
SELECT 
    d.id_docente,
    d.nome AS docente_nome,
    d.email AS docente_email,
    COUNT(DISTINCT luc.id_unidadecurricular) AS total_ucs,
    SUM(uc.ects) AS total_ects_lecionados,
    COUNT(DISTINCT t.id_turno) AS total_turnos,
    COUNT(DISTINCT it.n_mecanografico) AS total_alunos_distintos,
    STRING_AGG(DISTINCT uc.nome, '; ' ORDER BY uc.nome) AS ucs_lecionadas
FROM docente d
LEFT JOIN leciona_uc luc ON d.id_docente = luc.id_docente
LEFT JOIN unidade_curricular uc ON luc.id_unidadecurricular = uc.id_unidadecurricular
LEFT JOIN turno_uc tu ON uc.id_unidadecurricular = tu.id_unidadecurricular
LEFT JOIN turno t ON tu.id_turno = t.id_turno
LEFT JOIN inscricao_turno it ON t.id_turno = it.id_turno
GROUP BY 
    d.id_docente, d.nome, d.email
ORDER BY total_ucs DESC, d.nome;

CREATE INDEX idx_mv_carga_docentes_id ON mv_carga_docentes(id_docente);
CREATE INDEX idx_mv_carga_docentes_ucs ON mv_carga_docentes(total_ucs);

-- Vista 5: Histórico de Inscrições por Dia
-- Agrupa inscrições por data para análise temporal
DROP MATERIALIZED VIEW IF EXISTS mv_inscricoes_por_dia CASCADE;

CREATE MATERIALIZED VIEW mv_inscricoes_por_dia AS
SELECT 
    DATE(it.data_inscricao) AS data,
    COUNT(DISTINCT it.id_inscricao) AS total_inscricoes,
    COUNT(DISTINCT it.n_mecanografico) AS alunos_distintos,
    COUNT(DISTINCT it.id_unidadecurricular) AS ucs_distintas,
    COUNT(DISTINCT it.id_turno) AS turnos_distintos,
    EXTRACT(DOW FROM it.data_inscricao) AS dia_semana,
    EXTRACT(HOUR FROM it.data_inscricao) AS hora_pico,
    TO_CHAR(it.data_inscricao, 'Day') AS nome_dia_semana
FROM inscricao_turno it
GROUP BY DATE(it.data_inscricao), 
         EXTRACT(DOW FROM it.data_inscricao),
         EXTRACT(HOUR FROM it.data_inscricao),
         TO_CHAR(it.data_inscricao, 'Day')
ORDER BY data DESC;

CREATE INDEX idx_mv_inscricoes_dia_data ON mv_inscricoes_por_dia(data);
CREATE INDEX idx_mv_inscricoes_dia_total ON mv_inscricoes_por_dia(total_inscricoes);

-- Vista 6: Conflitos de Horário Potenciais
-- Identifica alunos inscritos em turnos com sobreposição de horário
DROP MATERIALIZED VIEW IF EXISTS mv_conflitos_horario CASCADE;

CREATE MATERIALIZED VIEW mv_conflitos_horario AS
SELECT DISTINCT
    a.n_mecanografico,
    a.nome AS aluno_nome,
    it1.id_turno AS turno1_id,
    uc1.nome AS uc1_nome,
    tu1.hora_inicio AS turno1_inicio,
    tu1.hora_fim AS turno1_fim,
    it2.id_turno AS turno2_id,
    uc2.nome AS uc2_nome,
    tu2.hora_inicio AS turno2_inicio,
    tu2.hora_fim AS turno2_fim
FROM aluno a
INNER JOIN inscricao_turno it1 ON a.n_mecanografico = it1.n_mecanografico
INNER JOIN turno_uc tu1 ON it1.id_turno = tu1.id_turno
INNER JOIN unidade_curricular uc1 ON tu1.id_unidadecurricular = uc1.id_unidadecurricular
INNER JOIN inscricao_turno it2 ON a.n_mecanografico = it2.n_mecanografico
INNER JOIN turno_uc tu2 ON it2.id_turno = tu2.id_turno
INNER JOIN unidade_curricular uc2 ON tu2.id_unidadecurricular = uc2.id_unidadecurricular
WHERE 
    it1.id_turno < it2.id_turno
    AND (
        (tu1.hora_inicio, tu1.hora_fim) OVERLAPS (tu2.hora_inicio, tu2.hora_fim)
    )
ORDER BY a.nome, turno1_id, turno2_id;

CREATE INDEX idx_mv_conflitos_aluno ON mv_conflitos_horario(n_mecanografico);

-- ==========================================
-- COMANDOS PARA ATUALIZAR AS VISTAS MATERIALIZADAS
-- ==========================================
-- Execute estes comandos periodicamente (ex: cronjob, trigger, ou manualmente)

-- Atualizar todas as vistas de uma só vez:
/*
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estatisticas_turno;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resumo_inscricoes_aluno;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ucs_mais_procuradas;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_carga_docentes;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inscricoes_por_dia;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_conflitos_horario;
*/

-- ==========================================
-- FUNÇÃO PARA ATUALIZAR AUTOMATICAMENTE
-- ==========================================
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estatisticas_turno;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resumo_inscricoes_aluno;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ucs_mais_procuradas;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_carga_docentes;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inscricoes_por_dia;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_conflitos_horario;
END;
$$ LANGUAGE plpgsql;

-- Para chamar a função:
-- SELECT refresh_all_materialized_views();
