-- ==========================================
-- COMANDOS SQL ÚTEIS - Vistas Materializadas
-- ==========================================

-- VERIFICAR VISTAS EXISTENTES
-- ==========================================
SELECT 
    schemaname,
    matviewname AS nome_vista,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) AS tamanho,
    hasindexes AS tem_indices
FROM pg_matviews 
WHERE schemaname = 'public'
ORDER BY matviewname;


-- ATUALIZAR TODAS AS VISTAS
-- ==========================================
-- Comando único para atualizar tudo
SELECT refresh_all_materialized_views();

-- Ou individualmente
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estatisticas_turno;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resumo_inscricoes_aluno;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ucs_mais_procuradas;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_carga_docentes;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inscricoes_por_dia;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_conflitos_horario;


-- CONSULTAS ÚTEIS
-- ==========================================

-- Top 10 Turnos Mais Cheios
SELECT 
    uc_nome,
    n_turno,
    tipo,
    total_inscritos,
    capacidade,
    taxa_ocupacao_percent
FROM mv_estatisticas_turno
WHERE turno_cheio = true
ORDER BY taxa_ocupacao_percent DESC
LIMIT 10;


-- UCs com Baixa Procura
SELECT 
    uc_nome,
    curso_nome,
    ano_curricular,
    total_alunos_inscritos,
    taxa_preenchimento_global_percent
FROM mv_ucs_mais_procuradas
WHERE total_alunos_inscritos > 0
ORDER BY total_alunos_inscritos ASC
LIMIT 10;


-- Alunos Sem Inscrições
SELECT 
    n_mecanografico,
    aluno_nome,
    aluno_email,
    curso_nome,
    ano_curricular
FROM mv_resumo_inscricoes_aluno
WHERE total_ucs_inscritas = 0
ORDER BY aluno_nome;


-- Docentes Mais Sobrecarregados
SELECT 
    docente_nome,
    total_ucs,
    total_ects_lecionados,
    total_alunos_distintos,
    total_turnos
FROM mv_carga_docentes
ORDER BY total_ucs DESC, total_ects_lecionados DESC
LIMIT 10;


-- Dias com Mais Inscrições
SELECT 
    data,
    nome_dia_semana,
    total_inscricoes,
    alunos_distintos,
    ucs_distintas
FROM mv_inscricoes_por_dia
ORDER BY total_inscricoes DESC
LIMIT 10;


-- Alunos com Conflitos de Horário
SELECT 
    n_mecanografico,
    aluno_nome,
    COUNT(*) AS total_conflitos
FROM mv_conflitos_horario
GROUP BY n_mecanografico, aluno_nome
ORDER BY total_conflitos DESC;


-- ESTATÍSTICAS GERAIS
-- ==========================================

-- Resumo Geral do Sistema
SELECT 
    'Turnos Cadastrados' AS metrica,
    COUNT(*) AS valor
FROM mv_estatisticas_turno
UNION ALL
SELECT 
    'Turnos Cheios',
    COUNT(*)
FROM mv_estatisticas_turno
WHERE turno_cheio = true
UNION ALL
SELECT 
    'Taxa Média de Ocupação (%)',
    ROUND(AVG(taxa_ocupacao_percent), 2)
FROM mv_estatisticas_turno
UNION ALL
SELECT 
    'Total de Alunos',
    COUNT(*)
FROM mv_resumo_inscricoes_aluno
UNION ALL
SELECT 
    'Alunos com Conflitos',
    COUNT(DISTINCT n_mecanografico)
FROM mv_conflitos_horario
UNION ALL
SELECT 
    'Total de Docentes',
    COUNT(*)
FROM mv_carga_docentes;


-- Distribuição de Ocupação
SELECT 
    CASE 
        WHEN taxa_ocupacao_percent < 25 THEN '0-25%'
        WHEN taxa_ocupacao_percent < 50 THEN '25-50%'
        WHEN taxa_ocupacao_percent < 75 THEN '50-75%'
        ELSE '75-100%'
    END AS faixa_ocupacao,
    COUNT(*) AS total_turnos,
    ROUND(AVG(taxa_ocupacao_percent), 2) AS media_faixa
FROM mv_estatisticas_turno
GROUP BY faixa_ocupacao
ORDER BY faixa_ocupacao;


-- ANÁLISES AVANÇADAS
-- ==========================================

-- UCs com Maior Demanda vs Capacidade
SELECT 
    u.uc_nome,
    u.total_alunos_inscritos AS demanda,
    u.capacidade_total_turnos AS capacidade,
    (u.total_alunos_inscritos - u.capacidade_total_turnos) AS deficit_vagas,
    u.taxa_preenchimento_global_percent
FROM mv_ucs_mais_procuradas u
WHERE u.total_alunos_inscritos > u.capacidade_total_turnos
ORDER BY (u.total_alunos_inscritos - u.capacidade_total_turnos) DESC;


-- Comparação de Carga entre Docentes
WITH stats AS (
    SELECT 
        AVG(total_ucs) AS media_ucs,
        STDDEV(total_ucs) AS desvio_ucs
    FROM mv_carga_docentes
)
SELECT 
    d.docente_nome,
    d.total_ucs,
    CASE 
        WHEN d.total_ucs > (s.media_ucs + s.desvio_ucs) THEN 'Acima da Média'
        WHEN d.total_ucs < (s.media_ucs - s.desvio_ucs) THEN 'Abaixo da Média'
        ELSE 'Normal'
    END AS classificacao
FROM mv_carga_docentes d
CROSS JOIN stats s
ORDER BY d.total_ucs DESC;


-- Tendência Temporal de Inscrições
SELECT 
    EXTRACT(WEEK FROM data) AS semana,
    SUM(total_inscricoes) AS inscricoes_semana,
    AVG(total_inscricoes) AS media_diaria
FROM mv_inscricoes_por_dia
GROUP BY EXTRACT(WEEK FROM data)
ORDER BY semana;


-- MANUTENÇÃO E ADMINISTRAÇÃO
-- ==========================================

-- Verificar Tamanho das Vistas
SELECT 
    matviewname,
    pg_size_pretty(pg_total_relation_size('public.' || matviewname)) AS tamanho_total,
    pg_size_pretty(pg_relation_size('public.' || matviewname)) AS tamanho_dados,
    pg_size_pretty(pg_indexes_size('public.' || matviewname)) AS tamanho_indices
FROM pg_matviews 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.' || matviewname) DESC;


-- Ver Última Atualização (requer extensão)
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT 
    matviewname,
    last_refresh
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
  AND relname LIKE 'mv_%';


-- Analisar Performance das Vistas
ANALYZE mv_estatisticas_turno;
ANALYZE mv_resumo_inscricoes_aluno;
ANALYZE mv_ucs_mais_procuradas;
ANALYZE mv_carga_docentes;
ANALYZE mv_inscricoes_por_dia;
ANALYZE mv_conflitos_horario;


-- RECRIAR ÍNDICES (se necessário)
-- ==========================================
REINDEX TABLE mv_estatisticas_turno;
REINDEX TABLE mv_resumo_inscricoes_aluno;
REINDEX TABLE mv_ucs_mais_procuradas;
REINDEX TABLE mv_carga_docentes;
REINDEX TABLE mv_inscricoes_por_dia;
REINDEX TABLE mv_conflitos_horario;


-- EXPORTAÇÃO DIRETA EM SQL
-- ==========================================

-- Exportar para CSV (via psql)
\copy (SELECT * FROM mv_estatisticas_turno) TO 'estatisticas_turnos.csv' CSV HEADER;
\copy (SELECT * FROM mv_ucs_mais_procuradas) TO 'ucs_procuradas.csv' CSV HEADER;
\copy (SELECT * FROM mv_resumo_inscricoes_aluno) TO 'resumo_alunos.csv' CSV HEADER;


-- LIMPEZA (CUIDADO!)
-- ==========================================
-- Apenas se precisar recriar tudo do zero

-- DROP MATERIALIZED VIEW IF EXISTS mv_conflitos_horario CASCADE;
-- DROP MATERIALIZED VIEW IF EXISTS mv_inscricoes_por_dia CASCADE;
-- DROP MATERIALIZED VIEW IF EXISTS mv_carga_docentes CASCADE;
-- DROP MATERIALIZED VIEW IF EXISTS mv_ucs_mais_procuradas CASCADE;
-- DROP MATERIALIZED VIEW IF EXISTS mv_resumo_inscricoes_aluno CASCADE;
-- DROP MATERIALIZED VIEW IF EXISTS mv_estatisticas_turno CASCADE;


-- BACKUP E RESTORE
-- ==========================================

-- Backup de uma vista específica
-- pg_dump -h host -U user -d database -t mv_estatisticas_turno > backup_vista.sql

-- Restore
-- psql -h host -U user -d database < backup_vista.sql


-- MONITORIZAÇÃO
-- ==========================================

-- Queries ativas nas vistas
SELECT 
    pid,
    usename,
    query,
    state,
    query_start
FROM pg_stat_activity
WHERE query LIKE '%mv_%'
  AND state = 'active';


-- Locks nas vistas
SELECT 
    l.relation::regclass AS tabela,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.relation::regclass::text LIKE 'mv_%';


-- ==========================================
-- QUERIES PARA RELATÓRIOS
-- ==========================================

-- Relatório Completo de Ocupação por Curso
SELECT 
    curso_nome,
    ano_curricular,
    COUNT(*) AS total_turnos,
    SUM(total_inscritos) AS total_alunos,
    SUM(capacidade) AS capacidade_total,
    ROUND(AVG(taxa_ocupacao_percent), 2) AS taxa_media_ocupacao
FROM mv_estatisticas_turno
GROUP BY curso_nome, ano_curricular
ORDER BY curso_nome, ano_curricular;


-- Relatório de Performance por Semestre
SELECT 
    semestre,
    COUNT(*) AS total_ucs,
    SUM(total_alunos_inscritos) AS total_inscricoes,
    ROUND(AVG(taxa_preenchimento_global_percent), 2) AS taxa_media
FROM mv_ucs_mais_procuradas
GROUP BY semestre
ORDER BY semestre;


-- Relatório de Atividade dos Alunos
SELECT 
    curso_nome,
    ano_curricular,
    COUNT(*) AS total_alunos,
    ROUND(AVG(total_ucs_inscritas), 2) AS media_ucs,
    ROUND(AVG(total_ects), 2) AS media_ects
FROM mv_resumo_inscricoes_aluno
GROUP BY curso_nome, ano_curricular
ORDER BY curso_nome, ano_curricular;
