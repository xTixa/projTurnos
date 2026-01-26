-- ============================================================================
-- PROCEDURES
-- ============================================================================

-- Criar inscrição em turno
CREATE OR REPLACE PROCEDURE public.criar_inscricao_turno(
    IN p_n_mecanografico INTEGER,
    IN p_id_turno INTEGER,
    IN p_id_unidadecurricular INTEGER,
    IN p_data_inscricao DATE DEFAULT CURRENT_DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM aluno WHERE n_mecanografico = p_n_mecanografico) THEN
        RAISE EXCEPTION 'Aluno com n_mecanografico % não existe', p_n_mecanografico;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM turno WHERE id_turno = p_id_turno) THEN
        RAISE EXCEPTION 'Turno com id % não existe', p_id_turno;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM unidade_curricular WHERE id_unidadecurricular = p_id_unidadecurricular) THEN
        RAISE EXCEPTION 'Unidade curricular com id % não existe', p_id_unidadecurricular;
    END IF;

    INSERT INTO inscricao_turno (n_mecanografico, id_turno, id_unidadecurricular, data_inscricao)
    VALUES (p_n_mecanografico, p_id_turno, p_id_unidadecurricular, p_data_inscricao);

    RAISE NOTICE 'Inscrição criada com sucesso para aluno %', p_n_mecanografico;
END;
$$;

-- Remover inscrição de turno
CREATE OR REPLACE PROCEDURE public.remover_inscricao_turno(
    IN p_n_mecanografico INTEGER,
    IN p_id_turno INTEGER,
    IN p_id_unidadecurricular INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows_deleted INTEGER;
BEGIN
    DELETE FROM inscricao_turno
    WHERE n_mecanografico = p_n_mecanografico
      AND id_turno = p_id_turno
      AND id_unidadecurricular = p_id_unidadecurricular;

    GET DIAGNOSTICS v_rows_deleted = ROW_COUNT;
    IF v_rows_deleted = 0 THEN
        RAISE EXCEPTION 'Inscrição não encontrada para aluno % no turno %', p_n_mecanografico, p_id_turno;
    END IF;

    RAISE NOTICE 'Inscrição removida com sucesso';
END;
$$;

-- Criar turno
CREATE OR REPLACE PROCEDURE public.criar_turno(
    IN p_id_docente INTEGER,
    IN p_id_unidadecurricular INTEGER,
    IN p_tipo VARCHAR,
    IN p_capacidade INTEGER,
    IN p_sala VARCHAR DEFAULT NULL,
    IN p_dia_semana VARCHAR DEFAULT NULL,
    IN p_hora_inicio TIME DEFAULT NULL,
    IN p_hora_fim TIME DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM docente WHERE id_docente = p_id_docente) THEN
        RAISE EXCEPTION 'Docente com id % não existe', p_id_docente;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM unidade_curricular WHERE id_unidadecurricular = p_id_unidadecurricular) THEN
        RAISE EXCEPTION 'Unidade curricular com id % não existe', p_id_unidadecurricular;
    END IF;
    IF p_capacidade <= 0 THEN
        RAISE EXCEPTION 'Capacidade deve ser maior que zero';
    END IF;

    INSERT INTO turno (id_docente, id_unidadecurricular, tipo, capacidade, sala, dia_semana, hora_inicio, hora_fim)
    VALUES (p_id_docente, p_id_unidadecurricular, p_tipo, p_capacidade, p_sala, p_dia_semana, p_hora_inicio, p_hora_fim);

    RAISE NOTICE 'Turno criado com sucesso';
END;
$$;

-- Atualizar turno
CREATE OR REPLACE PROCEDURE public.atualizar_turno(
    IN p_id_turno INTEGER,
    IN p_id_docente INTEGER DEFAULT NULL,
    IN p_tipo VARCHAR DEFAULT NULL,
    IN p_capacidade INTEGER DEFAULT NULL,
    IN p_sala VARCHAR DEFAULT NULL,
    IN p_dia_semana VARCHAR DEFAULT NULL,
    IN p_hora_inicio TIME DEFAULT NULL,
    IN p_hora_fim TIME DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM turno WHERE id_turno = p_id_turno) THEN
        RAISE EXCEPTION 'Turno com id % não existe', p_id_turno;
    END IF;

    UPDATE turno
    SET id_docente = COALESCE(p_id_docente, id_docente),
        tipo = COALESCE(p_tipo, tipo),
        capacidade = COALESCE(p_capacidade, capacidade),
        sala = COALESCE(p_sala, sala),
        dia_semana = COALESCE(p_dia_semana, dia_semana),
        hora_inicio = COALESCE(p_hora_inicio, hora_inicio),
        hora_fim = COALESCE(p_hora_fim, hora_fim)
    WHERE id_turno = p_id_turno;

    RAISE NOTICE 'Turno atualizado com sucesso';
END;
$$;

-- Apagar turno
CREATE OR REPLACE PROCEDURE public.apagar_turno(
    IN p_id_turno INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM turno WHERE id_turno = p_id_turno) THEN
        RAISE EXCEPTION 'Turno com id % não existe', p_id_turno;
    END IF;
    IF EXISTS (SELECT 1 FROM inscricao_turno WHERE id_turno = p_id_turno) THEN
        RAISE EXCEPTION 'Não é possível apagar o turno % porque existem alunos inscritos', p_id_turno;
    END IF;

    DELETE FROM turno WHERE id_turno = p_id_turno;
    RAISE NOTICE 'Turno apagado com sucesso';
END;
$$;

-- Transferir aluno entre turnos
CREATE OR REPLACE PROCEDURE public.transferir_aluno_turno(
    IN p_n_mecanografico INTEGER,
    IN p_id_turno_origem INTEGER,
    IN p_id_turno_destino INTEGER,
    IN p_id_unidadecurricular INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_capacidade_destino INTEGER;
    v_inscritos_destino INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM inscricao_turno
        WHERE n_mecanografico = p_n_mecanografico
          AND id_turno = p_id_turno_origem
          AND id_unidadecurricular = p_id_unidadecurricular
    ) THEN
        RAISE EXCEPTION 'Aluno não está inscrito no turno de origem';
    END IF;

    SELECT capacidade INTO v_capacidade_destino
    FROM turno WHERE id_turno = p_id_turno_destino;

    SELECT COUNT(*) INTO v_inscritos_destino
    FROM inscricao_turno WHERE id_turno = p_id_turno_destino;

    IF v_inscritos_destino >= v_capacidade_destino THEN
        RAISE EXCEPTION 'Turno de destino está cheio (capacidade: %, inscritos: %)', v_capacidade_destino, v_inscritos_destino;
    END IF;

    UPDATE inscricao_turno
    SET id_turno = p_id_turno_destino,
        data_inscricao = CURRENT_DATE
    WHERE n_mecanografico = p_n_mecanografico
      AND id_turno = p_id_turno_origem
      AND id_unidadecurricular = p_id_unidadecurricular;

    RAISE NOTICE 'Aluno transferido com sucesso do turno % para o turno %', p_id_turno_origem, p_id_turno_destino;
END;
$$;
