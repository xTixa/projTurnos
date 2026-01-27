-- ============================================================================
-- FUNÇÕES DE CONSULTA E UTILITÁRIOS
-- ============================================================================

-- Estatísticas de um turno
CREATE OR REPLACE FUNCTION public.obter_estatisticas_turno(p_id_turno INTEGER)
RETURNS TABLE(
    id_turno INTEGER,
    tipo_turno VARCHAR,
    docente_nome VARCHAR,
    capacidade INTEGER,
    inscritos INTEGER,
    vagas_disponiveis INTEGER,
    percentagem_ocupacao NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id_turno,
        t.tipo,
        d.nome,
        t.capacidade,
        COUNT(it.n_mecanografico)::INTEGER AS inscritos,
        (t.capacidade - COUNT(it.n_mecanografico))::INTEGER AS vagas_disponiveis,
        ROUND((COUNT(it.n_mecanografico)::NUMERIC / t.capacidade * 100), 2) AS percentagem_ocupacao
    FROM turno t
    JOIN docente d ON t.id_docente = d.id_docente
    LEFT JOIN inscricao_turno it ON t.id_turno = it.id_turno
    WHERE t.id_turno = p_id_turno
    GROUP BY t.id_turno, t.tipo, d.nome, t.capacidade;
END;
$$;

-- Listar turnos de uma UC
CREATE OR REPLACE FUNCTION public.listar_turnos_uc(p_id_uc INTEGER)
RETURNS TABLE(
    id_turno INTEGER,
    tipo VARCHAR,
    docente VARCHAR,
    sala VARCHAR,
    dia_semana VARCHAR,
    horario VARCHAR,
    capacidade INTEGER,
    inscritos BIGINT,
    vagas_disponiveis INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id_turno,
        t.tipo,
        d.nome,
        t.sala,
        t.dia_semana,
        CONCAT(t.hora_inicio::TEXT, ' - ', t.hora_fim::TEXT) AS horario,
        t.capacidade,
        COUNT(it.n_mecanografico) AS inscritos,
        (t.capacidade - COUNT(it.n_mecanografico))::INTEGER AS vagas_disponiveis
    FROM turno t
    JOIN docente d ON t.id_docente = d.id_docente
    LEFT JOIN inscricao_turno it ON t.id_turno = it.id_turno
    WHERE t.id_unidadecurricular = p_id_uc
    GROUP BY t.id_turno, t.tipo, d.nome, t.sala, t.dia_semana, t.hora_inicio, t.hora_fim, t.capacidade
    ORDER BY t.tipo, t.dia_semana, t.hora_inicio;
END;
$$;

-- Horário de um aluno
CREATE OR REPLACE FUNCTION public.obter_horario_aluno(p_n_mecanografico INTEGER)
RETURNS TABLE(
    dia_semana VARCHAR,
    hora_inicio TIME,
    hora_fim TIME,
    unidade_curricular VARCHAR,
    tipo_turno VARCHAR,
    sala VARCHAR,
    docente VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.dia_semana,
        t.hora_inicio,
        t.hora_fim,
        uc.nome AS unidade_curricular,
        t.tipo AS tipo_turno,
        t.sala,
        d.nome AS docente
    FROM inscricao_turno it
    JOIN turno t ON it.id_turno = t.id_turno
    JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
    JOIN docente d ON t.id_docente = d.id_docente
    WHERE it.n_mecanografico = p_n_mecanografico
    ORDER BY 
        CASE t.dia_semana
            WHEN 'Segunda-feira' THEN 1
            WHEN 'Terça-feira' THEN 2
            WHEN 'Quarta-feira' THEN 3
            WHEN 'Quinta-feira' THEN 4
            WHEN 'Sexta-feira' THEN 5
            WHEN 'Sábado' THEN 6
            ELSE 7
        END,
        t.hora_inicio;
END;
$$;

-- Verificar conflito de horário
CREATE OR REPLACE FUNCTION public.verificar_conflito_horario(
    p_n_mecanografico INTEGER,
    p_id_turno_novo INTEGER
)
RETURNS TABLE(
    tem_conflito BOOLEAN,
    mensagem TEXT,
    turnos_conflito TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_hora_inicio TIME;
    v_hora_fim TIME;
    v_conflitos TEXT[];
    v_tem_conflito BOOLEAN := FALSE;
    v_count INTEGER := 0;
BEGIN
    -- Obter horários do turno novo
    SELECT tu.hora_inicio, tu.hora_fim
    INTO v_hora_inicio, v_hora_fim
    FROM turno_uc tu
    WHERE tu.id_turno = p_id_turno_novo;

    -- Se o turno não tem horários, não há conflito
    IF v_hora_inicio IS NULL OR v_hora_fim IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Turno sem horário configurado', ARRAY[]::TEXT[];
        RETURN;
    END IF;

    -- Verificar conflitos com ANY turno já inscrito (qualquer UC)
    SELECT COUNT(*)
    INTO v_count
    FROM inscricao_turno it
    JOIN turno t ON it.id_turno = t.id_turno
    JOIN turno_uc tu ON tu.id_turno = t.id_turno
    WHERE it.n_mecanografico = p_n_mecanografico
      AND (
          (tu.hora_inicio <= v_hora_inicio AND tu.hora_fim > v_hora_inicio) OR
          (tu.hora_inicio < v_hora_fim AND tu.hora_fim >= v_hora_fim) OR
          (tu.hora_inicio >= v_hora_inicio AND tu.hora_fim <= v_hora_fim)
      );

    -- Se encontrou conflitos, agregar informações
    IF v_count > 0 THEN
        SELECT ARRAY_AGG(
            'Turno ' || t.id_turno || ' - ' || uc.nome || ' (' || 
            tu.hora_inicio::TEXT || '-' || tu.hora_fim::TEXT || ')'
        )
        INTO v_conflitos
        FROM inscricao_turno it
        JOIN turno t ON it.id_turno = t.id_turno
        JOIN turno_uc tu ON tu.id_turno = t.id_turno
        JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
        WHERE it.n_mecanografico = p_n_mecanografico
          AND (
              (tu.hora_inicio <= v_hora_inicio AND tu.hora_fim > v_hora_inicio) OR
              (tu.hora_inicio < v_hora_fim AND tu.hora_fim >= v_hora_fim) OR
              (tu.hora_inicio >= v_hora_inicio AND tu.hora_fim <= v_hora_fim)
          );
        
        RETURN QUERY SELECT TRUE, 'Conflito de horário detectado: ' || v_count::TEXT || ' turno(s) em conflito', COALESCE(v_conflitos, ARRAY[]::TEXT[]);
    ELSE
        RETURN QUERY SELECT FALSE, 'Sem conflitos de horário', ARRAY[]::TEXT[];
    END IF;
END;
$$;

-- Estatísticas gerais do sistema
CREATE OR REPLACE FUNCTION public.obter_estatisticas_sistema()
RETURNS TABLE(
    total_alunos BIGINT,
    total_docentes BIGINT,
    total_turnos BIGINT,
    total_inscricoes BIGINT,
    total_ucs BIGINT,
    media_alunos_por_turno NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM aluno),
        (SELECT COUNT(*) FROM docente),
        (SELECT COUNT(*) FROM turno),
        (SELECT COUNT(*) FROM inscricao_turno),
        (SELECT COUNT(*) FROM unidade_curricular),
        (SELECT ROUND(AVG(total), 2) FROM (
            SELECT COUNT(*) AS total FROM inscricao_turno GROUP BY id_turno
        ) sub);
END;
$$;

-- Limpar logs antigos
CREATE OR REPLACE FUNCTION public.limpar_logs_antigos(p_dias INTEGER DEFAULT 90)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_deletados INTEGER;
BEGIN
    DELETE FROM log_eventos
    WHERE data_hora < CURRENT_DATE - p_dias;

    GET DIAGNOSTICS v_deletados = ROW_COUNT;
    RETURN v_deletados;
END;
$$;

-- Backup de inscrições (JSON)
CREATE OR REPLACE FUNCTION public.backup_inscricoes()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT json_build_object(
        'data_backup', CURRENT_TIMESTAMP,
        'total_inscricoes', COUNT(*),
        'inscricoes', json_agg(json_build_object(
            'n_mecanografico', it.n_mecanografico,
            'id_turno', it.id_turno,
            'id_unidadecurricular', it.id_unidadecurricular,
            'data_inscricao', it.data_inscricao
        ))
    )
    INTO v_resultado
    FROM inscricao_turno it;

    RETURN v_resultado;
END;
$$;
