-- ============================================================================
-- FUNÇÕES DE TRIGGER E TRIGGERS
-- ============================================================================

-- Log update de aluno
CREATE OR REPLACE FUNCTION public.trg_log_aluno_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM registar_log(
        'aluno'::VARCHAR,
        'UPDATE'::VARCHAR,
        NEW.n_mecanografico::TEXT,
        'Aluno atualizado: nome ' || OLD.nome || ' -> ' || NEW.nome || ', email ' || OLD.email || ' -> ' || NEW.email || ', curso ' || OLD.id_curso || ' -> ' || NEW.id_curso
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER log_aluno_update
AFTER UPDATE ON aluno
FOR EACH ROW
EXECUTE FUNCTION public.trg_log_aluno_update();

-- Log delete de aluno
CREATE OR REPLACE FUNCTION public.trg_log_aluno_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM registar_log(
        'aluno'::VARCHAR,
        'DELETE'::VARCHAR,
        OLD.n_mecanografico::TEXT,
        'Aluno removido: nome=' || OLD.nome || ', email=' || OLD.email
    );
    RETURN OLD;
END;
$$;

CREATE TRIGGER log_aluno_delete
AFTER DELETE ON aluno
FOR EACH ROW
EXECUTE FUNCTION public.trg_log_aluno_delete();

-- Validar capacidade antes de inserir inscrição
CREATE OR REPLACE FUNCTION public.trg_validar_capacidade_turno()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_capacidade INTEGER;
    v_inscritos INTEGER;
BEGIN
    SELECT capacidade INTO v_capacidade FROM turno WHERE id_turno = NEW.id_turno;
    SELECT COUNT(*) INTO v_inscritos FROM inscricao_turno WHERE id_turno = NEW.id_turno;
    IF v_inscritos >= v_capacidade THEN
        RAISE EXCEPTION 'Turno % está cheio (capacidade: %, inscritos: %)', NEW.id_turno, v_capacidade, v_inscritos;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validar_capacidade
BEFORE INSERT ON inscricao_turno
FOR EACH ROW
EXECUTE FUNCTION public.trg_validar_capacidade_turno();

-- Log de inscrição em turno
CREATE OR REPLACE FUNCTION public.trg_log_inscricao_turno()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM registar_log(
        'inscricao_turno'::VARCHAR,
        'INSERT'::VARCHAR,
        NEW.n_mecanografico::TEXT || '-' || NEW.id_turno::TEXT,
        'Inscrição: aluno=' || NEW.n_mecanografico || ', turno=' || NEW.id_turno || ', UC=' || NEW.id_unidadecurricular || ', data=' || NEW.data_inscricao
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER log_inscricao_turno_insert
AFTER INSERT ON inscricao_turno
FOR EACH ROW
EXECUTE FUNCTION public.trg_log_inscricao_turno();

-- Validar conflito de horário antes de inserir inscrição
CREATE OR REPLACE FUNCTION public.trg_validar_conflito_horario()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_conflito RECORD;
BEGIN
    SELECT * INTO v_conflito
    FROM verificar_conflito_horario(NEW.n_mecanografico, NEW.id_turno)
    WHERE tem_conflito = TRUE
    LIMIT 1;

    IF FOUND THEN
        RAISE EXCEPTION 'Conflito de horário detectado: %', v_conflito.mensagem;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_conflito_horario
BEFORE INSERT ON inscricao_turno
FOR EACH ROW
EXECUTE FUNCTION public.trg_validar_conflito_horario();

-- Atualizar timestamp de última modificação (necessita coluna ultima_atualizacao)
CREATE OR REPLACE FUNCTION public.trg_atualizar_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.ultima_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Exemplo de ativação:
-- CREATE TRIGGER trg_turno_timestamp
-- BEFORE UPDATE ON turno
-- FOR EACH ROW
-- EXECUTE FUNCTION public.trg_atualizar_timestamp();
