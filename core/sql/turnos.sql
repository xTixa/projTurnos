-- ============================================================================
-- FUNÇÕES DE GESTÃO DE TURNOS E INSCRIÇÕES
-- ============================================================================

-- Função para obter aluno por número de mecanográfico
CREATE OR REPLACE FUNCTION fn_get_aluno(p_n_mecanografico INTEGER)
RETURNS TABLE(n_mecanografico INTEGER, nome TEXT, email TEXT, id_curso INTEGER, id_anocurricular INTEGER)
LANGUAGE sql
AS $$
    SELECT n_mecanografico, nome, email, id_curso, id_anocurricular
    FROM aluno
    WHERE n_mecanografico = p_n_mecanografico;
$$;

-- Função para obter turno por ID
CREATE OR REPLACE FUNCTION fn_get_turno(p_turno_id INTEGER)
RETURNS TABLE(id_turno INTEGER, n_turno TEXT, tipo TEXT, capacidade INTEGER)
LANGUAGE sql
AS $$
    SELECT id_turno, n_turno, tipo, capacidade
    FROM turno
    WHERE id_turno = p_turno_id;
$$;

-- Função para obter UC por ID
CREATE OR REPLACE FUNCTION fn_get_uc(p_uc_id INTEGER)
RETURNS TABLE(id_unidadecurricular INTEGER, nome TEXT, id_curso INTEGER, id_anocurricular INTEGER)
LANGUAGE sql
AS $$
    SELECT id_unidadecurricular, nome, id_curso, id_anocurricular
    FROM unidade_curricular
    WHERE id_unidadecurricular = p_uc_id;
$$;

-- Função para verificar se turno pertence a UC
CREATE OR REPLACE FUNCTION fn_turno_pertence_uc(p_turno_id INTEGER, p_uc_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    SELECT EXISTS(
        SELECT 1 FROM turno_uc
        WHERE id_turno = p_turno_id AND id_unidadecurricular = p_uc_id
    );
$$;

-- Função para verificar se aluno está inscrito em UC
CREATE OR REPLACE FUNCTION fn_inscrito_na_uc(p_n_mecanografico INTEGER, p_uc_id INTEGER)
RETURNS BOOLEAN
LANGUAGE sql
AS $$
    SELECT EXISTS(
        SELECT 1 FROM inscrito_uc
        WHERE n_mecanografico = p_n_mecanografico 
          AND id_unidadecurricular = p_uc_id 
          AND estado = TRUE
    );
$$;

-- Função para contar inscritos em turno/UC
CREATE OR REPLACE FUNCTION fn_count_inscritos(p_turno_id INTEGER, p_uc_id INTEGER)
RETURNS BIGINT
LANGUAGE sql
AS $$
    SELECT COUNT(*)
    FROM inscricao_turno
    WHERE id_turno = p_turno_id AND id_unidadecurricular = p_uc_id;
$$;

-- Função para listar turnos/UCs de uma UC
CREATE OR REPLACE FUNCTION fn_turno_uc_por_uc(p_uc_id INTEGER)
RETURNS TABLE(
    id_unidadecurricular INTEGER,
    id_turno INTEGER,
    n_turno TEXT,
    tipo TEXT,
    capacidade INTEGER,
    hora_inicio TIME,
    hora_fim TIME
)
LANGUAGE sql
AS $$
    SELECT tu.id_unidadecurricular, t.id_turno, t.n_turno, t.tipo, t.capacidade, tu.hora_inicio, tu.hora_fim
    FROM turno_uc tu
    JOIN turno t ON t.id_turno = tu.id_turno
    WHERE tu.id_unidadecurricular = p_uc_id
    ORDER BY t.id_turno;
$$;

-- Função para listar UCs inscritas de um aluno
CREATE OR REPLACE FUNCTION fn_ucs_inscritas_por_aluno(p_n_mecanografico INTEGER)
RETURNS TABLE(
    id_unidadecurricular INTEGER,
    nome TEXT,
    id_curso INTEGER,
    id_anocurricular INTEGER
)
LANGUAGE sql
AS $$
    SELECT iu.id_unidadecurricular, uc.nome, uc.id_curso, uc.id_anocurricular
    FROM inscrito_uc iu
    JOIN unidade_curricular uc ON uc.id_unidadecurricular = iu.id_unidadecurricular
    WHERE iu.n_mecanografico = p_n_mecanografico AND iu.estado = TRUE
    ORDER BY uc.nome;
$$;

-- Função para listar inscrições em turnos de um aluno
CREATE OR REPLACE FUNCTION fn_inscricoes_turno_por_aluno(p_n_mecanografico INTEGER)
RETURNS TABLE(
    id_turno INTEGER,
    id_unidadecurricular INTEGER,
    hora_inicio TIME,
    hora_fim TIME,
    uc_nome TEXT,
    turno_tipo TEXT,
    turno_numero TEXT
)
LANGUAGE sql
AS $$
    SELECT it.id_turno,
           it.id_unidadecurricular,
           tu.hora_inicio,
           tu.hora_fim,
           uc.nome AS uc_nome,
           t.tipo AS turno_tipo,
           t.n_turno AS turno_numero
    FROM inscricao_turno it
    LEFT JOIN turno_uc tu ON tu.id_turno = it.id_turno
    LEFT JOIN unidade_curricular uc ON uc.id_unidadecurricular = it.id_unidadecurricular
    LEFT JOIN turno t ON t.id_turno = it.id_turno
    WHERE it.n_mecanografico = p_n_mecanografico;
$$;

-- Função para listar turno_uc de um turno
CREATE OR REPLACE FUNCTION fn_turno_uc_por_turno(p_turno_id INTEGER)
RETURNS TABLE(
    id_turno INTEGER,
    id_unidadecurricular INTEGER,
    hora_inicio TIME,
    hora_fim TIME
)
LANGUAGE sql
AS $$
    SELECT id_turno, id_unidadecurricular, hora_inicio, hora_fim
    FROM turno_uc
    WHERE id_turno = p_turno_id;
$$;

-- Função para criar inscrição em turno
CREATE OR REPLACE FUNCTION fn_create_inscricao_turno(
    p_n_mecanografico INTEGER,
    p_turno_id INTEGER,
    p_uc_id INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO inscricao_turno (n_mecanografico, id_turno, id_unidadecurricular, data_inscricao)
    VALUES (p_n_mecanografico, p_turno_id, p_uc_id, CURRENT_DATE);
    RETURN TRUE;
EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$;

-- Função para deletar inscrição em turno (com ou sem UC)
CREATE OR REPLACE FUNCTION fn_delete_inscricao_turno(
    p_n_mecanografico INTEGER,
    p_turno_id INTEGER,
    p_uc_id INTEGER DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    IF p_uc_id IS NOT NULL THEN
        DELETE FROM inscricao_turno
        WHERE n_mecanografico = p_n_mecanografico 
          AND id_turno = p_turno_id 
          AND id_unidadecurricular = p_uc_id;
    ELSE
        DELETE FROM inscricao_turno
        WHERE n_mecanografico = p_n_mecanografico 
          AND id_turno = p_turno_id;
    END IF;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$;
