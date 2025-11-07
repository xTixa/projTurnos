-- ========================================
-- SQL Setup Script para Base de Dados de Teste
-- Base: test_neondb
-- Gerado: 2025-11-06
-- ========================================

-- ========================================
-- TABELAS BASE (sem dependências)
-- ========================================

-- Table: ano_curricular
CREATE TABLE IF NOT EXISTS public.ano_curricular
(
    id_anocurricular SERIAL PRIMARY KEY,
    ano_curricular VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ano_curricular_pk
    ON public.ano_curricular USING btree (id_anocurricular ASC NULLS LAST);

-- Table: ano_letivo
CREATE TABLE IF NOT EXISTS public.ano_letivo
(
    id_anoletivo SERIAL PRIMARY KEY,
    anoletivo VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ano_letivo_pk
    ON public.ano_letivo USING btree (id_anoletivo ASC NULLS LAST);

-- Table: curso
CREATE TABLE IF NOT EXISTS public.curso
(
    id_curso SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    grau VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS curso_pk
    ON public.curso USING btree (id_curso ASC NULLS LAST);

-- Table: docente
CREATE TABLE IF NOT EXISTS public.docente
(
    id_docente SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cargo VARCHAR NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS docente_pk
    ON public.docente USING btree (id_docente ASC NULLS LAST);

-- Table: semestre
CREATE TABLE IF NOT EXISTS public.semestre
(
    id_semestre SERIAL PRIMARY KEY,
    semestre VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS semestre_pk
    ON public.semestre USING btree (id_semestre ASC NULLS LAST);

-- Table: turno
CREATE TABLE IF NOT EXISTS public.turno
(
    id_turno SERIAL PRIMARY KEY,
    n_turno INTEGER NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    capacidade INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS turno_pk
    ON public.turno USING btree (id_turno ASC NULLS LAST);

-- ========================================
-- TABELAS COM DEPENDÊNCIAS
-- ========================================

-- Table: aluno
CREATE TABLE IF NOT EXISTS public.aluno
(
    n_mecanografico INTEGER PRIMARY KEY,
    id_curso INTEGER NOT NULL,
    id_anocurricular INTEGER NOT NULL,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    CONSTRAINT fk_aluno_esta_ano_curr FOREIGN KEY (id_anocurricular)
        REFERENCES public.ano_curricular (id_anocurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_aluno_pertence_curso FOREIGN KEY (id_curso)
        REFERENCES public.curso (id_curso) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS aluno_pk
    ON public.aluno USING btree (n_mecanografico ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS esta_fk
    ON public.aluno USING btree (id_anocurricular ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS pertence_fk
    ON public.aluno USING btree (id_curso ASC NULLS LAST);

-- Table: horario
CREATE TABLE IF NOT EXISTS public.horario
(
    id_horario SERIAL PRIMARY KEY,
    id_anoletivo INTEGER,
    id_semestre INTEGER NOT NULL,
    horario VARCHAR(255) NOT NULL,
    CONSTRAINT fk_horario_esta_cont_semestre FOREIGN KEY (id_semestre)
        REFERENCES public.semestre (id_semestre) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_horario_possui_ano_leti FOREIGN KEY (id_anoletivo)
        REFERENCES public.ano_letivo (id_anoletivo) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS horario_pk
    ON public.horario USING btree (id_horario ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS esta_contido_fk
    ON public.horario USING btree (id_semestre ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS possui_fk
    ON public.horario USING btree (id_anoletivo ASC NULLS LAST);

-- Table: matricula
CREATE TABLE IF NOT EXISTS public.matricula
(
    id_matricula SERIAL PRIMARY KEY,
    id_anoletivo INTEGER NOT NULL,
    n_mecanografico INTEGER NOT NULL,
    data_matricula DATE NOT NULL,
    estado VARCHAR(255) NOT NULL,
    CONSTRAINT fk_matricul_feita_no_ano_leti FOREIGN KEY (id_anoletivo)
        REFERENCES public.ano_letivo (id_anoletivo) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_matricul_tem_aluno FOREIGN KEY (n_mecanografico)
        REFERENCES public.aluno (n_mecanografico) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS matricula_pk
    ON public.matricula USING btree (id_matricula ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS feita_no_fk
    ON public.matricula USING btree (id_anoletivo ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS tem_fk
    ON public.matricula USING btree (n_mecanografico ASC NULLS LAST);

-- Table: unidade_curricular
CREATE TABLE IF NOT EXISTS public.unidade_curricular
(
    id_unidadecurricular SERIAL PRIMARY KEY,
    id_semestre INTEGER NOT NULL,
    id_anocurricular INTEGER NOT NULL,
    ects INTEGER NOT NULL,
    nome VARCHAR(255) NOT NULL,
    CONSTRAINT fk_unidade__do_semestre FOREIGN KEY (id_semestre)
        REFERENCES public.semestre (id_semestre) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_unidade__relations_ano_curr FOREIGN KEY (id_anocurricular)
        REFERENCES public.ano_curricular (id_anocurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS unidade_curricular_pk
    ON public.unidade_curricular USING btree (id_unidadecurricular ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS do_fk
    ON public.unidade_curricular USING btree (id_semestre ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS relationship_6_fk
    ON public.unidade_curricular USING btree (id_anocurricular ASC NULLS LAST);

-- Table: turno_uc
CREATE TABLE IF NOT EXISTS public.turno_uc
(
    id_turno INTEGER NOT NULL,
    id_unidadecurricular INTEGER NOT NULL,
    CONSTRAINT pk_turno_uc PRIMARY KEY (id_turno, id_unidadecurricular),
    CONSTRAINT fk_turno_uc_turno_uc2_unidade_ FOREIGN KEY (id_unidadecurricular)
        REFERENCES public.unidade_curricular (id_unidadecurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_turno_uc_turno_uc_turno FOREIGN KEY (id_turno)
        REFERENCES public.turno (id_turno) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS relationship_7_fk
    ON public.turno_uc USING btree (id_turno ASC NULLS LAST);
CREATE UNIQUE INDEX IF NOT EXISTS relationship_7_pk
    ON public.turno_uc USING btree (id_turno ASC NULLS LAST, id_unidadecurricular ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS relationship_8_fk
    ON public.turno_uc USING btree (id_unidadecurricular ASC NULLS LAST);

-- Table: inscricao_turno
CREATE TABLE IF NOT EXISTS public.inscricao_turno
(
    id_inscricao SERIAL PRIMARY KEY,
    n_mecanografico INTEGER NOT NULL,
    id_turno INTEGER,
    id_unidadecurricular INTEGER,
    data_inscricao DATE NOT NULL,
    CONSTRAINT fk_inscrica_faz_aluno FOREIGN KEY (n_mecanografico)
        REFERENCES public.aluno (n_mecanografico) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_inscrica_reference_turno_uc FOREIGN KEY (id_turno, id_unidadecurricular)
        REFERENCES public.turno_uc (id_turno, id_unidadecurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS faz_fk
    ON public.inscricao_turno USING btree (n_mecanografico ASC NULLS LAST);
CREATE UNIQUE INDEX IF NOT EXISTS inscricao_turno_pk
    ON public.inscricao_turno USING btree (id_inscricao ASC NULLS LAST);

-- Table: inscrito_uc
CREATE TABLE IF NOT EXISTS public.inscrito_uc
(
    n_mecanografico INTEGER NOT NULL,
    id_unidadecurricular INTEGER NOT NULL,
    estado BOOLEAN NOT NULL,
    CONSTRAINT pk_inscrito_uc PRIMARY KEY (n_mecanografico, id_unidadecurricular),
    CONSTRAINT fk_inscrito_inscrito__aluno FOREIGN KEY (n_mecanografico)
        REFERENCES public.aluno (n_mecanografico) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_inscrito_inscrito__unidade_ FOREIGN KEY (id_unidadecurricular)
        REFERENCES public.unidade_curricular (id_unidadecurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS inscrito2_fk
    ON public.inscrito_uc USING btree (id_unidadecurricular ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS inscrito_fk
    ON public.inscrito_uc USING btree (n_mecanografico ASC NULLS LAST);
CREATE UNIQUE INDEX IF NOT EXISTS inscrito_pk
    ON public.inscrito_uc USING btree (n_mecanografico ASC NULLS LAST, id_unidadecurricular ASC NULLS LAST);

-- Table: leciona_uc
CREATE TABLE IF NOT EXISTS public.leciona_uc
(
    id_unidadecurricular INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    CONSTRAINT pk_leciona_uc PRIMARY KEY (id_unidadecurricular, id_docente),
    CONSTRAINT fk_leciona__leciona_u_docente FOREIGN KEY (id_docente)
        REFERENCES public.docente (id_docente) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_leciona__leciona_u_unidade_ FOREIGN KEY (id_unidadecurricular)
        REFERENCES public.unidade_curricular (id_unidadecurricular) MATCH SIMPLE
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS relationship_10_fk
    ON public.leciona_uc USING btree (id_docente ASC NULLS LAST);
CREATE INDEX IF NOT EXISTS relationship_9_fk
    ON public.leciona_uc USING btree (id_unidadecurricular ASC NULLS LAST);
CREATE UNIQUE INDEX IF NOT EXISTS relationship_9_pk
    ON public.leciona_uc USING btree (id_unidadecurricular ASC NULLS LAST, id_docente ASC NULLS LAST);

-- ========================================
-- PROCEDURES
-- ========================================

-- Procedure: criar_docente
CREATE OR REPLACE PROCEDURE public.criar_docente(
    IN p_nome character varying,
    IN p_email character varying,
    IN p_cargo character varying
)
LANGUAGE 'plpgsql'
AS $$
BEGIN
    IF p_nome IS NULL OR p_email IS NULL OR p_cargo IS NULL THEN
        RAISE EXCEPTION 'Nenhum dos parâmetros pode ser nulo!';
    END IF;
    IF EXISTS (SELECT 1 FROM docente WHERE email = p_email) THEN
        RAISE EXCEPTION 'Já existe um docente com este email';
    END IF;
    INSERT INTO docente (nome, email, cargo)
    VALUES (p_nome, p_email, p_cargo);
END;
$$;

ALTER PROCEDURE public.criar_docente(character varying, character varying, character varying)
    OWNER TO neondb_owner;

-- ========================================
-- FIM DO SCRIPT
-- ========================================