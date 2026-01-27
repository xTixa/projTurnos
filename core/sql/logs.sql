-- ============================================================================
-- FUNÇÕES DE GESTÃO DE LOGS
-- ============================================================================

-- Função para listar logs com filtros opcionais
CREATE OR REPLACE FUNCTION fn_list_logs(
    p_operacao_filter TEXT DEFAULT NULL,
    p_entidade_filter TEXT DEFAULT NULL,
    p_limite INTEGER DEFAULT 100
)
RETURNS TABLE(
    entidade TEXT,
    operacao TEXT,
    chave_primaria TEXT,
    detalhes TEXT,
    data_hora TIMESTAMP
)
LANGUAGE sql
AS $$
    SELECT entidade, operacao, chave_primaria, detalhes, data_hora
    FROM log_eventos
    WHERE (p_operacao_filter IS NULL OR operacao ILIKE ('%' || p_operacao_filter || '%'))
      AND (p_entidade_filter IS NULL OR entidade ILIKE ('%' || p_entidade_filter || '%'))
    ORDER BY data_hora DESC
    LIMIT p_limite;
$$;

-- Função para obter operações distintas
CREATE OR REPLACE FUNCTION fn_get_distinct_operacoes()
RETURNS TABLE(operacao TEXT)
LANGUAGE sql
AS $$
    SELECT DISTINCT operacao
    FROM log_eventos
    WHERE operacao IS NOT NULL AND operacao != ''
    ORDER BY operacao;
$$;

-- Função para obter entidades distintas
CREATE OR REPLACE FUNCTION fn_get_distinct_entidades()
RETURNS TABLE(entidade TEXT)
LANGUAGE sql
AS $$
    SELECT DISTINCT entidade
    FROM log_eventos
    WHERE entidade IS NOT NULL AND entidade != ''
    ORDER BY entidade;
$$;
