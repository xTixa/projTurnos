--
-- PostgreSQL database dump
--

\restrict jSA7kiBeniMLqA4KdFr8HtiDmabyeR2a9owlsxM1IpacjyvFEfuNMk6cduvghuz

-- Dumped from database version 17.7 (e429a59)
-- Dumped by pg_dump version 17.6

-- Started on 2026-01-20 14:43:47

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 16486)
-- Name: neon_auth; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA neon_auth;


ALTER SCHEMA neon_auth OWNER TO neondb_owner;

--
-- TOC entry 319 (class 1255 OID 155654)
-- Name: alunos_inscritos_por_dia(date); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.alunos_inscritos_por_dia(p_data date) RETURNS TABLE(n_mecanografico integer, nome_aluno character varying, email character varying, id_unidadecurricular integer, nome_uc character varying, id_turno integer, tipo_turno character varying, data_inscricao date)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.n_mecanografico,
        a.nome,
        a.email,
        it.id_unidadecurricular,
        uc.nome,
        it.id_turno,
        t.tipo,
        it.data_inscricao
    FROM aluno a
    JOIN inscricao_turno it ON a.n_mecanografico = it.n_mecanografico
    JOIN unidade_curricular uc ON it.id_unidadecurricular = uc.id_unidadecurricular
    JOIN turno t ON it.id_turno = t.id_turno
    WHERE it.data_inscricao = p_data
    ORDER BY a.nome;
END;
$$;


ALTER FUNCTION public.alunos_inscritos_por_dia(p_data date) OWNER TO neondb_owner;

--
-- TOC entry 317 (class 1255 OID 155652)
-- Name: alunos_por_uc(integer, character varying); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.alunos_por_uc(p_id_uc integer, tipo_de_turno character varying) RETURNS TABLE(n_mecanografico integer, nome_aluno character varying, id_turno integer, tipo_turno character varying, data_inscricao date)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.n_mecanografico,
        a.nome,
        it.id_turno,
        t.tipo,
        it.data_inscricao
    FROM aluno a
    JOIN inscricao_turno it ON 
		a.n_mecanografico = it.n_mecanografico
    JOIN turno t ON 
		it.id_turno = t.id_turno
    WHERE it.id_unidadecurricular = p_id_uc AND t.tipo = tipo_de_turno
    ORDER BY a.nome;
END;
$$;


ALTER FUNCTION public.alunos_por_uc(p_id_uc integer, tipo_de_turno character varying) OWNER TO neondb_owner;

--
-- TOC entry 296 (class 1255 OID 122881)
-- Name: apagar_aluno(integer); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.apagar_aluno(IN p_n_mecanografico integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM aluno WHERE n_mecanografico = p_n_mecanografico) THEN
        RAISE EXCEPTION 'Aluno não existe';
    END IF;
    DELETE FROM aluno WHERE n_mecanografico = p_n_mecanografico;
END;
$$;


ALTER PROCEDURE public.apagar_aluno(IN p_n_mecanografico integer) OWNER TO neondb_owner;

--
-- TOC entry 295 (class 1255 OID 122880)
-- Name: apagar_docente(integer); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.apagar_docente(IN p_id_docente integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM docente WHERE id_docente = p_id_docente) THEN
        RAISE EXCEPTION 'Docente não existe';
    END IF;
    DELETE FROM docente WHERE id_docente = p_id_docente;
END;
$$;


ALTER PROCEDURE public.apagar_docente(IN p_id_docente integer) OWNER TO neondb_owner;

--
-- TOC entry 298 (class 1255 OID 122882)
-- Name: atualizar_aluno(integer, integer, integer, character varying, character varying, character varying); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.atualizar_aluno(IN p_n_mecanografico integer, IN p_id_curso integer, IN p_id_anocurricular integer, IN p_nome character varying, IN p_email character varying, IN p_password character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM aluno WHERE n_mecanografico = p_n_mecanografico) THEN
        RAISE EXCEPTION 'Aluno não existe';
    END IF;
    UPDATE aluno
    SET id_curso = COALESCE(p_id_curso, id_curso),
        id_anocurricular = COALESCE(p_id_anocurricular, id_anocurricular),
        nome = COALESCE(p_nome, nome),
        email = COALESCE(p_email, email),
        password = COALESCE(p_password, password)
    WHERE n_mecanografico = p_n_mecanografico;
END;
$$;


ALTER PROCEDURE public.atualizar_aluno(IN p_n_mecanografico integer, IN p_id_curso integer, IN p_id_anocurricular integer, IN p_nome character varying, IN p_email character varying, IN p_password character varying) OWNER TO neondb_owner;

--
-- TOC entry 299 (class 1255 OID 122883)
-- Name: atualizar_docente(integer, character varying, character varying, character varying); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.atualizar_docente(IN p_id_docente integer, IN p_nome character varying, IN p_email character varying, IN p_cargo character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM docente WHERE id_docente = p_id_docente) THEN
        RAISE EXCEPTION 'Docente não existe';
    END IF;
    UPDATE docente
    SET nome = COALESCE(p_nome, nome),
        email = COALESCE(p_email, email),
        cargo = COALESCE(p_cargo, cargo)
    WHERE id_docente = p_id_docente;
END;
$$;


ALTER PROCEDURE public.atualizar_docente(IN p_id_docente integer, IN p_nome character varying, IN p_email character varying, IN p_cargo character varying) OWNER TO neondb_owner;

--
-- TOC entry 300 (class 1255 OID 122884)
-- Name: criar_aluno(integer, integer, integer, character varying, character varying, character varying); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.criar_aluno(IN p_n_mecanografico integer, IN p_id_curso integer, IN p_id_anocurricular integer, IN p_nome character varying, IN p_email character varying, IN p_password character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_n_mecanografico IS NULL OR p_id_curso IS NULL OR p_id_anocurricular IS NULL 
       OR p_nome IS NULL OR p_email IS NULL OR p_password IS NULL THEN
        RAISE EXCEPTION 'Nenhum dos parâmetros pode ser nulo!';
    END IF;
    IF EXISTS (SELECT 1 FROM aluno WHERE n_mecanografico = p_n_mecanografico) THEN
        RAISE EXCEPTION 'Já existe um aluno com este número mecanográfico';
    END IF;
    IF EXISTS (SELECT 1 FROM aluno WHERE email = p_email) THEN
        RAISE EXCEPTION 'Já existe um aluno com este email';
    END IF;
    INSERT INTO aluno (n_mecanografico, id_curso, id_anocurricular, nome, email, password)
    VALUES (p_n_mecanografico, p_id_curso, p_id_anocurricular, p_nome, p_email, p_password);
END;
$$;


ALTER PROCEDURE public.criar_aluno(IN p_n_mecanografico integer, IN p_id_curso integer, IN p_id_anocurricular integer, IN p_nome character varying, IN p_email character varying, IN p_password character varying) OWNER TO neondb_owner;

--
-- TOC entry 294 (class 1255 OID 40960)
-- Name: criar_docente(character varying, character varying, character varying); Type: PROCEDURE; Schema: public; Owner: neondb_owner
--

CREATE PROCEDURE public.criar_docente(IN p_nome character varying, IN p_email character varying, IN p_cargo character varying)
    LANGUAGE plpgsql
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


ALTER PROCEDURE public.criar_docente(IN p_nome character varying, IN p_email character varying, IN p_cargo character varying) OWNER TO neondb_owner;

--
-- TOC entry 318 (class 1255 OID 155653)
-- Name: inserir_matricula(integer, integer, date, character varying); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.inserir_matricula(p_id_anoletivo integer, p_n_mecanografico integer, p_data_matricula date, p_estado character varying) RETURNS TABLE(mensagem character varying, sucesso boolean)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_resultado VARCHAR;
    v_sucesso BOOLEAN := FALSE;
    v_aluno_existe BOOLEAN;
BEGIN
    -- Verifica se o aluno existe
    SELECT EXISTS(SELECT 1 FROM aluno WHERE n_mecanografico = p_n_mecanografico)
    INTO v_aluno_existe;
    
    IF NOT v_aluno_existe THEN
        RETURN QUERY SELECT 'Erro: Aluno com n_mecanografico ' || p_n_mecanografico || ' não existe!', FALSE;
        RETURN;
    END IF;
    
    BEGIN
        INSERT INTO matricula (id_anoletivo, n_mecanografico, data_matricula, estado)
        VALUES (p_id_anoletivo, p_n_mecanografico, p_data_matricula, p_estado);
        
        v_resultado := 'Matrícula inserida com sucesso!';
        v_sucesso := TRUE;
    EXCEPTION WHEN OTHERS THEN
        v_resultado := 'Erro ao inserir matrícula: ' || SQLERRM;
        v_sucesso := FALSE;
    END;
    
    RETURN QUERY SELECT v_resultado, v_sucesso;
END;
$$;


ALTER FUNCTION public.inserir_matricula(p_id_anoletivo integer, p_n_mecanografico integer, p_data_matricula date, p_estado character varying) OWNER TO neondb_owner;

--
-- TOC entry 305 (class 1255 OID 163856)
-- Name: registar_log(character varying, character varying, character varying, text); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.registar_log(p_entidade character varying, p_operacao character varying, p_chave_primaria character varying, p_detalhes text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO log_eventos (entidade, operacao, chave_primaria, detalhes, utilizador_db)
    VALUES (
        p_entidade,
        p_operacao,
        p_chave_primaria,
        p_detalhes,
        current_user
    );
END;
$$;


ALTER FUNCTION public.registar_log(p_entidade character varying, p_operacao character varying, p_chave_primaria character varying, p_detalhes text) OWNER TO neondb_owner;

--
-- TOC entry 303 (class 1255 OID 163852)
-- Name: trg_log_aluno_insert(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_log_aluno_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM registar_log(
        'aluno'::VARCHAR,
        'INSERT'::VARCHAR,
        NEW.n_mecanografico::TEXT,
        'Aluno criado: nome=' || NEW.nome ||
        ', email=' || COALESCE(NEW.email, '') ||
        ', id_curso=' || NEW.id_curso::TEXT ||
        ', id_anocurricular=' || NEW.id_anocurricular::TEXT
    );
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.trg_log_aluno_insert() OWNER TO neondb_owner;

--
-- TOC entry 297 (class 1255 OID 163850)
-- Name: trg_log_docente_insert(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_log_docente_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM registar_log(
        'docente'::VARCHAR,
        'INSERT'::VARCHAR,
        NEW.id_docente::TEXT,
        'Docente criado: nome=' || NEW.nome ||
        ', email=' || COALESCE(NEW.email, '') ||
        ', cargo=' || COALESCE(NEW.cargo, '')
    );
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.trg_log_docente_insert() OWNER TO neondb_owner;

--
-- TOC entry 304 (class 1255 OID 163854)
-- Name: trg_log_matricula_insert(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_log_matricula_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM registar_log(
        'matricula'::VARCHAR,
        'INSERT'::VARCHAR,
        NEW.id_matricula::TEXT,
        'Matrícula criada: n_mecanografico=' || NEW.n_mecanografico::TEXT ||
        ', id_anoletivo=' || NEW.id_anoletivo::TEXT ||
        ', data_matricula=' || NEW.data_matricula::TEXT ||
        ', estado=' || COALESCE(NEW.estado, '')
    );
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.trg_log_matricula_insert() OWNER TO neondb_owner;

--
-- TOC entry 301 (class 1255 OID 147456)
-- Name: validar_inscricao_duplicada(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.validar_inscricao_duplicada() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inscricao_turno
        WHERE n_mecanografico = NEW.n_mecanografico
        AND id_turno = NEW.id_turno
        AND id_unidadecurricular = NEW.id_unidadecurricular
    ) THEN
        RAISE EXCEPTION 'O aluno já está inscrito neste turno nesta unidade curricular.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validar_inscricao_duplicada() OWNER TO neondb_owner;

--
-- TOC entry 302 (class 1255 OID 147458)
-- Name: validar_inscricao_uc(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.validar_inscricao_uc() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Verifica se o aluno está inscrito na UC correspondente ao turno
    IF NOT EXISTS (
        SELECT 1
        FROM inscrito_uc
        WHERE n_mecanografico = NEW.n_mecanografico
        AND id_unidadecurricular = NEW.id_unidadecurricular
        AND estado = TRUE
    ) THEN
        RAISE EXCEPTION
        'O aluno não está inscrito na unidade curricular % — inscrição no turno não permitida.',
        NEW.id_unidadecurricular;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validar_inscricao_uc() OWNER TO neondb_owner;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 16487)
-- Name: users_sync; Type: TABLE; Schema: neon_auth; Owner: neondb_owner
--

CREATE TABLE neon_auth.users_sync (
    raw_json jsonb NOT NULL,
    id text GENERATED ALWAYS AS ((raw_json ->> 'id'::text)) STORED NOT NULL,
    name text GENERATED ALWAYS AS ((raw_json ->> 'display_name'::text)) STORED,
    email text GENERATED ALWAYS AS ((raw_json ->> 'primary_email'::text)) STORED,
    created_at timestamp with time zone GENERATED ALWAYS AS (to_timestamp((trunc((((raw_json ->> 'signed_up_at_millis'::text))::bigint)::double precision) / (1000)::double precision))) STORED,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone
);


ALTER TABLE neon_auth.users_sync OWNER TO neondb_owner;

--
-- TOC entry 219 (class 1259 OID 24576)
-- Name: aluno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.aluno (
    n_mecanografico integer NOT NULL,
    id_curso integer NOT NULL,
    id_anocurricular integer NOT NULL,
    nome character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.aluno OWNER TO neondb_owner;

--
-- TOC entry 221 (class 1259 OID 24587)
-- Name: ano_curricular; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.ano_curricular (
    id_anocurricular integer NOT NULL,
    ano_curricular character varying(255) NOT NULL
);


ALTER TABLE public.ano_curricular OWNER TO neondb_owner;

--
-- TOC entry 220 (class 1259 OID 24586)
-- Name: ano_curricular_id_anocurricular_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.ano_curricular_id_anocurricular_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ano_curricular_id_anocurricular_seq OWNER TO neondb_owner;

--
-- TOC entry 3875 (class 0 OID 0)
-- Dependencies: 220
-- Name: ano_curricular_id_anocurricular_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.ano_curricular_id_anocurricular_seq OWNED BY public.ano_curricular.id_anocurricular;


--
-- TOC entry 223 (class 1259 OID 24595)
-- Name: ano_letivo; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.ano_letivo (
    id_anoletivo integer NOT NULL,
    anoletivo character varying(255) NOT NULL
);


ALTER TABLE public.ano_letivo OWNER TO neondb_owner;

--
-- TOC entry 222 (class 1259 OID 24594)
-- Name: ano_letivo_id_anoletivo_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.ano_letivo_id_anoletivo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ano_letivo_id_anoletivo_seq OWNER TO neondb_owner;

--
-- TOC entry 3878 (class 0 OID 0)
-- Dependencies: 222
-- Name: ano_letivo_id_anoletivo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.ano_letivo_id_anoletivo_seq OWNED BY public.ano_letivo.id_anoletivo;


--
-- TOC entry 287 (class 1259 OID 204801)
-- Name: auditoria_inscricao; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auditoria_inscricao (
    id_auditoria integer NOT NULL,
    data_tentativa timestamp with time zone NOT NULL,
    resultado character varying(50) NOT NULL,
    motivo_rejeicao text,
    tempo_processamento_ms integer NOT NULL,
    id_turno integer,
    id_unidadecurricular integer,
    n_mecanografico integer
);


ALTER TABLE public.auditoria_inscricao OWNER TO neondb_owner;

--
-- TOC entry 286 (class 1259 OID 204800)
-- Name: auditoria_inscricao_id_auditoria_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auditoria_inscricao ALTER COLUMN id_auditoria ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auditoria_inscricao_id_auditoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 250 (class 1259 OID 24804)
-- Name: auth_group; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO neondb_owner;

--
-- TOC entry 249 (class 1259 OID 24803)
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 252 (class 1259 OID 24812)
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO neondb_owner;

--
-- TOC entry 251 (class 1259 OID 24811)
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 248 (class 1259 OID 24798)
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO neondb_owner;

--
-- TOC entry 247 (class 1259 OID 24797)
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 254 (class 1259 OID 24818)
-- Name: auth_user; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO neondb_owner;

--
-- TOC entry 256 (class 1259 OID 24826)
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO neondb_owner;

--
-- TOC entry 255 (class 1259 OID 24825)
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 253 (class 1259 OID 24817)
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 258 (class 1259 OID 24832)
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO neondb_owner;

--
-- TOC entry 257 (class 1259 OID 24831)
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 237 (class 1259 OID 24668)
-- Name: semestre; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.semestre (
    id_semestre integer NOT NULL,
    semestre character varying(255) NOT NULL
);


ALTER TABLE public.semestre OWNER TO neondb_owner;

--
-- TOC entry 242 (class 1259 OID 24692)
-- Name: unidade_curricular; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.unidade_curricular (
    id_unidadecurricular integer NOT NULL,
    id_semestre integer NOT NULL,
    id_anocurricular integer NOT NULL,
    ects integer NOT NULL,
    nome character varying(255) NOT NULL,
    id_curso integer NOT NULL
);


ALTER TABLE public.unidade_curricular OWNER TO neondb_owner;

--
-- TOC entry 264 (class 1259 OID 98324)
-- Name: cadeirassemestre; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.cadeirassemestre AS
 SELECT uc.id_unidadecurricular,
    uc.nome,
    uc.ects,
    s.id_semestre AS semestre_id,
    s.semestre AS semestre_nome
   FROM (public.unidade_curricular uc
     JOIN public.semestre s ON ((s.id_semestre = uc.id_semestre)))
  WHERE ((s.semestre)::text = '2º semestre'::text);


ALTER VIEW public.cadeirassemestre OWNER TO neondb_owner;

--
-- TOC entry 289 (class 1259 OID 212993)
-- Name: core_avaliacaopdf; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.core_avaliacaopdf (
    id integer NOT NULL,
    nome character varying(200) DEFAULT 'Calendário de Avaliações'::character varying,
    ficheiro character varying(100),
    id_anocurricular integer,
    atualizado_em timestamp with time zone,
    id_curso integer
);


ALTER TABLE public.core_avaliacaopdf OWNER TO neondb_owner;

--
-- TOC entry 288 (class 1259 OID 212992)
-- Name: core_avaliacaopdf_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.core_avaliacaopdf_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.core_avaliacaopdf_id_seq OWNER TO neondb_owner;

--
-- TOC entry 3898 (class 0 OID 0)
-- Dependencies: 288
-- Name: core_avaliacaopdf_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.core_avaliacaopdf_id_seq OWNED BY public.core_avaliacaopdf.id;


--
-- TOC entry 271 (class 1259 OID 131073)
-- Name: core_horariopdf; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.core_horariopdf (
    id bigint NOT NULL,
    nome character varying(200) NOT NULL,
    ficheiro character varying(100) NOT NULL,
    atualizado_em timestamp with time zone NOT NULL,
    id_anocurricular integer,
    id_curso integer
);


ALTER TABLE public.core_horariopdf OWNER TO neondb_owner;

--
-- TOC entry 270 (class 1259 OID 131072)
-- Name: core_horariopdf_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.core_horariopdf ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_horariopdf_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 279 (class 1259 OID 172058)
-- Name: core_pedidotrocaturno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.core_pedidotrocaturno (
    id bigint NOT NULL,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    inscricao_contraparte_id integer,
    inscricao_solicitante_id integer NOT NULL,
    turno_desejado_id integer NOT NULL
);


ALTER TABLE public.core_pedidotrocaturno OWNER TO neondb_owner;

--
-- TOC entry 278 (class 1259 OID 172057)
-- Name: core_pedidotrocaturno_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.core_pedidotrocaturno ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_pedidotrocaturno_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 225 (class 1259 OID 24603)
-- Name: curso; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.curso (
    id_curso integer NOT NULL,
    nome character varying(255) NOT NULL,
    grau character varying(255) NOT NULL
);


ALTER TABLE public.curso OWNER TO neondb_owner;

--
-- TOC entry 224 (class 1259 OID 24602)
-- Name: curso_id_curso_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.curso_id_curso_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.curso_id_curso_seq OWNER TO neondb_owner;

--
-- TOC entry 3905 (class 0 OID 0)
-- Dependencies: 224
-- Name: curso_id_curso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.curso_id_curso_seq OWNED BY public.curso.id_curso;


--
-- TOC entry 260 (class 1259 OID 24890)
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO neondb_owner;

--
-- TOC entry 259 (class 1259 OID 24889)
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 246 (class 1259 OID 24790)
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO neondb_owner;

--
-- TOC entry 245 (class 1259 OID 24789)
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 244 (class 1259 OID 24782)
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO neondb_owner;

--
-- TOC entry 243 (class 1259 OID 24781)
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 261 (class 1259 OID 24918)
-- Name: django_session; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO neondb_owner;

--
-- TOC entry 227 (class 1259 OID 24613)
-- Name: docente; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.docente (
    id_docente integer NOT NULL,
    nome character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    cargo character varying NOT NULL
);


ALTER TABLE public.docente OWNER TO neondb_owner;

--
-- TOC entry 226 (class 1259 OID 24612)
-- Name: docente_id_docente_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.docente_id_docente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.docente_id_docente_seq OWNER TO neondb_owner;

--
-- TOC entry 3915 (class 0 OID 0)
-- Dependencies: 226
-- Name: docente_id_docente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.docente_id_docente_seq OWNED BY public.docente.id_docente;


--
-- TOC entry 281 (class 1259 OID 180225)
-- Name: forum_inscricaoturno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.forum_inscricaoturno (
    id_inscricao integer NOT NULL,
    n_mecanografico integer NOT NULL,
    id_turno_id bigint NOT NULL
);


ALTER TABLE public.forum_inscricaoturno OWNER TO neondb_owner;

--
-- TOC entry 280 (class 1259 OID 180224)
-- Name: forum_inscricaoturno_id_inscricao_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.forum_inscricaoturno ALTER COLUMN id_inscricao ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.forum_inscricaoturno_id_inscricao_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 285 (class 1259 OID 180237)
-- Name: forum_pedidotrocaturno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.forum_pedidotrocaturno (
    id bigint NOT NULL,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    inscricao_contraparte_id integer,
    inscricao_solicitante_id integer NOT NULL,
    turno_desejado_id bigint NOT NULL
);


ALTER TABLE public.forum_pedidotrocaturno OWNER TO neondb_owner;

--
-- TOC entry 284 (class 1259 OID 180236)
-- Name: forum_pedidotrocaturno_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.forum_pedidotrocaturno ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.forum_pedidotrocaturno_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 283 (class 1259 OID 180231)
-- Name: forum_turno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.forum_turno (
    id bigint NOT NULL,
    n_turno integer NOT NULL,
    tipo character varying(20) NOT NULL,
    capacidade integer NOT NULL
);


ALTER TABLE public.forum_turno OWNER TO neondb_owner;

--
-- TOC entry 282 (class 1259 OID 180230)
-- Name: forum_turno_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.forum_turno ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.forum_turno_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 229 (class 1259 OID 24623)
-- Name: horario; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.horario (
    id_horario integer NOT NULL,
    id_anoletivo integer,
    id_semestre integer NOT NULL,
    horario character varying(255) NOT NULL
);


ALTER TABLE public.horario OWNER TO neondb_owner;

--
-- TOC entry 228 (class 1259 OID 24622)
-- Name: horario_id_horario_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.horario_id_horario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.horario_id_horario_seq OWNER TO neondb_owner;

--
-- TOC entry 3924 (class 0 OID 0)
-- Dependencies: 228
-- Name: horario_id_horario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.horario_id_horario_seq OWNED BY public.horario.id_horario;


--
-- TOC entry 231 (class 1259 OID 24633)
-- Name: inscricao_turno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.inscricao_turno (
    id_inscricao integer NOT NULL,
    n_mecanografico integer NOT NULL,
    id_turno integer,
    id_unidadecurricular integer,
    data_inscricao date NOT NULL
);


ALTER TABLE public.inscricao_turno OWNER TO neondb_owner;

--
-- TOC entry 230 (class 1259 OID 24632)
-- Name: inscricao_turno_id_inscricao_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.inscricao_turno_id_inscricao_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inscricao_turno_id_inscricao_seq OWNER TO neondb_owner;

--
-- TOC entry 3927 (class 0 OID 0)
-- Dependencies: 230
-- Name: inscricao_turno_id_inscricao_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.inscricao_turno_id_inscricao_seq OWNED BY public.inscricao_turno.id_inscricao;


--
-- TOC entry 232 (class 1259 OID 24641)
-- Name: inscrito_uc; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.inscrito_uc (
    n_mecanografico integer NOT NULL,
    id_unidadecurricular integer NOT NULL,
    estado boolean NOT NULL
);


ALTER TABLE public.inscrito_uc OWNER TO neondb_owner;

--
-- TOC entry 233 (class 1259 OID 24649)
-- Name: leciona_uc; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.leciona_uc (
    id_unidadecurricular integer NOT NULL,
    id_docente integer NOT NULL
);


ALTER TABLE public.leciona_uc OWNER TO neondb_owner;

--
-- TOC entry 275 (class 1259 OID 163841)
-- Name: log_eventos; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.log_eventos (
    id_log integer NOT NULL,
    entidade character varying(50),
    operacao character varying(20),
    chave_primaria character varying(50),
    detalhes text,
    utilizador_db character varying(100),
    data_hora timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.log_eventos OWNER TO neondb_owner;

--
-- TOC entry 274 (class 1259 OID 163840)
-- Name: log_eventos_id_log_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.log_eventos_id_log_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.log_eventos_id_log_seq OWNER TO neondb_owner;

--
-- TOC entry 3932 (class 0 OID 0)
-- Dependencies: 274
-- Name: log_eventos_id_log_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.log_eventos_id_log_seq OWNED BY public.log_eventos.id_log;


--
-- TOC entry 235 (class 1259 OID 24658)
-- Name: matricula; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.matricula (
    id_matricula integer NOT NULL,
    id_anoletivo integer NOT NULL,
    n_mecanografico integer NOT NULL,
    data_matricula date NOT NULL,
    estado character varying(255) NOT NULL
);


ALTER TABLE public.matricula OWNER TO neondb_owner;

--
-- TOC entry 234 (class 1259 OID 24657)
-- Name: matricula_id_matricula_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.matricula_id_matricula_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.matricula_id_matricula_seq OWNER TO neondb_owner;

--
-- TOC entry 3935 (class 0 OID 0)
-- Dependencies: 234
-- Name: matricula_id_matricula_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.matricula_id_matricula_seq OWNED BY public.matricula.id_matricula;


--
-- TOC entry 240 (class 1259 OID 24683)
-- Name: turno_uc; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.turno_uc (
    id_turno integer NOT NULL,
    id_unidadecurricular integer NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fim time without time zone NOT NULL,
    CONSTRAINT chk_horas_validas CHECK ((hora_inicio < hora_fim))
);


ALTER TABLE public.turno_uc OWNER TO neondb_owner;

--
-- TOC entry 293 (class 1259 OID 229430)
-- Name: mv_conflitos_horario; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_conflitos_horario AS
 SELECT DISTINCT a.n_mecanografico,
    a.nome AS aluno_nome,
    it1.id_turno AS turno1_id,
    uc1.nome AS uc1_nome,
    tu1.hora_inicio AS turno1_inicio,
    tu1.hora_fim AS turno1_fim,
    it2.id_turno AS turno2_id,
    uc2.nome AS uc2_nome,
    tu2.hora_inicio AS turno2_inicio,
    tu2.hora_fim AS turno2_fim
   FROM ((((((public.aluno a
     JOIN public.inscricao_turno it1 ON ((a.n_mecanografico = it1.n_mecanografico)))
     JOIN public.turno_uc tu1 ON ((it1.id_turno = tu1.id_turno)))
     JOIN public.unidade_curricular uc1 ON ((tu1.id_unidadecurricular = uc1.id_unidadecurricular)))
     JOIN public.inscricao_turno it2 ON ((a.n_mecanografico = it2.n_mecanografico)))
     JOIN public.turno_uc tu2 ON ((it2.id_turno = tu2.id_turno)))
     JOIN public.unidade_curricular uc2 ON ((tu2.id_unidadecurricular = uc2.id_unidadecurricular)))
  WHERE ((it1.id_turno < it2.id_turno) AND ((tu1.hora_inicio, tu1.hora_fim) OVERLAPS (tu2.hora_inicio, tu2.hora_fim)))
  ORDER BY a.nome, it1.id_turno, it2.id_turno
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_conflitos_horario OWNER TO neondb_owner;

--
-- TOC entry 239 (class 1259 OID 24676)
-- Name: turno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.turno (
    id_turno integer NOT NULL,
    n_turno integer NOT NULL,
    tipo character varying(255) NOT NULL,
    capacidade integer NOT NULL
);


ALTER TABLE public.turno OWNER TO neondb_owner;

--
-- TOC entry 290 (class 1259 OID 229376)
-- Name: mv_estatisticas_turno; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_estatisticas_turno AS
 SELECT t.id_turno,
    t.n_turno,
    t.tipo,
    t.capacidade,
    uc.id_unidadecurricular,
    uc.nome AS uc_nome,
    uc.ects,
    c.nome AS curso_nome,
    ac.ano_curricular,
    count(DISTINCT it.id_inscricao) AS total_inscritos,
    (t.capacidade - count(DISTINCT it.id_inscricao)) AS vagas_disponiveis,
    round((((count(DISTINCT it.id_inscricao))::numeric / (NULLIF(t.capacidade, 0))::numeric) * (100)::numeric), 2) AS taxa_ocupacao_percent,
        CASE
            WHEN (count(DISTINCT it.id_inscricao) >= t.capacidade) THEN true
            ELSE false
        END AS turno_cheio,
    tu.hora_inicio,
    tu.hora_fim
   FROM (((((public.turno t
     JOIN public.turno_uc tu ON ((t.id_turno = tu.id_turno)))
     JOIN public.unidade_curricular uc ON ((tu.id_unidadecurricular = uc.id_unidadecurricular)))
     JOIN public.curso c ON ((uc.id_curso = c.id_curso)))
     JOIN public.ano_curricular ac ON ((uc.id_anocurricular = ac.id_anocurricular)))
     LEFT JOIN public.inscricao_turno it ON ((t.id_turno = it.id_turno)))
  GROUP BY t.id_turno, t.n_turno, t.tipo, t.capacidade, uc.id_unidadecurricular, uc.nome, uc.ects, c.nome, ac.ano_curricular, tu.hora_inicio, tu.hora_fim
  ORDER BY uc.nome, t.n_turno
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_estatisticas_turno OWNER TO neondb_owner;

--
-- TOC entry 291 (class 1259 OID 229391)
-- Name: mv_resumo_inscricoes_aluno; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_resumo_inscricoes_aluno AS
 SELECT a.n_mecanografico,
    a.nome AS aluno_nome,
    a.email AS aluno_email,
    c.nome AS curso_nome,
    ac.ano_curricular,
    count(DISTINCT it.id_unidadecurricular) AS total_ucs_inscritas,
    count(DISTINCT it.id_turno) AS total_turnos_inscritos,
    sum(uc.ects) AS total_ects,
    min(it.data_inscricao) AS primeira_inscricao,
    max(it.data_inscricao) AS ultima_inscricao,
    count(DISTINCT it.data_inscricao) AS dias_com_atividade
   FROM ((((public.aluno a
     JOIN public.curso c ON ((a.id_curso = c.id_curso)))
     JOIN public.ano_curricular ac ON ((a.id_anocurricular = ac.id_anocurricular)))
     LEFT JOIN public.inscricao_turno it ON ((a.n_mecanografico = it.n_mecanografico)))
     LEFT JOIN public.unidade_curricular uc ON ((it.id_unidadecurricular = uc.id_unidadecurricular)))
  GROUP BY a.n_mecanografico, a.nome, a.email, c.nome, ac.ano_curricular
  ORDER BY a.nome
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_resumo_inscricoes_aluno OWNER TO neondb_owner;

--
-- TOC entry 292 (class 1259 OID 229405)
-- Name: mv_ucs_mais_procuradas; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_ucs_mais_procuradas AS
 SELECT uc.id_unidadecurricular,
    uc.nome AS uc_nome,
    uc.ects,
    c.nome AS curso_nome,
    ac.ano_curricular,
    s.semestre,
    count(DISTINCT it.n_mecanografico) AS total_alunos_inscritos,
    count(DISTINCT it.id_turno) AS total_turnos_com_inscricoes,
    count(DISTINCT it.id_inscricao) AS total_inscricoes,
    sum(t.capacidade) AS capacidade_total_turnos,
    round((((count(DISTINCT it.n_mecanografico))::numeric / (NULLIF(sum(t.capacidade), 0))::numeric) * (100)::numeric), 2) AS taxa_preenchimento_global_percent
   FROM (((((public.unidade_curricular uc
     JOIN public.curso c ON ((uc.id_curso = c.id_curso)))
     JOIN public.ano_curricular ac ON ((uc.id_anocurricular = ac.id_anocurricular)))
     JOIN public.semestre s ON ((uc.id_semestre = s.id_semestre)))
     LEFT JOIN public.inscricao_turno it ON ((uc.id_unidadecurricular = it.id_unidadecurricular)))
     LEFT JOIN public.turno t ON ((it.id_turno = t.id_turno)))
  GROUP BY uc.id_unidadecurricular, uc.nome, uc.ects, c.nome, ac.ano_curricular, s.semestre
  ORDER BY (count(DISTINCT it.n_mecanografico)) DESC, uc.nome
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_ucs_mais_procuradas OWNER TO neondb_owner;

--
-- TOC entry 277 (class 1259 OID 172033)
-- Name: pedido_troca_turno; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.pedido_troca_turno (
    id_pedido integer NOT NULL,
    id_inscricao_solicitante integer NOT NULL,
    id_turno_desejado integer NOT NULL,
    id_inscricao_contraparte integer,
    estado character varying(20) DEFAULT 'pendente'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.pedido_troca_turno OWNER TO neondb_owner;

--
-- TOC entry 276 (class 1259 OID 172032)
-- Name: pedido_troca_turno_id_pedido_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.pedido_troca_turno_id_pedido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedido_troca_turno_id_pedido_seq OWNER TO neondb_owner;

--
-- TOC entry 3944 (class 0 OID 0)
-- Dependencies: 276
-- Name: pedido_troca_turno_id_pedido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.pedido_troca_turno_id_pedido_seq OWNED BY public.pedido_troca_turno.id_pedido;


--
-- TOC entry 236 (class 1259 OID 24667)
-- Name: semestre_id_semestre_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.semestre_id_semestre_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.semestre_id_semestre_seq OWNER TO neondb_owner;

--
-- TOC entry 3946 (class 0 OID 0)
-- Dependencies: 236
-- Name: semestre_id_semestre_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.semestre_id_semestre_seq OWNED BY public.semestre.id_semestre;


--
-- TOC entry 238 (class 1259 OID 24675)
-- Name: turno_id_turno_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.turno_id_turno_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.turno_id_turno_seq OWNER TO neondb_owner;

--
-- TOC entry 3948 (class 0 OID 0)
-- Dependencies: 238
-- Name: turno_id_turno_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.turno_id_turno_seq OWNED BY public.turno.id_turno;


--
-- TOC entry 263 (class 1259 OID 98320)
-- Name: uc_mais4etcs; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.uc_mais4etcs AS
 SELECT id_unidadecurricular,
    id_semestre,
    id_anocurricular,
    ects,
    nome
   FROM public.unidade_curricular
  WHERE (ects > 4);


ALTER VIEW public.uc_mais4etcs OWNER TO neondb_owner;

--
-- TOC entry 241 (class 1259 OID 24691)
-- Name: unidade_curricular_id_unidadecurricular_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.unidade_curricular_id_unidadecurricular_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.unidade_curricular_id_unidadecurricular_seq OWNER TO neondb_owner;

--
-- TOC entry 3951 (class 0 OID 0)
-- Dependencies: 241
-- Name: unidade_curricular_id_unidadecurricular_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.unidade_curricular_id_unidadecurricular_seq OWNED BY public.unidade_curricular.id_unidadecurricular;


--
-- TOC entry 273 (class 1259 OID 139265)
-- Name: utilizador; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.utilizador (
    id bigint NOT NULL,
    tipo character varying(20) NOT NULL,
    ativo boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.utilizador OWNER TO neondb_owner;

--
-- TOC entry 272 (class 1259 OID 139264)
-- Name: utilizador_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

ALTER TABLE public.utilizador ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.utilizador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 269 (class 1259 OID 114693)
-- Name: vw_alunos_inscricoes_2025; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_alunos_inscricoes_2025 AS
 SELECT it.id_inscricao,
    it.data_inscricao,
    a.n_mecanografico,
    a.nome AS aluno_nome,
    a.email AS aluno_email,
    it.id_unidadecurricular,
    uc.nome AS uc_nome,
    it.id_turno
   FROM ((public.inscricao_turno it
     JOIN public.aluno a ON ((a.n_mecanografico = it.n_mecanografico)))
     JOIN public.unidade_curricular uc ON ((uc.id_unidadecurricular = it.id_unidadecurricular)))
  WHERE (EXTRACT(year FROM it.data_inscricao) = (2025)::numeric)
  ORDER BY it.data_inscricao DESC, a.nome;


ALTER VIEW public.vw_alunos_inscricoes_2025 OWNER TO neondb_owner;

--
-- TOC entry 262 (class 1259 OID 98316)
-- Name: vw_alunos_matriculados_por_dia; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_alunos_matriculados_por_dia AS
 SELECT m.id_matricula,
    m.n_mecanografico,
    a.nome,
    a.email,
    m.estado,
    m.data_matricula,
    m.data_matricula AS dia_matricula,
    (EXTRACT(year FROM m.data_matricula))::integer AS ano_matricula
   FROM (public.matricula m
     JOIN public.aluno a USING (n_mecanografico));


ALTER VIEW public.vw_alunos_matriculados_por_dia OWNER TO neondb_owner;

--
-- TOC entry 265 (class 1259 OID 98328)
-- Name: vw_alunos_por_ordem_alfabetica; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_alunos_por_ordem_alfabetica AS
 SELECT n_mecanografico,
    nome,
    email,
    id_anocurricular
   FROM public.aluno a
  ORDER BY nome;


ALTER VIEW public.vw_alunos_por_ordem_alfabetica OWNER TO neondb_owner;

--
-- TOC entry 267 (class 1259 OID 106500)
-- Name: vw_cursos; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_cursos AS
 SELECT id_curso,
    nome,
    grau
   FROM public.curso;


ALTER VIEW public.vw_cursos OWNER TO neondb_owner;

--
-- TOC entry 268 (class 1259 OID 114688)
-- Name: vw_top_docente_uc_ano_corrente; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_top_docente_uc_ano_corrente AS
 WITH ano_corrente AS (
         SELECT max(ano_letivo.id_anoletivo) AS id_anoletivo
           FROM public.ano_letivo
        ), ucs_no_ano AS (
         SELECT d.id_docente,
            d.nome,
            d.email,
            count(DISTINCT lu.id_unidadecurricular) AS total_ucs
           FROM (((((public.docente d
             JOIN public.leciona_uc lu ON ((lu.id_docente = d.id_docente)))
             JOIN public.unidade_curricular uc ON ((uc.id_unidadecurricular = lu.id_unidadecurricular)))
             JOIN public.semestre s ON ((s.id_semestre = uc.id_semestre)))
             JOIN public.horario h ON ((h.id_semestre = s.id_semestre)))
             JOIN ano_corrente ac ON ((h.id_anoletivo = ac.id_anoletivo)))
          GROUP BY d.id_docente, d.nome, d.email
        )
 SELECT id_docente,
    nome,
    email,
    total_ucs
   FROM ucs_no_ano
  ORDER BY total_ucs DESC, nome
 LIMIT 1;


ALTER VIEW public.vw_top_docente_uc_ano_corrente OWNER TO neondb_owner;

--
-- TOC entry 266 (class 1259 OID 106496)
-- Name: vw_turnos; Type: VIEW; Schema: public; Owner: neondb_owner
--

CREATE VIEW public.vw_turnos AS
 SELECT id_turno,
    n_turno,
    tipo,
    capacidade
   FROM public.turno;


ALTER VIEW public.vw_turnos OWNER TO neondb_owner;

--
-- TOC entry 3421 (class 2604 OID 24590)
-- Name: ano_curricular id_anocurricular; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ano_curricular ALTER COLUMN id_anocurricular SET DEFAULT nextval('public.ano_curricular_id_anocurricular_seq'::regclass);


--
-- TOC entry 3422 (class 2604 OID 24598)
-- Name: ano_letivo id_anoletivo; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ano_letivo ALTER COLUMN id_anoletivo SET DEFAULT nextval('public.ano_letivo_id_anoletivo_seq'::regclass);


--
-- TOC entry 3437 (class 2604 OID 212996)
-- Name: core_avaliacaopdf id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_avaliacaopdf ALTER COLUMN id SET DEFAULT nextval('public.core_avaliacaopdf_id_seq'::regclass);


--
-- TOC entry 3423 (class 2604 OID 24606)
-- Name: curso id_curso; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.curso ALTER COLUMN id_curso SET DEFAULT nextval('public.curso_id_curso_seq'::regclass);


--
-- TOC entry 3424 (class 2604 OID 24616)
-- Name: docente id_docente; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.docente ALTER COLUMN id_docente SET DEFAULT nextval('public.docente_id_docente_seq'::regclass);


--
-- TOC entry 3425 (class 2604 OID 24626)
-- Name: horario id_horario; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.horario ALTER COLUMN id_horario SET DEFAULT nextval('public.horario_id_horario_seq'::regclass);


--
-- TOC entry 3426 (class 2604 OID 24636)
-- Name: inscricao_turno id_inscricao; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscricao_turno ALTER COLUMN id_inscricao SET DEFAULT nextval('public.inscricao_turno_id_inscricao_seq'::regclass);


--
-- TOC entry 3431 (class 2604 OID 163844)
-- Name: log_eventos id_log; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.log_eventos ALTER COLUMN id_log SET DEFAULT nextval('public.log_eventos_id_log_seq'::regclass);


--
-- TOC entry 3427 (class 2604 OID 24661)
-- Name: matricula id_matricula; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matricula ALTER COLUMN id_matricula SET DEFAULT nextval('public.matricula_id_matricula_seq'::regclass);


--
-- TOC entry 3433 (class 2604 OID 172036)
-- Name: pedido_troca_turno id_pedido; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.pedido_troca_turno ALTER COLUMN id_pedido SET DEFAULT nextval('public.pedido_troca_turno_id_pedido_seq'::regclass);


--
-- TOC entry 3428 (class 2604 OID 24671)
-- Name: semestre id_semestre; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.semestre ALTER COLUMN id_semestre SET DEFAULT nextval('public.semestre_id_semestre_seq'::regclass);


--
-- TOC entry 3429 (class 2604 OID 24679)
-- Name: turno id_turno; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.turno ALTER COLUMN id_turno SET DEFAULT nextval('public.turno_id_turno_seq'::regclass);


--
-- TOC entry 3430 (class 2604 OID 24695)
-- Name: unidade_curricular id_unidadecurricular; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.unidade_curricular ALTER COLUMN id_unidadecurricular SET DEFAULT nextval('public.unidade_curricular_id_unidadecurricular_seq'::regclass);


--
-- TOC entry 3799 (class 0 OID 16487)
-- Dependencies: 218
-- Data for Name: users_sync; Type: TABLE DATA; Schema: neon_auth; Owner: neondb_owner
--

COPY neon_auth.users_sync (raw_json, updated_at, deleted_at) FROM stdin;
{"id": "80c76046-a49f-4dcf-999d-17daec1726d0", "display_name": "David Simão Borges", "has_password": false, "is_anonymous": false, "primary_email": "pv27431@aluno.estgv.ipv.pt", "selected_team": null, "auth_with_email": false, "client_metadata": null, "oauth_providers": [], "server_metadata": null, "otp_auth_enabled": false, "selected_team_id": null, "profile_image_url": null, "requires_totp_mfa": false, "signed_up_at_millis": 1761851098762, "passkey_auth_enabled": false, "last_active_at_millis": 1761851098762, "primary_email_verified": false, "client_read_only_metadata": null, "primary_email_auth_enabled": true}	2025-10-30 19:04:59+00	2025-11-01 14:27:37.609057+00
\.


--
-- TOC entry 3800 (class 0 OID 24576)
-- Dependencies: 219
-- Data for Name: aluno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.aluno (n_mecanografico, id_curso, id_anocurricular, nome, email, password) FROM stdin;
12345	1	1	Ana Silva	ana.silva@example.com	abc123
12346	1	1	Bruno Costa	bruno.costa@example.com	abc123
12347	1	1	Carla Santos	carla.santos@example.com	abc123
12348	1	1	Diogo Vieira	diogo.vieira@example.com	abc123
12349	1	1	Eva Marques	eva.marques@example.com	abc123
12350	1	1	Fábio Ribeiro	fabio.ribeiro@example.com	abc123
1002	1	1	Bruno Costa	bruno.costa@email.pt	pw2
1003	1	2	Carla Mendes	carla.mendes@email.pt	pw3
1004	1	2	Diogo Pereira	diogo.pereira@email.pt	pw4
1005	2	1	Eduarda Lopes	eduarda.lopes@email.pt	pw5
1006	2	1	Filipe Matos	filipe.matos@email.pt	pw6
1007	2	2	Gabriela Rocha	gabriela.rocha@email.pt	pw7
1008	2	2	Hugo Almeida	hugo.almeida@email.pt	pw8
1009	3	1	Inês Cardoso	ines.cardoso@email.pt	pw9
1010	3	2	Joaquim Morais	joaquim.morais@email.pt	pw10
1011	3	1	Leonor Reis	leonor.reis@email.pt	pw11
1013	3	2	Nuno Moreira	nuno.moreira@email.pt	pw13
1014	2	2	Olívia Amaral	olivia.amaral@email.pt	pw14
1015	1	2	Pedro Fonseca	pedro.fonseca@email.pt	pw15
9999	1	1	David Teste	david.teste@alunos.ipv.pt	senha123
12351	1	1	João Pedro Silva	joao.silva@alunos.ipv.pt	abc123
12352	1	1	Maria Santos Costa	maria.costa@alunos.ipv.pt	abc123
12353	1	1	Pedro Almeida Rocha	pedro.rocha@alunos.ipv.pt	abc123
12354	1	1	Sofia Rodrigues Lima	sofia.lima@alunos.ipv.pt	abc123
12355	1	1	André Ferreira Santos	andre.santos@alunos.ipv.pt	abc123
12356	1	1	Beatriz Oliveira Sousa	beatriz.sousa@alunos.ipv.pt	abc123
12357	1	1	Ricardo Martins Pinto	ricardo.pinto@alunos.ipv.pt	abc123
12358	1	1	Inês Cardoso Lopes	ines.lopes@alunos.ipv.pt	abc123
12359	1	2	Miguel Teixeira Cruz	miguel.cruz@alunos.ipv.pt	abc123
12360	1	2	Carolina Nunes Dias	carolina.dias@alunos.ipv.pt	abc123
12361	1	2	Tiago Moreira Gomes	tiago.gomes@alunos.ipv.pt	abc123
12362	1	2	Leonor Pereira Ramos	leonor.ramos@alunos.ipv.pt	abc123
12363	1	2	Gonçalo Ribeiro Castro	goncalo.castro@alunos.ipv.pt	abc123
12364	1	2	Mariana Soares Melo	mariana.melo@alunos.ipv.pt	abc123
30001	2	1	João Silva TDM	joao.silva.tdm@ipv.pt	password123
30002	2	1	Maria Santos TDM	maria.santos.tdm@ipv.pt	password123
30003	2	1	Pedro Costa TDM	pedro.costa.tdm@ipv.pt	password123
30004	2	1	Ana Oliveira TDM	ana.oliveira.tdm@ipv.pt	password123
30005	2	1	Carlos Pereira TDM	carlos.pereira.tdm@ipv.pt	password123
30101	2	2	Sofia Rodrigues TDM	sofia.rodrigues.tdm@ipv.pt	password123
30102	2	2	Miguel Ferreira TDM	miguel.ferreira.tdm@ipv.pt	password123
30103	2	2	Beatriz Alves TDM	beatriz.alves.tdm@ipv.pt	password123
30104	2	2	Ricardo Martins TDM	ricardo.martins.tdm@ipv.pt	password123
30105	2	2	Inês Carvalho TDM	ines.carvalho.tdm@ipv.pt	password123
30201	2	3	Tiago Sousa TDM	tiago.sousa.tdm@ipv.pt	password123
30202	2	3	Catarina Lopes TDM	catarina.lopes.tdm@ipv.pt	password123
30203	2	3	Bruno Fernandes TDM	bruno.fernandes.tdm@ipv.pt	password123
30204	2	3	Laura Gonçalves TDM	laura.goncalves.tdm@ipv.pt	password123
30205	2	3	André Ribeiro TDM	andre.ribeiro.tdm@ipv.pt	password123
40001	1	1	Sofia Martins Silva	sofia.martins@alunos.ipv.pt	password123
40002	1	1	Ricardo Pereira Costa	ricardo.pereira@alunos.ipv.pt	password123
\.


--
-- TOC entry 3802 (class 0 OID 24587)
-- Dependencies: 221
-- Data for Name: ano_curricular; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.ano_curricular (id_anocurricular, ano_curricular) FROM stdin;
1	1º ano
2	2º ano
3	3º ano
\.


--
-- TOC entry 3804 (class 0 OID 24595)
-- Dependencies: 223
-- Data for Name: ano_letivo; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.ano_letivo (id_anoletivo, anoletivo) FROM stdin;
1	2024/2025
\.


--
-- TOC entry 3860 (class 0 OID 204801)
-- Dependencies: 287
-- Data for Name: auditoria_inscricao; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auditoria_inscricao (id_auditoria, data_tentativa, resultado, motivo_rejeicao, tempo_processamento_ms, id_turno, id_unidadecurricular, n_mecanografico) FROM stdin;
1	2026-01-12 00:13:58.210119+00	sucesso	\N	730	17	1	12345
2	2026-01-12 00:34:26.776051+00	sucesso	\N	1054	4	4	12345
3	2026-01-20 13:35:45.356698+00	sucesso	\N	384	17	1	40001
4	2026-01-20 13:35:59.406891+00	sucesso	\N	379	4	2	40001
\.


--
-- TOC entry 3831 (class 0 OID 24804)
-- Dependencies: 250
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- TOC entry 3833 (class 0 OID 24812)
-- Dependencies: 252
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3829 (class 0 OID 24798)
-- Dependencies: 248
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add aluno	7	add_aluno
26	Can change aluno	7	change_aluno
27	Can delete aluno	7	delete_aluno
28	Can view aluno	7	view_aluno
29	Can add ano curricular	8	add_anocurricular
30	Can change ano curricular	8	change_anocurricular
31	Can delete ano curricular	8	delete_anocurricular
32	Can view ano curricular	8	view_anocurricular
33	Can add ano letivo	9	add_anoletivo
34	Can change ano letivo	9	change_anoletivo
35	Can delete ano letivo	9	delete_anoletivo
36	Can view ano letivo	9	view_anoletivo
37	Can add curso	10	add_curso
38	Can change curso	10	change_curso
39	Can delete curso	10	delete_curso
40	Can view curso	10	view_curso
41	Can add docente	11	add_docente
42	Can change docente	11	change_docente
43	Can delete docente	11	delete_docente
44	Can view docente	11	view_docente
45	Can add horario	12	add_horario
46	Can change horario	12	change_horario
47	Can delete horario	12	delete_horario
48	Can view horario	12	view_horario
49	Can add inscricao turno	13	add_inscricaoturno
50	Can change inscricao turno	13	change_inscricaoturno
51	Can delete inscricao turno	13	delete_inscricaoturno
52	Can view inscricao turno	13	view_inscricaoturno
53	Can add inscrito uc	14	add_inscritouc
54	Can change inscrito uc	14	change_inscritouc
55	Can delete inscrito uc	14	delete_inscritouc
56	Can view inscrito uc	14	view_inscritouc
57	Can add leciona uc	15	add_lecionauc
58	Can change leciona uc	15	change_lecionauc
59	Can delete leciona uc	15	delete_lecionauc
60	Can view leciona uc	15	view_lecionauc
61	Can add matricula	16	add_matricula
62	Can change matricula	16	change_matricula
63	Can delete matricula	16	delete_matricula
64	Can view matricula	16	view_matricula
65	Can add semestre	17	add_semestre
66	Can change semestre	17	change_semestre
67	Can delete semestre	17	delete_semestre
68	Can view semestre	17	view_semestre
69	Can add turno	18	add_turno
70	Can change turno	18	change_turno
71	Can delete turno	18	delete_turno
72	Can view turno	18	view_turno
73	Can add turno uc	19	add_turnouc
74	Can change turno uc	19	change_turnouc
75	Can delete turno uc	19	delete_turnouc
76	Can view turno uc	19	view_turnouc
77	Can add unidade curricular	20	add_unidadecurricular
78	Can change unidade curricular	20	change_unidadecurricular
79	Can delete unidade curricular	20	delete_unidadecurricular
80	Can view unidade curricular	20	view_unidadecurricular
81	Can add alunos matriculados por dia	21	add_alunosmatriculadospordia
82	Can change alunos matriculados por dia	21	change_alunosmatriculadospordia
83	Can delete alunos matriculados por dia	21	delete_alunosmatriculadospordia
84	Can view alunos matriculados por dia	21	view_alunosmatriculadospordia
85	Can add alunos por ordem alfabetica	22	add_alunosporordemalfabetica
86	Can change alunos por ordem alfabetica	22	change_alunosporordemalfabetica
87	Can delete alunos por ordem alfabetica	22	delete_alunosporordemalfabetica
88	Can view alunos por ordem alfabetica	22	view_alunosporordemalfabetica
89	Can add Cadeira (2º semestre)	23	add_cadeirassemestre
90	Can change Cadeira (2º semestre)	23	change_cadeirassemestre
91	Can delete Cadeira (2º semestre)	23	delete_cadeirassemestre
92	Can view Cadeira (2º semestre)	23	view_cadeirassemestre
93	Can add cursos	24	add_cursos
94	Can change cursos	24	change_cursos
95	Can delete cursos	24	delete_cursos
96	Can view cursos	24	view_cursos
97	Can add turnos	25	add_turnos
98	Can change turnos	25	change_turnos
99	Can delete turnos	25	delete_turnos
100	Can view turnos	25	view_turnos
101	Can add UC (>4 ECTS)	26	add_ucmais4ects
102	Can change UC (>4 ECTS)	26	change_ucmais4ects
103	Can delete UC (>4 ECTS)	26	delete_ucmais4ects
104	Can view UC (>4 ECTS)	26	view_ucmais4ects
105	Can add vw alunos inscricoes2025	27	add_vwalunosinscricoes2025
106	Can change vw alunos inscricoes2025	27	change_vwalunosinscricoes2025
107	Can delete vw alunos inscricoes2025	27	delete_vwalunosinscricoes2025
108	Can view vw alunos inscricoes2025	27	view_vwalunosinscricoes2025
109	Can add vw top docente uc ano corrente	28	add_vwtopdocenteucanocorrente
110	Can change vw top docente uc ano corrente	28	change_vwtopdocenteucanocorrente
111	Can delete vw top docente uc ano corrente	28	delete_vwtopdocenteucanocorrente
112	Can view vw top docente uc ano corrente	28	view_vwtopdocenteucanocorrente
113	Can add horario pdf	29	add_horariopdf
114	Can change horario pdf	29	change_horariopdf
115	Can delete horario pdf	29	delete_horariopdf
116	Can view horario pdf	29	view_horariopdf
117	Can add Utilizador	30	add_utilizador
118	Can change Utilizador	30	change_utilizador
119	Can delete Utilizador	30	delete_utilizador
120	Can view Utilizador	30	view_utilizador
121	Can add pedido troca turno	31	add_pedidotrocaturno
122	Can change pedido troca turno	31	change_pedidotrocaturno
123	Can delete pedido troca turno	31	delete_pedidotrocaturno
124	Can view pedido troca turno	31	view_pedidotrocaturno
125	Can add pedido troca turno	32	add_pedidotrocaturno
126	Can change pedido troca turno	32	change_pedidotrocaturno
127	Can delete pedido troca turno	32	delete_pedidotrocaturno
128	Can view pedido troca turno	32	view_pedidotrocaturno
129	Can add turno	33	add_turno
130	Can change turno	33	change_turno
131	Can delete turno	33	delete_turno
132	Can view turno	33	view_turno
133	Can add inscricao turno	34	add_inscricaoturno
134	Can change inscricao turno	34	change_inscricaoturno
135	Can delete inscricao turno	34	delete_inscricaoturno
136	Can view inscricao turno	34	view_inscricaoturno
137	Can add log evento	35	add_logevento
138	Can change log evento	35	change_logevento
139	Can delete log evento	35	delete_logevento
140	Can view log evento	35	view_logevento
141	Can add auditoria inscricao	36	add_auditoriainscricao
142	Can change auditoria inscricao	36	change_auditoriainscricao
143	Can delete auditoria inscricao	36	delete_auditoriainscricao
144	Can view auditoria inscricao	36	view_auditoriainscricao
145	Can add avaliacao pdf	37	add_avaliacaopdf
146	Can change avaliacao pdf	37	change_avaliacaopdf
147	Can delete avaliacao pdf	37	delete_avaliacaopdf
148	Can view avaliacao pdf	37	view_avaliacaopdf
\.


--
-- TOC entry 3835 (class 0 OID 24818)
-- Dependencies: 254
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
2	pbkdf2_sha256$1000000$P7w83F3zk0wVkx5YpCfH8c$j3OxAZ2CdeAkq6oikyTxihIpNLaBpKmt3yDtCdpGP/k=	2026-01-20 14:22:55.992365+00	t	admin	Admin	Sistema	admin@example.com	t	t	2025-11-24 21:24:09.769942+00
1	pbkdf2_sha256$720000$VuyIpLTA4ezX3RoCESlM2R$KoK5AIg2JmJ7yEHJiNkftFIc+icgXC8k3uoI/+ZLa74=	2025-11-17 20:22:18.36034+00	t	ana			ana@email.com	t	t	2025-11-01 17:31:48.799178+00
5	pbkdf2_sha256$720000$VuyIpLTA4ezX3RoCESlM2R$KoK5AIg2JmJ7yEHJiNkftFIc+icgXC8k3uoI/+ZLa74=	\N	f	joao123	João	Silva	joao@example.com	f	t	2025-11-24 21:37:36.269963+00
\.


--
-- TOC entry 3837 (class 0 OID 24826)
-- Dependencies: 256
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- TOC entry 3839 (class 0 OID 24832)
-- Dependencies: 258
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3862 (class 0 OID 212993)
-- Dependencies: 289
-- Data for Name: core_avaliacaopdf; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.core_avaliacaopdf (id, nome, ficheiro, id_anocurricular, atualizado_em, id_curso) FROM stdin;
18	Calendário de Avaliações - EI - 1º ano	mongodb_gridfs:696e788b3644be914bac9616	1	2026-01-19 18:31:39.69963+00	1
19	Calendário de Avaliações - EI - 2º ano	mongodb_gridfs:696e78c83644be914bac961b	2	2026-01-19 18:32:40.333972+00	1
20	Calendário de Avaliações - EI - 3º ano	mongodb_gridfs:696e78db3644be914bac961f	3	2026-01-19 18:32:59.523119+00	1
21	Calendário de Avaliações - TDM - 1º ano	mongodb_gridfs:696e79073644be914bac9623	1	2026-01-19 18:33:43.983415+00	2
22	Calendário de Avaliações - TDM - 2º ano	mongodb_gridfs:696e791b3644be914bac9627	2	2026-01-19 18:34:04.151501+00	2
23	Calendário de Avaliações - TDM - 3º ano	mongodb_gridfs:696e79483644be914bac962b	3	2026-01-19 18:34:48.525628+00	2
24	Calendário de Avaliações - EISI - 1º ano	mongodb_gridfs:696e798d3644be914bac962f	1	2026-01-19 18:35:57.864498+00	5
25	Calendário de Avaliações - EISI - 2º ano	mongodb_gridfs:696e79a73644be914bac9633	2	2026-01-19 18:36:23.413983+00	5
26	Calendário de Avaliações - RSI - 1º ano	mongodb_gridfs:696e79d63644be914bac9637	1	2026-01-19 18:37:10.963163+00	3
27	Calendário de Avaliações - RSI - 2º ano	mongodb_gridfs:696e7a093644be914bac963b	2	2026-01-19 18:38:01.465244+00	3
28	Calendário de Avaliações - DWDM - 1º ano	mongodb_gridfs:696e7a273644be914bac963f	1	2026-01-19 18:38:32.115806+00	4
29	Calendário de Avaliações - DWDM - 2º ano	mongodb_gridfs:696e7a4a3644be914bac9643	2	2026-01-19 18:39:06.534089+00	4
\.


--
-- TOC entry 3844 (class 0 OID 131073)
-- Dependencies: 271
-- Data for Name: core_horariopdf; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.core_horariopdf (id, nome, ficheiro, atualizado_em, id_anocurricular, id_curso) FROM stdin;
20	Horário do 1º ano - EI	mongodb_gridfs:696e76563644be914bac95d1	2026-01-19 18:22:15.927139+00	1	1
21	Horário do 2º ano - EI	mongodb_gridfs:696e76733644be914bac95d5	2026-01-19 18:22:44.337213+00	2	1
22	Horário do 3º ano - EI	mongodb_gridfs:696e76ac3644be914bac95dd	2026-01-19 18:23:40.66723+00	3	1
23	Horário do 1º ano - TDM	mongodb_gridfs:696e76e03644be914bac95e1	2026-01-19 18:24:33.253646+00	1	2
24	Horário do 2º ano - TDM	mongodb_gridfs:696e77093644be914bac95e5	2026-01-19 18:25:14.148549+00	2	2
25	Horário do 3º ano - TDM	mongodb_gridfs:696e77243644be914bac95ea	2026-01-19 18:25:40.844651+00	3	2
26	Horário do 1º ano - EISI	mongodb_gridfs:696e774e3644be914bac95ee	2026-01-19 18:26:23.224789+00	1	5
27	Horário do 2º ano - EISI	mongodb_gridfs:696e77703644be914bac95f3	2026-01-19 18:26:57.540992+00	2	5
28	Horário do 1º ano - RSI	mongodb_gridfs:696e779b3644be914bac95f7	2026-01-19 18:27:40.403489+00	1	3
29	Horário do 2º ano - RSI	mongodb_gridfs:696e77ae3644be914bac95fb	2026-01-19 18:27:58.625673+00	2	3
30	Horário do 1º ano - DWDM	mongodb_gridfs:696e77f93644be914bac95ff	2026-01-19 18:29:14.216725+00	1	4
31	Horário do 2º ano - DWDM	mongodb_gridfs:696e780e3644be914bac9603	2026-01-19 18:29:35.271646+00	2	4
\.


--
-- TOC entry 3852 (class 0 OID 172058)
-- Dependencies: 279
-- Data for Name: core_pedidotrocaturno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.core_pedidotrocaturno (id, estado, created_at, updated_at, inscricao_contraparte_id, inscricao_solicitante_id, turno_desejado_id) FROM stdin;
\.


--
-- TOC entry 3806 (class 0 OID 24603)
-- Dependencies: 225
-- Data for Name: curso; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.curso (id_curso, nome, grau) FROM stdin;
1	Engenharia Informatica	6
2	Tecnologia e Design Multimedia	6
3	Redes e Sistemas Informaticos	5
4	Desenvolvimento Web e Dispositivos Móveis	5
5	Engenharia Informática – Sistemas de Informação	7
\.


--
-- TOC entry 3841 (class 0 OID 24890)
-- Dependencies: 260
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- TOC entry 3827 (class 0 OID 24790)
-- Dependencies: 246
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	core	aluno
8	core	anocurricular
9	core	anoletivo
10	core	curso
11	core	docente
12	core	horario
13	core	inscricaoturno
14	core	inscritouc
15	core	lecionauc
16	core	matricula
17	core	semestre
18	core	turno
19	core	turnouc
20	core	unidadecurricular
21	core	alunosmatriculadospordia
22	core	alunosporordemalfabetica
23	core	cadeirassemestre
24	core	cursos
25	core	turnos
26	core	ucmais4ects
27	core	vwalunosinscricoes2025
28	core	vwtopdocenteucanocorrente
29	core	horariopdf
30	core	utilizador
31	core	pedidotrocaturno
32	forum	pedidotrocaturno
33	forum	turno
34	forum	inscricaoturno
35	core	logevento
36	core	auditoriainscricao
37	core	avaliacaopdf
\.


--
-- TOC entry 3825 (class 0 OID 24782)
-- Dependencies: 244
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-10-30 19:42:19.341775+00
2	auth	0001_initial	2025-10-30 19:42:22.641481+00
3	admin	0001_initial	2025-10-30 19:42:23.54778+00
4	admin	0002_logentry_remove_auto_add	2025-10-30 19:42:23.68167+00
5	admin	0003_logentry_add_action_flag_choices	2025-10-30 19:42:24.026191+00
6	contenttypes	0002_remove_content_type_name	2025-10-30 19:42:24.703048+00
7	auth	0002_alter_permission_name_max_length	2025-10-30 19:42:25.141563+00
8	auth	0003_alter_user_email_max_length	2025-10-30 19:42:25.593694+00
9	auth	0004_alter_user_username_opts	2025-10-30 19:42:25.834845+00
10	auth	0005_alter_user_last_login_null	2025-10-30 19:42:26.355241+00
11	auth	0006_require_contenttypes_0002	2025-10-30 19:42:26.608783+00
12	auth	0007_alter_validators_add_error_messages	2025-10-30 19:42:26.976104+00
13	auth	0008_alter_user_username_max_length	2025-10-30 19:42:27.512774+00
14	auth	0009_alter_user_last_name_max_length	2025-10-30 19:42:27.967298+00
15	auth	0010_alter_group_name_max_length	2025-10-30 19:42:28.357148+00
16	auth	0011_update_proxy_permissions	2025-10-30 19:42:28.598895+00
17	auth	0012_alter_user_first_name_max_length	2025-10-30 19:42:29.19946+00
18	sessions	0001_initial	2025-10-30 19:42:30.119804+00
19	core	0001_initial	2025-11-01 14:57:08.230674+00
20	core	0002_alter_aluno_options_alter_anocurricular_options_and_more	2025-11-06 18:15:34.317028+00
21	core	0003_alunosmatriculadospordia_alunosporordemalfabetica_and_more	2025-11-23 16:22:35.994854+00
22	core	0004_utilizador	2025-11-24 21:20:43.727177+00
23	core	0004_pedidotrocaturno	2025-12-10 15:52:35.898333+00
24	forum	0001_initial	2025-12-10 16:28:28.262369+00
25	core	0004_logevento_horariopdf_id_anocurricular_and_more	2026-01-11 18:28:43.952427+00
26	core	0005_horariopdf_id_anocurricular_avaliacaopdf	2026-01-11 19:14:08.080778+00
27	core	0006_add_curso_to_pdf_models	2026-01-14 23:29:47.736713+00
\.


--
-- TOC entry 3842 (class 0 OID 24918)
-- Dependencies: 261
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
nkzt2hjsufe8ojyaq8z9rzbhoxeyig3r	.eJxVjDsOwjAQBe_iGll21l9K-pzB8u46OIASKU4qxN1JpBTQvpl5b5Hytta0tbKkkcVVaHH53TDTs0wH4Eee7rOkeVqXEeWhyJM22c9cXrfT_TuoudW9LmQcBEM-WCTfWQAFUXEsyA5BR6cGVGzt4Mh5MHYHWaO2hjsIZIL4fAHO5TdJ:1vFGBi:geg3LtytA64Ta9_bGtogcAQ_8lIZiZ7ZaGN22Oahppw	2025-11-15 18:18:54.967049+00
hixmya8ipqjyovypfde2qk6ra8r2wh8k	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhmbmEL5efm5qUA1jnmJCsGZOWWJMHWpuYmZOSDNeYl6xSAJh9SKxNyCnFS95PxcpVoAXO4hXA:1vhz3q:1-YZXYy-ot8CQqiKhm1UF6z62sURzgRE6GNhiV1gXw8	2026-02-02 23:53:30.330444+00
u7o4p7twn87hgg4y08k1v4kidyzrpwhk	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vNdM5:cKeNebyPDA1ddT2iz_-XYzhQim36AKc_VNoKxcXdh9U	2025-12-08 20:40:13.920485+00
8n3ri4me7d7tp2vbcb0copsv80quk23g	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vNdRj:xc63pKTtDfDKsycwb3MgPihwCvnWKCQalWYHDAJUEIo	2025-12-08 20:46:03.049273+00
op6ny2qhokonhcm565ikefw5ecdg0v05	.eJxdj8sKwjAQRf8laynJJKmNK3HvN5RJM9pok5Q-QBD_3VRaUHfDPXcOM09W4zy19TzSUHvHDgzY7juz2NwpLsDdMF5T0aQ4Dd4WS6VY6Vick6PutHZ_BC2Obd4mqy6iMhp0KQGNEFw4p82-QtAKnQFsrOFalLpEzaWyUiioiEsyliSoLP3oJt-nrEMXfNyy5W5Y55gC_XMK6LstPNIDQ99RfiSw1xukE1O1:1viCdE:xTPsRKr5pOs9Rus8RH6Mz7ILGfTdnuzoH6kuj0Q7Sec	2026-02-03 14:22:56.043795+00
tiwsbk5ystqby1jtbbfvq5q3he5k8rdc	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vUAPx:bIWLlFH5UK0U6leoAK83Y52ua-3zLKnEE3g3Z0oYwtY	2025-12-26 21:11:13.649739+00
fgk00ooqkuaknrm269v5un3pnml7ttzq	.eJxVjMsOwiAQRf-FtSE8Mgx16d5vIMMAUjWQlHZl_Hdt0oVu7znnvkSgba1hG3kJcxJnYcTpd4vEj9x2kO7Ubl1yb-syR7kr8qBDXnvKz8vh_h1UGvVbAySV2ZFnUyJEo5C894kmTMhoETkCU1HG6agnAwS26JLRM1uXwYn3B_Y-OD0:1vgW8I:gxVcUOyRNr45jsHLSRqlGOBWU3wFmaFotl6rxDO6Zqk	2026-01-29 22:48:02.941418+00
sffue0yng3qw57d9man0i2luo9u98l8i	.eJxVjDsOwjAQBe_iGllrJ_6Ekj5nsNbeNQ4gR4qTCnF3EikFtG9m3lsE3NYStsZLmEhchRaX3y1ienI9AD2w3meZ5rouU5SHIk_a5DgTv26n-3dQsJW9xggduQwDgwZtlPIM7HvPTCl7lQw4rXyvIHUZrLFEUbnB2Ezo7F6KzxfTmTds:1vUTXM:X2hvMwyELBUZKQhE1-RNbTwPk9pGGLSZ5VXrK1OBDiA	2025-12-27 17:36:08.473374+00
4uuzp3gqjp0ix9r0sj6dm93z0yn1urum	.eJxVjDsOwjAQBe_iGllrJ_6Ekj5nsNbeNQ4gR4qTCnF3EikFtG9m3lsE3NYStsZLmEhchRaX3y1ienI9AD2w3meZ5rouU5SHIk_a5DgTv26n-3dQsJW9xggduQwDgwZtlPIM7HvPTCl7lQw4rXyvIHUZrLFEUbnB2Ezo7F6KzxfTmTds:1vUUsZ:5Lte5HTyJC8DNpYTWBLe5xulSYOuqfG34rjePG6kgGA	2025-12-27 19:02:07.80862+00
5t8fv5pgh363w74b2ejq981jza7unye9	.eJxVjEEOwiAQRe_C2pAyA5S6dO8ZCMyAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIsQJx-txjokeoO-B7qrUlqdV3mKHdFHrTLa-P0vBzu30EJvXzrjHEakRmzUZSzSlph1IoTaEcEoIyb0LqUQTOPmtgOOIQADGyNZSveH-_NN_0:1vhRwF:0G9xT7aYscAawwKKSy1cDQkuhbVFmgDJ2IAd0RSr99M	2026-02-01 12:31:27.787051+00
wut74vx4dhqztr9hmptkd0dtemv6wcv2	.eJxVjEEOwiAQRe_C2pAyA5S6dO8ZCMyAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIsQJx-txjokeoO-B7qrUlqdV3mKHdFHrTLa-P0vBzu30EJvXzrjHEakRmzUZSzSlph1IoTaEcEoIyb0LqUQTOPmtgOOIQADGyNZSveH-_NN_0:1vhRwH:lx-smmVZEjJpTBmNfyrbWPNTQuanTo16an46X7m3Oo8	2026-02-01 12:31:29.083847+00
dca50ghn2xgeq9ce1e2tlb1duswjcx4s	.eJxVjDsOwjAQBe_iGllrJ_6Ekj5nsNbeNQ4gR4qTCnF3EikFtG9m3lsE3NYStsZLmEhchRaX3y1ienI9AD2w3meZ5rouU5SHIk_a5DgTv26n-3dQsJW9xggduQwDgwZtlPIM7HvPTCl7lQw4rXyvIHUZrLFEUbnB2Ezo7F6KzxfTmTds:1vUkwk:EVR49BAo9VGKlNuyv0ymOjXsaRLGZgGWS7eNlaWcHt0	2025-12-28 12:11:30.437043+00
4p3w262op63mqh4ojcfo2tevnq3zzzjk	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vUlaf:6xXskuZozbK_AAXPqh0WRps6n9KRrk6GO2AeuoKu3Uk	2025-12-28 12:52:45.161438+00
wgb04r0g2mblk4qnr0xxoe7tbdtn3sma	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vUmvN:z1hm6_1nyWAsMx4h1kbcpCWYJisLnmGoMm7HDJAzn7s	2025-12-28 14:18:13.278031+00
j1l9tr6tmhegb5hjhlmtlfryed78ddyu	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhgYQrl5-bmpQCWOeYkKwZk5ZYkwZam5iZk5IL15iXrFIAkHsIheQYlSLQDeux_g:1vXglz:h-jseIgxjtNs_8p-bZ_7ufRL5JBxYfkA4pzDLYqHvyY	2026-01-05 14:20:31.875403+00
1iynawptkihlmm1mpwp0fpa1o64rptni	.eJxVjEEOwiAQRe_C2pAyA5S6dO8ZCMyAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIsQJx-txjokeoO-B7qrUlqdV3mKHdFHrTLa-P0vBzu30EJvXzrjHEakRmzUZSzSlph1IoTaEcEoIyb0LqUQTOPmtgOOIQADGyNZSveH-_NN_0:1vhRwH:lx-smmVZEjJpTBmNfyrbWPNTQuanTo16an46X7m3Oo8	2026-02-01 12:31:29.302537+00
ga5jtolcfnqsyv3ndnxtr2cqq1u1jvvy	.eJxVjEEOwiAQRe_C2pAyA5S6dO8ZCMyAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIsQJx-txjokeoO-B7qrUlqdV3mKHdFHrTLa-P0vBzu30EJvXzrjHEakRmzUZSzSlph1IoTaEcEoIyb0LqUQTOPmtgOOIQADGyNZSveH-_NN_0:1vhRwH:lx-smmVZEjJpTBmNfyrbWPNTQuanTo16an46X7m3Oo8	2026-02-01 12:31:29.474603+00
7xm1ql7aecai36veomeb02018wxq0whi	.eJxVjEEOwiAQRe_C2hCgdAou3XsGwgyMVA0kpV0Z765NutDtf-_9lwhxW0vYel7CnMRZGHH63TDSI9cdpHustyap1XWZUe6KPGiX15by83K4fwcl9vKtkZQBRADNTiGRjR7ATA5G8Iqzs-wTJRp40KjsOHE2iRjYDOytBifeH-0IOBc:1vhuEL:71GtWHGqKDdw-LFEWOR_yKEP1pHs5dOE8KT7ochooIM	2026-02-02 18:44:01.522043+00
02mbypr3am8l84d9ay65qeft9ybckick	.eJxVjEEOwiAQRe_C2pAyA5S6dO8ZCMyAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIsQJx-txjokeoO-B7qrUlqdV3mKHdFHrTLa-P0vBzu30EJvXzrjHEakRmzUZSzSlph1IoTaEcEoIyb0LqUQTOPmtgOOIQADGyNZSveH-_NN_0:1vhRwI:7K4u7Ra6oUQkA1otwkXoIksHV_wC0sdm699I25d_Els	2026-02-01 12:31:30.536971+00
xhksmgvlrzfblj4f06tuo35ie66wsvyp	.eJxVjEEOwiAQRe_C2pBxQMu4dN8zEIYBqRpISrsy3l2bdKHb_977L-XDuhS_9jT7SdRFoTr8bhziI9UNyD3UW9Ox1WWeWG-K3mnXY5P0vO7u30EJvXzrSNklhIQSiYGjw8FaA06iJRHO-QRZTLIENBgg65DhjCAhU8iWjur9Afb3OAw:1vhuUJ:IM4X9FuwpsTNQz5LLNjlg3QwrLi-ODBmHXeRauBTdRE	2026-02-02 19:00:31.213038+00
hcuvbrej2vmpkwy61x67ukpebl2qeplw	.eJyrViotTi2KL8ksyFeyUkrMKc3LV9KBiGWmKFkZGhmbmEL5efm5qUA1jnmJCsGZOWWJMHWpuYmZOSDNeYl6xSAJh9SKxNyCnFS95PxcpVoAXO4hXA:1vhxC6:swMSk3IND2eQ4m7-P8ZIAYxOAGYn0yPhV_XY-Qb8riM	2026-02-02 21:53:54.426513+00
\.


--
-- TOC entry 3808 (class 0 OID 24613)
-- Dependencies: 227
-- Data for Name: docente; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.docente (id_docente, nome, email, cargo) FROM stdin;
1	David Borges	davidsimaoborges@gmail.com	T
2	Steven Abrantes	steven-abrantes@docente.ipv.com	Diretor de Curso
3	Filipe Manuel Simões Caldeira	caldeira@estgv.ipv.pt	Diretor do Departamento
4	Carlos Alberto Tomás Simões	csimoes@estgv.ipv.pt	Coordenador CTeSP
5	Carlos Augusto da Silva Cunha	cacunha@estgv.ipv.pt	Coordenador CTeSP
6	Rui Pedro Monteiro Amaro Duarte	pduarte@estgv.ipv.pt	Diretor de Mestrado
7	Steven Lopes Abrantes	steven@estgv.ipv.pt	Diretor de Curso
8	Valter Nelson Noronha Alves	valter@estgv.ipv.pt	Diretor de Curso
9	Júlio Sousa Florentino	julioflorentino@estgv.ipv.pt	Docente
10	Luís Carlos Lopes Soares	luislopessoares@estgv.ipv.pt	Docente
11	Luis Oliveira	luis.oliveira@estgv.ipv.pt	Docente
12	Marco André Vieira Andrade Bernardo	mbernardo@estgv.ipv.pt	Docente
13	Marcos Jorge Rebelo Ferreira	marcosferreira@estgv.ipv.pt	Docente
14	Mauro Lima	maurolima@estgv.ipv.pt	Docente
15	Nuno Filipe Alexandre Carapito	nfac@estgv.ipv.pt	Docente
16	Nuno Filipe Esteves Videira	nunovideira@estgv.ipv.pt	Docente
17	Sílvia Catarina de Oliveira Moreira	smoreira@estgv.ipv.pt	Docente
18	Tiago Orlando de Jesus Rebelo	tiago.rebelo@estgv.ipv.pt	Docente
19	Vitor Figueiredo	vmfigueiredo@estgv.ipv.pt	Docente
20	João Pedro Menoita Henriques	jhenriques@estgv.ipv.pt	Professor Adjunto
999	Teste Docente	teste@ipv.pt	Professor
\.


--
-- TOC entry 3854 (class 0 OID 180225)
-- Dependencies: 281
-- Data for Name: forum_inscricaoturno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.forum_inscricaoturno (id_inscricao, n_mecanografico, id_turno_id) FROM stdin;
\.


--
-- TOC entry 3858 (class 0 OID 180237)
-- Dependencies: 285
-- Data for Name: forum_pedidotrocaturno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.forum_pedidotrocaturno (id, estado, created_at, updated_at, inscricao_contraparte_id, inscricao_solicitante_id, turno_desejado_id) FROM stdin;
\.


--
-- TOC entry 3856 (class 0 OID 180231)
-- Dependencies: 283
-- Data for Name: forum_turno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.forum_turno (id, n_turno, tipo, capacidade) FROM stdin;
\.


--
-- TOC entry 3810 (class 0 OID 24623)
-- Dependencies: 229
-- Data for Name: horario; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.horario (id_horario, id_anoletivo, id_semestre, horario) FROM stdin;
1	1	1	Seg 10h-12h
\.


--
-- TOC entry 3812 (class 0 OID 24633)
-- Dependencies: 231
-- Data for Name: inscricao_turno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.inscricao_turno (id_inscricao, n_mecanografico, id_turno, id_unidadecurricular, data_inscricao) FROM stdin;
13	12345	1	1	2026-01-03
16	12346	1	1	2026-01-03
17	12346	2	1	2026-01-03
18	12346	3	1	2026-01-03
19	12347	1	1	2026-01-03
20	12347	2	1	2026-01-03
21	12347	3	1	2026-01-03
22	12348	1	1	2026-01-03
23	12348	2	1	2026-01-03
24	12348	3	1	2026-01-03
25	12349	1	1	2026-01-03
26	12349	2	1	2026-01-03
27	12349	3	1	2026-01-03
28	12350	1	1	2026-01-03
29	12350	2	1	2026-01-03
30	12350	3	1	2026-01-03
34	1002	1	1	2026-01-03
35	1002	2	1	2026-01-03
36	1002	3	1	2026-01-03
37	1005	1	1	2026-01-03
38	1005	2	1	2026-01-03
39	1005	3	1	2026-01-03
40	1006	1	1	2026-01-03
41	1006	2	1	2026-01-03
42	1006	3	1	2026-01-03
43	1009	1	1	2026-01-03
44	1009	2	1	2026-01-03
45	1009	3	1	2026-01-03
46	1011	1	1	2026-01-03
47	1011	2	1	2026-01-03
48	1011	3	1	2026-01-03
52	9999	1	1	2026-01-03
53	9999	2	1	2026-01-03
54	9999	3	1	2026-01-03
55	12345	1	3	2026-01-03
56	12345	2	3	2026-01-03
58	12346	1	3	2026-01-03
59	12346	2	3	2026-01-03
60	12346	3	3	2026-01-03
61	12347	1	3	2026-01-03
62	12347	2	3	2026-01-03
63	12347	3	3	2026-01-03
64	12348	1	3	2026-01-03
65	12348	2	3	2026-01-03
66	12348	3	3	2026-01-03
67	12349	1	3	2026-01-03
68	12349	2	3	2026-01-03
69	12349	3	3	2026-01-03
70	12350	1	3	2026-01-03
71	12350	2	3	2026-01-03
72	12350	3	3	2026-01-03
76	1002	1	3	2026-01-03
77	1002	2	3	2026-01-03
78	1002	3	3	2026-01-03
79	1005	1	3	2026-01-03
80	1005	2	3	2026-01-03
81	1005	3	3	2026-01-03
82	1006	1	3	2026-01-03
83	1006	2	3	2026-01-03
84	1006	3	3	2026-01-03
85	1009	1	3	2026-01-03
86	1009	2	3	2026-01-03
87	1009	3	3	2026-01-03
88	1011	1	3	2026-01-03
89	1011	2	3	2026-01-03
90	1011	3	3	2026-01-03
94	9999	1	3	2026-01-03
95	9999	2	3	2026-01-03
96	9999	3	3	2026-01-03
97	12345	1	5	2026-01-03
98	12345	2	5	2026-01-03
100	12346	1	5	2026-01-03
101	12346	2	5	2026-01-03
102	12346	3	5	2026-01-03
103	12347	1	5	2026-01-03
104	12347	2	5	2026-01-03
105	12347	3	5	2026-01-03
106	12348	1	5	2026-01-03
107	12348	2	5	2026-01-03
108	12348	3	5	2026-01-03
109	12349	1	5	2026-01-03
110	12349	2	5	2026-01-03
111	12349	3	5	2026-01-03
112	12350	1	5	2026-01-03
113	12350	2	5	2026-01-03
114	12350	3	5	2026-01-03
118	1002	1	5	2026-01-03
119	1002	2	5	2026-01-03
120	1002	3	5	2026-01-03
121	1005	1	5	2026-01-03
122	1005	2	5	2026-01-03
123	1005	3	5	2026-01-03
124	1006	1	5	2026-01-03
125	1006	2	5	2026-01-03
126	1006	3	5	2026-01-03
127	1009	1	5	2026-01-03
128	1009	2	5	2026-01-03
129	1009	3	5	2026-01-03
130	1011	1	5	2026-01-03
131	1011	2	5	2026-01-03
132	1011	3	5	2026-01-03
136	9999	1	5	2026-01-03
137	9999	2	5	2026-01-03
138	9999	3	5	2026-01-03
139	12345	1	6	2026-01-03
140	12345	2	6	2026-01-03
142	12345	1	8	2026-01-03
143	12345	2	8	2026-01-03
145	12345	1	10	2026-01-03
146	12345	2	10	2026-01-03
148	12346	1	6	2026-01-03
149	12346	2	6	2026-01-03
150	12346	3	6	2026-01-03
151	12346	1	8	2026-01-03
152	12346	2	8	2026-01-03
153	12346	3	8	2026-01-03
154	12346	1	10	2026-01-03
155	12346	2	10	2026-01-03
156	12346	3	10	2026-01-03
157	12347	1	6	2026-01-03
158	12347	2	6	2026-01-03
159	12347	3	6	2026-01-03
160	12347	1	8	2026-01-03
161	12347	2	8	2026-01-03
162	12347	3	8	2026-01-03
163	12347	1	10	2026-01-03
164	12347	2	10	2026-01-03
165	12347	3	10	2026-01-03
166	12348	1	6	2026-01-03
167	12348	2	6	2026-01-03
168	12348	3	6	2026-01-03
169	12348	1	8	2026-01-03
170	12348	2	8	2026-01-03
171	12348	3	8	2026-01-03
172	12348	1	10	2026-01-03
173	12348	2	10	2026-01-03
174	12348	3	10	2026-01-03
175	12349	1	6	2026-01-03
176	12349	2	6	2026-01-03
177	12349	3	6	2026-01-03
178	12349	1	8	2026-01-03
179	12349	2	8	2026-01-03
180	12349	3	8	2026-01-03
181	12349	1	10	2026-01-03
182	12349	2	10	2026-01-03
183	12349	3	10	2026-01-03
184	12350	1	6	2026-01-03
185	12350	2	6	2026-01-03
186	12350	3	6	2026-01-03
187	12350	1	8	2026-01-03
188	12350	2	8	2026-01-03
189	12350	3	8	2026-01-03
190	12350	1	10	2026-01-03
191	12350	2	10	2026-01-03
192	12350	3	10	2026-01-03
202	1002	1	6	2026-01-03
203	1002	2	6	2026-01-03
204	1002	3	6	2026-01-03
205	1002	1	8	2026-01-03
206	1002	2	8	2026-01-03
207	1002	3	8	2026-01-03
208	1002	1	10	2026-01-03
209	1002	2	10	2026-01-03
210	1002	3	10	2026-01-03
211	1005	1	6	2026-01-03
212	1005	2	6	2026-01-03
213	1005	3	6	2026-01-03
214	1005	1	8	2026-01-03
215	1005	2	8	2026-01-03
216	1005	3	8	2026-01-03
217	1005	1	10	2026-01-03
218	1005	2	10	2026-01-03
219	1005	3	10	2026-01-03
220	1006	1	6	2026-01-03
221	1006	2	6	2026-01-03
222	1006	3	6	2026-01-03
223	1006	1	8	2026-01-03
224	1006	2	8	2026-01-03
225	1006	3	8	2026-01-03
226	1006	1	10	2026-01-03
227	1006	2	10	2026-01-03
228	1006	3	10	2026-01-03
229	1009	1	6	2026-01-03
230	1009	2	6	2026-01-03
231	1009	3	6	2026-01-03
232	1009	1	8	2026-01-03
233	1009	2	8	2026-01-03
234	1009	3	8	2026-01-03
235	1009	1	10	2026-01-03
236	1009	2	10	2026-01-03
237	1009	3	10	2026-01-03
238	1011	1	6	2026-01-03
239	1011	2	6	2026-01-03
240	1011	3	6	2026-01-03
241	1011	1	8	2026-01-03
242	1011	2	8	2026-01-03
243	1011	3	8	2026-01-03
244	1011	1	10	2026-01-03
245	1011	2	10	2026-01-03
246	1011	3	10	2026-01-03
256	9999	1	6	2026-01-03
257	9999	2	6	2026-01-03
258	9999	3	6	2026-01-03
259	9999	1	8	2026-01-03
260	9999	2	8	2026-01-03
261	9999	3	8	2026-01-03
262	9999	1	10	2026-01-03
263	9999	2	10	2026-01-03
264	9999	3	10	2026-01-03
265	1015	4	11	2026-01-03
266	1014	4	11	2026-01-03
267	1013	4	11	2026-01-03
268	1010	4	11	2026-01-03
269	1015	5	11	2026-01-03
270	1014	5	11	2026-01-03
271	1013	5	11	2026-01-03
272	1010	5	11	2026-01-03
273	1015	6	11	2026-01-03
274	1014	6	11	2026-01-03
275	1013	6	11	2026-01-03
276	1010	6	11	2026-01-03
277	1008	1	11	2026-01-03
278	1007	1	11	2026-01-03
279	1004	1	11	2026-01-03
280	1003	1	11	2026-01-03
281	1008	2	11	2026-01-03
282	1007	2	11	2026-01-03
283	1004	2	11	2026-01-03
284	1003	2	11	2026-01-03
285	1008	3	11	2026-01-03
286	1007	3	11	2026-01-03
287	1004	3	11	2026-01-03
288	1003	3	11	2026-01-03
289	1015	4	12	2026-01-03
290	1014	4	12	2026-01-03
291	1013	4	12	2026-01-03
292	1010	4	12	2026-01-03
293	1015	5	12	2026-01-03
294	1014	5	12	2026-01-03
295	1013	5	12	2026-01-03
296	1010	5	12	2026-01-03
297	1015	6	12	2026-01-03
298	1014	6	12	2026-01-03
299	1013	6	12	2026-01-03
300	1010	6	12	2026-01-03
301	1008	1	13	2026-01-03
302	1007	1	13	2026-01-03
303	1004	1	13	2026-01-03
304	1003	1	13	2026-01-03
305	1008	2	13	2026-01-03
306	1007	2	13	2026-01-03
307	1004	2	13	2026-01-03
308	1003	2	13	2026-01-03
309	1008	3	13	2026-01-03
310	1007	3	13	2026-01-03
311	1004	3	13	2026-01-03
312	1003	3	13	2026-01-03
313	1015	4	14	2026-01-03
314	1014	4	14	2026-01-03
315	1013	4	14	2026-01-03
316	1010	4	14	2026-01-03
317	1015	5	14	2026-01-03
318	1014	5	14	2026-01-03
319	1013	5	14	2026-01-03
320	1010	5	14	2026-01-03
321	1015	6	14	2026-01-03
322	1014	6	14	2026-01-03
323	1013	6	14	2026-01-03
324	1010	6	14	2026-01-03
325	1008	1	15	2026-01-03
326	1007	1	15	2026-01-03
327	1004	1	15	2026-01-03
328	1003	1	15	2026-01-03
329	1008	2	15	2026-01-03
330	1007	2	15	2026-01-03
331	1004	2	15	2026-01-03
332	1003	2	15	2026-01-03
333	1008	3	15	2026-01-03
334	1007	3	15	2026-01-03
335	1004	3	15	2026-01-03
336	1003	3	15	2026-01-03
337	1008	1	16	2026-01-03
338	1007	1	16	2026-01-03
339	1004	1	16	2026-01-03
340	1003	1	16	2026-01-03
341	1008	2	16	2026-01-03
342	1007	2	16	2026-01-03
343	1004	2	16	2026-01-03
344	1003	2	16	2026-01-03
345	1008	3	16	2026-01-03
346	1007	3	16	2026-01-03
347	1004	3	16	2026-01-03
348	1003	3	16	2026-01-03
349	1015	4	17	2026-01-03
350	1014	4	17	2026-01-03
351	1013	4	17	2026-01-03
352	1010	4	17	2026-01-03
353	1015	5	17	2026-01-03
354	1014	5	17	2026-01-03
355	1013	5	17	2026-01-03
356	1010	5	17	2026-01-03
357	1015	6	17	2026-01-03
358	1014	6	17	2026-01-03
359	1013	6	17	2026-01-03
360	1010	6	17	2026-01-03
361	1008	1	18	2026-01-03
362	1007	1	18	2026-01-03
363	1004	1	18	2026-01-03
364	1003	1	18	2026-01-03
365	1008	2	18	2026-01-03
366	1007	2	18	2026-01-03
367	1004	2	18	2026-01-03
368	1003	2	18	2026-01-03
369	1008	3	18	2026-01-03
370	1007	3	18	2026-01-03
371	1004	3	18	2026-01-03
372	1003	3	18	2026-01-03
373	1015	4	19	2026-01-03
374	1014	4	19	2026-01-03
375	1013	4	19	2026-01-03
376	1010	4	19	2026-01-03
377	1015	5	19	2026-01-03
378	1014	5	19	2026-01-03
379	1013	5	19	2026-01-03
380	1010	5	19	2026-01-03
381	1015	6	19	2026-01-03
382	1014	6	19	2026-01-03
383	1013	6	19	2026-01-03
384	1010	6	19	2026-01-03
385	1008	1	20	2026-01-03
386	1007	1	20	2026-01-03
387	1004	1	20	2026-01-03
388	1003	1	20	2026-01-03
389	1008	2	20	2026-01-03
390	1007	2	20	2026-01-03
391	1004	2	20	2026-01-03
392	1003	2	20	2026-01-03
393	1008	3	20	2026-01-03
394	1007	3	20	2026-01-03
395	1004	3	20	2026-01-03
396	1003	3	20	2026-01-03
397	1015	4	21	2026-01-03
398	1014	4	21	2026-01-03
399	1013	4	21	2026-01-03
400	1010	4	21	2026-01-03
401	1015	5	21	2026-01-03
402	1014	5	21	2026-01-03
403	1013	5	21	2026-01-03
404	1010	5	21	2026-01-03
405	1015	6	21	2026-01-03
406	1014	6	21	2026-01-03
407	1013	6	21	2026-01-03
408	1010	6	21	2026-01-03
409	12358	1	1	2026-01-03
410	12357	1	1	2026-01-03
411	12356	1	1	2026-01-03
412	12355	1	1	2026-01-03
413	12354	1	1	2026-01-03
414	12353	1	1	2026-01-03
415	12352	1	1	2026-01-03
416	12351	1	1	2026-01-03
417	12358	1	10	2026-01-03
418	12357	1	10	2026-01-03
419	12356	1	10	2026-01-03
420	12355	1	10	2026-01-03
421	12354	1	10	2026-01-03
422	12353	1	10	2026-01-03
423	12352	1	10	2026-01-03
424	12351	1	10	2026-01-03
425	12358	2	10	2026-01-03
426	12357	2	10	2026-01-03
427	12356	2	10	2026-01-03
428	12355	2	10	2026-01-03
429	12354	2	10	2026-01-03
430	12353	2	10	2026-01-03
431	12352	2	10	2026-01-03
432	12351	2	10	2026-01-03
433	12358	3	10	2026-01-03
434	12357	3	10	2026-01-03
435	12356	3	10	2026-01-03
436	12355	3	10	2026-01-03
437	12354	3	10	2026-01-03
438	12353	3	10	2026-01-03
439	12352	3	10	2026-01-03
440	12351	3	10	2026-01-03
441	12358	2	1	2026-01-03
442	12357	2	1	2026-01-03
443	12356	2	1	2026-01-03
444	12355	2	1	2026-01-03
445	12354	2	1	2026-01-03
446	12353	2	1	2026-01-03
447	12352	2	1	2026-01-03
448	12351	2	1	2026-01-03
449	12358	3	1	2026-01-03
450	12357	3	1	2026-01-03
451	12356	3	1	2026-01-03
452	12355	3	1	2026-01-03
453	12354	3	1	2026-01-03
454	12353	3	1	2026-01-03
455	12352	3	1	2026-01-03
456	12351	3	1	2026-01-03
457	12358	1	3	2026-01-03
458	12357	1	3	2026-01-03
459	12356	1	3	2026-01-03
460	12355	1	3	2026-01-03
461	12354	1	3	2026-01-03
462	12353	1	3	2026-01-03
463	12352	1	3	2026-01-03
464	12351	1	3	2026-01-03
465	12358	2	3	2026-01-03
466	12357	2	3	2026-01-03
467	12356	2	3	2026-01-03
468	12355	2	3	2026-01-03
469	12354	2	3	2026-01-03
470	12353	2	3	2026-01-03
471	12352	2	3	2026-01-03
472	12351	2	3	2026-01-03
473	12358	3	3	2026-01-03
474	12357	3	3	2026-01-03
475	12356	3	3	2026-01-03
476	12355	3	3	2026-01-03
477	12354	3	3	2026-01-03
478	12353	3	3	2026-01-03
479	12352	3	3	2026-01-03
480	12351	3	3	2026-01-03
481	12358	1	5	2026-01-03
482	12357	1	5	2026-01-03
483	12356	1	5	2026-01-03
484	12355	1	5	2026-01-03
485	12354	1	5	2026-01-03
486	12353	1	5	2026-01-03
487	12352	1	5	2026-01-03
488	12351	1	5	2026-01-03
489	12358	2	5	2026-01-03
490	12357	2	5	2026-01-03
491	12356	2	5	2026-01-03
492	12355	2	5	2026-01-03
493	12354	2	5	2026-01-03
494	12353	2	5	2026-01-03
495	12352	2	5	2026-01-03
496	12351	2	5	2026-01-03
497	12358	3	5	2026-01-03
498	12357	3	5	2026-01-03
499	12356	3	5	2026-01-03
500	12355	3	5	2026-01-03
501	12354	3	5	2026-01-03
502	12353	3	5	2026-01-03
503	12352	3	5	2026-01-03
504	12351	3	5	2026-01-03
505	12358	1	6	2026-01-03
506	12357	1	6	2026-01-03
507	12356	1	6	2026-01-03
508	12355	1	6	2026-01-03
509	12354	1	6	2026-01-03
510	12353	1	6	2026-01-03
511	12352	1	6	2026-01-03
512	12351	1	6	2026-01-03
513	12358	2	6	2026-01-03
514	12357	2	6	2026-01-03
515	12356	2	6	2026-01-03
516	12355	2	6	2026-01-03
517	12354	2	6	2026-01-03
518	12353	2	6	2026-01-03
519	12352	2	6	2026-01-03
520	12351	2	6	2026-01-03
521	12358	3	6	2026-01-03
522	12357	3	6	2026-01-03
523	12356	3	6	2026-01-03
524	12355	3	6	2026-01-03
525	12354	3	6	2026-01-03
526	12353	3	6	2026-01-03
527	12352	3	6	2026-01-03
528	12351	3	6	2026-01-03
529	12358	1	8	2026-01-03
530	12357	1	8	2026-01-03
531	12356	1	8	2026-01-03
532	12355	1	8	2026-01-03
533	12354	1	8	2026-01-03
534	12353	1	8	2026-01-03
535	12352	1	8	2026-01-03
536	12351	1	8	2026-01-03
537	12358	2	8	2026-01-03
538	12357	2	8	2026-01-03
539	12356	2	8	2026-01-03
540	12355	2	8	2026-01-03
541	12354	2	8	2026-01-03
542	12353	2	8	2026-01-03
543	12352	2	8	2026-01-03
544	12351	2	8	2026-01-03
545	12358	3	8	2026-01-03
546	12357	3	8	2026-01-03
547	12356	3	8	2026-01-03
548	12355	3	8	2026-01-03
549	12354	3	8	2026-01-03
550	12353	3	8	2026-01-03
551	12352	3	8	2026-01-03
552	12351	3	8	2026-01-03
553	12364	4	11	2026-01-03
554	12363	4	11	2026-01-03
555	12362	4	11	2026-01-03
556	12361	4	11	2026-01-03
557	12360	4	11	2026-01-03
558	12359	4	11	2026-01-03
559	12364	5	11	2026-01-03
560	12363	5	11	2026-01-03
561	12362	5	11	2026-01-03
562	12361	5	11	2026-01-03
563	12360	5	11	2026-01-03
564	12359	5	11	2026-01-03
565	12364	6	11	2026-01-03
566	12363	6	11	2026-01-03
567	12362	6	11	2026-01-03
568	12361	6	11	2026-01-03
569	12360	6	11	2026-01-03
570	12359	6	11	2026-01-03
571	12364	4	12	2026-01-03
572	12363	4	12	2026-01-03
573	12362	4	12	2026-01-03
574	12361	4	12	2026-01-03
575	12360	4	12	2026-01-03
576	12359	4	12	2026-01-03
577	12364	5	12	2026-01-03
578	12363	5	12	2026-01-03
579	12362	5	12	2026-01-03
580	12361	5	12	2026-01-03
581	12360	5	12	2026-01-03
582	12359	5	12	2026-01-03
583	12364	6	12	2026-01-03
584	12363	6	12	2026-01-03
585	12362	6	12	2026-01-03
586	12361	6	12	2026-01-03
587	12360	6	12	2026-01-03
588	12359	6	12	2026-01-03
589	12364	4	14	2026-01-03
590	12363	4	14	2026-01-03
591	12362	4	14	2026-01-03
592	12361	4	14	2026-01-03
593	12360	4	14	2026-01-03
594	12359	4	14	2026-01-03
595	12364	5	14	2026-01-03
596	12363	5	14	2026-01-03
597	12362	5	14	2026-01-03
598	12361	5	14	2026-01-03
599	12360	5	14	2026-01-03
600	12359	5	14	2026-01-03
601	12364	6	14	2026-01-03
602	12363	6	14	2026-01-03
603	12362	6	14	2026-01-03
604	12361	6	14	2026-01-03
605	12360	6	14	2026-01-03
606	12359	6	14	2026-01-03
607	12364	4	17	2026-01-03
608	12363	4	17	2026-01-03
609	12362	4	17	2026-01-03
610	12361	4	17	2026-01-03
611	12360	4	17	2026-01-03
612	12359	4	17	2026-01-03
613	12364	5	17	2026-01-03
614	12363	5	17	2026-01-03
615	12362	5	17	2026-01-03
616	12361	5	17	2026-01-03
617	12360	5	17	2026-01-03
618	12359	5	17	2026-01-03
619	12364	6	17	2026-01-03
620	12363	6	17	2026-01-03
621	12362	6	17	2026-01-03
622	12361	6	17	2026-01-03
623	12360	6	17	2026-01-03
624	12359	6	17	2026-01-03
625	12364	4	19	2026-01-03
626	12363	4	19	2026-01-03
627	12362	4	19	2026-01-03
628	12361	4	19	2026-01-03
629	12360	4	19	2026-01-03
630	12359	4	19	2026-01-03
631	12364	5	19	2026-01-03
632	12363	5	19	2026-01-03
633	12362	5	19	2026-01-03
634	12361	5	19	2026-01-03
635	12360	5	19	2026-01-03
636	12359	5	19	2026-01-03
637	12364	6	19	2026-01-03
638	12363	6	19	2026-01-03
639	12362	6	19	2026-01-03
640	12361	6	19	2026-01-03
641	12360	6	19	2026-01-03
642	12359	6	19	2026-01-03
643	12364	4	21	2026-01-03
644	12363	4	21	2026-01-03
645	12362	4	21	2026-01-03
646	12361	4	21	2026-01-03
647	12360	4	21	2026-01-03
648	12359	4	21	2026-01-03
649	12364	5	21	2026-01-03
650	12363	5	21	2026-01-03
651	12362	5	21	2026-01-03
652	12361	5	21	2026-01-03
653	12360	5	21	2026-01-03
654	12359	5	21	2026-01-03
655	12364	6	21	2026-01-03
656	12363	6	21	2026-01-03
657	12362	6	21	2026-01-03
658	12361	6	21	2026-01-03
659	12360	6	21	2026-01-03
660	12359	6	21	2026-01-03
661	12345	17	1	2026-01-12
662	12345	4	4	2026-01-12
\.


--
-- TOC entry 3813 (class 0 OID 24641)
-- Dependencies: 232
-- Data for Name: inscrito_uc; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.inscrito_uc (n_mecanografico, id_unidadecurricular, estado) FROM stdin;
12345	1	t
12345	2	t
12345	3	t
12345	4	t
12345	5	t
12346	1	t
12346	2	t
12346	3	t
12346	4	t
12346	5	t
12347	1	t
12347	2	t
12347	3	t
12347	4	t
12347	5	t
12348	1	t
12348	2	t
12348	3	t
12348	4	t
12348	5	t
12349	1	t
12349	2	t
12349	3	t
12349	4	t
12349	5	t
12350	1	t
12350	2	t
12350	3	t
12350	4	t
12350	5	t
1002	1	t
1002	2	t
1002	3	t
1002	4	t
1002	5	t
1005	1	t
1005	2	t
1005	3	t
1005	4	t
1005	5	t
1006	1	t
1006	2	t
1006	3	t
1006	4	t
1006	5	t
1009	1	t
1009	2	t
1009	3	t
1009	4	t
1009	5	t
1011	1	t
1011	2	t
1011	3	t
1011	4	t
1011	5	t
9999	1	t
9999	2	t
9999	3	t
9999	4	t
9999	5	t
12345	6	t
12345	7	t
12345	8	t
12345	9	t
12345	10	t
12346	6	t
12346	7	t
12346	8	t
12346	9	t
12346	10	t
12347	6	t
12347	7	t
12347	8	t
12347	9	t
12347	10	t
12348	6	t
12348	7	t
12348	8	t
12348	9	t
12348	10	t
12349	6	t
12349	7	t
12349	8	t
12349	9	t
12349	10	t
12350	6	t
12350	7	t
12350	8	t
12350	9	t
12350	10	t
1002	6	t
1002	7	t
1002	8	t
1002	9	t
1002	10	t
1005	6	t
1005	7	t
1005	8	t
1005	9	t
1005	10	t
1006	6	t
1006	7	t
1006	8	t
1006	9	t
1006	10	t
1009	6	t
1009	7	t
1009	8	t
1009	9	t
1009	10	t
1011	6	t
1011	7	t
1011	8	t
1011	9	t
1011	10	t
9999	6	t
9999	7	t
9999	8	t
9999	9	t
9999	10	t
1003	11	t
1003	12	t
1003	13	t
1003	14	t
1003	15	t
1003	16	t
1003	17	t
1003	18	t
1003	19	t
1003	20	t
1003	21	t
1004	11	t
1004	12	t
1004	13	t
1004	14	t
1004	15	t
1004	16	t
1004	17	t
1004	18	t
1004	19	t
1004	20	t
1004	21	t
1007	11	t
1007	12	t
1007	13	t
1007	14	t
1007	15	t
1007	16	t
1007	17	t
1007	18	t
1007	19	t
1007	20	t
1007	21	t
1008	11	t
1008	12	t
1008	13	t
1008	14	t
1008	15	t
1008	16	t
1008	17	t
1008	18	t
1008	19	t
1008	20	t
1008	21	t
1010	11	t
1010	12	t
1010	13	t
1010	14	t
1010	15	t
1010	16	t
1010	17	t
1010	18	t
1010	19	t
1010	20	t
1010	21	t
1013	11	t
1013	12	t
1013	13	t
1013	14	t
1013	15	t
1013	16	t
1013	17	t
1013	18	t
1013	19	t
1013	20	t
1013	21	t
1014	11	t
1014	12	t
1014	13	t
1014	14	t
1014	15	t
1014	16	t
1014	17	t
1014	18	t
1014	19	t
1014	20	t
1014	21	t
1015	11	t
1015	12	t
1015	13	t
1015	14	t
1015	15	t
1015	16	t
1015	17	t
1015	18	t
1015	19	t
1015	20	t
1015	21	t
12351	1	t
12351	2	t
12351	3	t
12351	4	t
12351	5	t
12351	6	t
12351	7	t
12351	8	t
12351	9	t
12351	10	t
12352	1	t
12352	2	t
12352	3	t
12352	4	t
12352	5	t
12352	6	t
12352	7	t
12352	8	t
12352	9	t
12352	10	t
12353	1	t
12353	2	t
12353	3	t
12353	4	t
12353	5	t
12353	6	t
12353	7	t
12353	8	t
12353	9	t
12353	10	t
12354	1	t
12354	2	t
12354	3	t
12354	4	t
12354	5	t
12354	6	t
12354	7	t
12354	8	t
12354	9	t
12354	10	t
12355	1	t
12355	2	t
12355	3	t
12355	4	t
12355	5	t
12355	6	t
12355	7	t
12355	8	t
12355	9	t
12355	10	t
12356	1	t
12356	2	t
12356	3	t
12356	4	t
12356	5	t
12356	6	t
12356	7	t
12356	8	t
12356	9	t
12356	10	t
12357	1	t
12357	2	t
12357	3	t
12357	4	t
12357	5	t
12357	6	t
12357	7	t
12357	8	t
12357	9	t
12357	10	t
12358	1	t
12358	2	t
12358	3	t
12358	4	t
12358	5	t
12358	6	t
12358	7	t
12358	8	t
12358	9	t
12358	10	t
12359	11	t
12359	12	t
12359	13	t
12359	14	t
12359	15	t
12359	16	t
12359	17	t
12359	18	t
12359	19	t
12359	20	t
12359	21	t
12360	11	t
12360	12	t
12360	13	t
12360	14	t
12360	15	t
12360	16	t
12360	17	t
12360	18	t
12360	19	t
12360	20	t
12360	21	t
12361	11	t
12361	12	t
12361	13	t
12361	14	t
12361	15	t
12361	16	t
12361	17	t
12361	18	t
12361	19	t
12361	20	t
12361	21	t
12362	11	t
12362	12	t
12362	13	t
12362	14	t
12362	15	t
12362	16	t
12362	17	t
12362	18	t
12362	19	t
12362	20	t
12362	21	t
12363	11	t
12363	12	t
12363	13	t
12363	14	t
12363	15	t
12363	16	t
12363	17	t
12363	18	t
12363	19	t
12363	20	t
12363	21	t
12364	11	t
12364	12	t
12364	13	t
12364	14	t
12364	15	t
12364	16	t
12364	17	t
12364	18	t
12364	19	t
12364	20	t
12364	21	t
30001	32	t
30002	32	t
30003	32	t
30004	32	t
30005	32	t
30001	33	t
30002	33	t
30003	33	t
30004	33	t
30005	33	t
30001	34	t
30002	34	t
30003	34	t
30004	34	t
30005	34	t
30001	35	t
30002	35	t
30003	35	t
30004	35	t
30005	35	t
30001	36	t
30002	36	t
30003	36	t
30004	36	t
30005	36	t
30001	37	t
30002	37	t
30003	37	t
30004	37	t
30005	37	t
40001	1	t
40001	2	t
40001	3	t
40001	4	t
40001	5	t
40002	1	t
40002	3	t
40002	4	t
40002	5	t
\.


--
-- TOC entry 3814 (class 0 OID 24649)
-- Dependencies: 233
-- Data for Name: leciona_uc; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.leciona_uc (id_unidadecurricular, id_docente) FROM stdin;
1	1
\.


--
-- TOC entry 3848 (class 0 OID 163841)
-- Dependencies: 275
-- Data for Name: log_eventos; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.log_eventos (id_log, entidade, operacao, chave_primaria, detalhes, utilizador_db, data_hora) FROM stdin;
1	docente	INSERT	999	Docente criado: nome=Teste Docente, email=teste@ipv.pt, cargo=Professor	neondb_owner	2025-11-27 18:47:57.493551
2	aluno	INSERT	9999	Aluno criado: nome=David Teste, email=david.teste@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2025-11-27 18:56:27.954571
3	matricula	INSERT	12	Matrícula criada: n_mecanografico=9999, id_anoletivo=1, data_matricula=2025-11-27, estado=ativa	neondb_owner	2025-11-27 18:56:31.709223
4	turno	CREATE	9	Turno criado: Pratico (nº 4)		2025-12-12 20:04:53.320659
5	turno	CREATE	10	Turno criado: Pratico (nº 4)		2025-12-12 20:04:59.320011
6	turno	CREATE	11	Turno criado: Pratico (nº 4)		2025-12-12 20:06:52.725261
7	turno	CREATE	12	Turno criado: Pratico (nº 4)		2025-12-12 20:06:56.380722
8	turno	CREATE	13	Turno criado: Pratico (nº 4)		2025-12-12 20:07:00.779732
9	turno	CREATE	14	Turno criado: Pratico (nº 4)		2025-12-12 20:09:54.36904
10	turno	DELETE	None	Turno apagado: Pratico (nº 4)		2025-12-13 16:59:51.570357
11	matricula	INSERT	14	Matrícula criada: n_mecanografico=12345, id_anoletivo=1, data_matricula=2025-12-14, estado=true	neondb_owner	2025-12-14 13:47:58.08721
12	turno	DELETE	None	Turno apagado: Pratico (nº 4)	admin	2025-12-22 14:56:12.916659
13	aluno	INSERT	12351	Aluno criado: nome=João Pedro Silva, email=joao.silva@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
14	aluno	INSERT	12352	Aluno criado: nome=Maria Santos Costa, email=maria.costa@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
15	aluno	INSERT	12353	Aluno criado: nome=Pedro Almeida Rocha, email=pedro.rocha@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
16	aluno	INSERT	12354	Aluno criado: nome=Sofia Rodrigues Lima, email=sofia.lima@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
17	aluno	INSERT	12355	Aluno criado: nome=André Ferreira Santos, email=andre.santos@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
18	aluno	INSERT	12356	Aluno criado: nome=Beatriz Oliveira Sousa, email=beatriz.sousa@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
19	aluno	INSERT	12357	Aluno criado: nome=Ricardo Martins Pinto, email=ricardo.pinto@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
20	aluno	INSERT	12358	Aluno criado: nome=Inês Cardoso Lopes, email=ines.lopes@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-03 15:43:18.286272
21	aluno	INSERT	12359	Aluno criado: nome=Miguel Teixeira Cruz, email=miguel.cruz@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
22	aluno	INSERT	12360	Aluno criado: nome=Carolina Nunes Dias, email=carolina.dias@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
23	aluno	INSERT	12361	Aluno criado: nome=Tiago Moreira Gomes, email=tiago.gomes@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
24	aluno	INSERT	12362	Aluno criado: nome=Leonor Pereira Ramos, email=leonor.ramos@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
25	aluno	INSERT	12363	Aluno criado: nome=Gonçalo Ribeiro Castro, email=goncalo.castro@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
26	aluno	INSERT	12364	Aluno criado: nome=Mariana Soares Melo, email=mariana.melo@alunos.ipv.pt, id_curso=1, id_anocurricular=2	neondb_owner	2026-01-03 15:43:18.286272
27	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações	admin	2026-01-11 19:17:52.186616
28	aluno	INSERT	30001	Aluno criado: nome=João Silva TDM, email=joao.silva.tdm@ipv.pt, id_curso=2, id_anocurricular=1	neondb_owner	2026-01-11 20:01:32.524629
29	aluno	INSERT	30002	Aluno criado: nome=Maria Santos TDM, email=maria.santos.tdm@ipv.pt, id_curso=2, id_anocurricular=1	neondb_owner	2026-01-11 20:01:32.524629
30	aluno	INSERT	30003	Aluno criado: nome=Pedro Costa TDM, email=pedro.costa.tdm@ipv.pt, id_curso=2, id_anocurricular=1	neondb_owner	2026-01-11 20:01:32.524629
31	aluno	INSERT	30004	Aluno criado: nome=Ana Oliveira TDM, email=ana.oliveira.tdm@ipv.pt, id_curso=2, id_anocurricular=1	neondb_owner	2026-01-11 20:01:32.524629
32	aluno	INSERT	30005	Aluno criado: nome=Carlos Pereira TDM, email=carlos.pereira.tdm@ipv.pt, id_curso=2, id_anocurricular=1	neondb_owner	2026-01-11 20:01:32.524629
33	aluno	INSERT	30101	Aluno criado: nome=Sofia Rodrigues TDM, email=sofia.rodrigues.tdm@ipv.pt, id_curso=2, id_anocurricular=2	neondb_owner	2026-01-11 20:01:32.634434
34	aluno	INSERT	30102	Aluno criado: nome=Miguel Ferreira TDM, email=miguel.ferreira.tdm@ipv.pt, id_curso=2, id_anocurricular=2	neondb_owner	2026-01-11 20:01:32.634434
35	aluno	INSERT	30103	Aluno criado: nome=Beatriz Alves TDM, email=beatriz.alves.tdm@ipv.pt, id_curso=2, id_anocurricular=2	neondb_owner	2026-01-11 20:01:32.634434
36	aluno	INSERT	30104	Aluno criado: nome=Ricardo Martins TDM, email=ricardo.martins.tdm@ipv.pt, id_curso=2, id_anocurricular=2	neondb_owner	2026-01-11 20:01:32.634434
37	aluno	INSERT	30105	Aluno criado: nome=Inês Carvalho TDM, email=ines.carvalho.tdm@ipv.pt, id_curso=2, id_anocurricular=2	neondb_owner	2026-01-11 20:01:32.634434
38	aluno	INSERT	30201	Aluno criado: nome=Tiago Sousa TDM, email=tiago.sousa.tdm@ipv.pt, id_curso=2, id_anocurricular=3	neondb_owner	2026-01-11 20:01:32.695495
39	aluno	INSERT	30202	Aluno criado: nome=Catarina Lopes TDM, email=catarina.lopes.tdm@ipv.pt, id_curso=2, id_anocurricular=3	neondb_owner	2026-01-11 20:01:32.695495
40	aluno	INSERT	30203	Aluno criado: nome=Bruno Fernandes TDM, email=bruno.fernandes.tdm@ipv.pt, id_curso=2, id_anocurricular=3	neondb_owner	2026-01-11 20:01:32.695495
41	aluno	INSERT	30204	Aluno criado: nome=Laura Gonçalves TDM, email=laura.goncalves.tdm@ipv.pt, id_curso=2, id_anocurricular=3	neondb_owner	2026-01-11 20:01:32.695495
42	aluno	INSERT	30205	Aluno criado: nome=André Ribeiro TDM, email=andre.ribeiro.tdm@ipv.pt, id_curso=2, id_anocurricular=3	neondb_owner	2026-01-11 20:01:32.695495
43	turno	CREATE	17	Turno criado para UC Análise Matemática	admin	2026-01-11 23:56:44.325558
44	user_admin	UPDATE	1	Campos alterados: username=ana, email=ana@email.com	admin	2026-01-14 13:40:09.57562
45	user_admin	UPDATE	1	Campos alterados: username=ana, email=ana@email.com	admin	2026-01-14 13:40:58.567651
46	user_aluno	DELETE	1001	Utilizador apagado: Ana Silva (Tipo: Aluno)	admin	2026-01-14 14:09:23.058315
47	user_aluno	DELETE	1001	Utilizador apagado: Ana Silva (Tipo: Aluno)	admin	2026-01-14 14:10:07.87323
48	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações 1ºano - TDM	admin	2026-01-14 23:16:20.044909
49	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações	admin	2026-01-14 23:25:08.472297
50	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações	admin	2026-01-14 23:30:22.480995
51	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - EI - 1º ano	admin	2026-01-15 13:26:48.504106
52	avaliacao_pdf	DELETE	3	Avaliação PDF apagada: Calendário de Avaliações	admin	2026-01-15 13:27:38.844998
53	avaliacao_pdf	DELETE	1	Avaliação PDF apagada: Calendário de Avaliações	admin	2026-01-15 13:27:43.734709
54	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - EI - 2º ano	admin	2026-01-15 13:28:10.106745
55	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - EI - 3º ano	admin	2026-01-15 13:28:29.232289
56	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - TDM - 2º ano	admin	2026-01-15 13:29:01.259652
57	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - TDM - 3º ano	admin	2026-01-15 13:29:30.055688
58	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - EISI - 1º ano	admin	2026-01-15 15:29:20.932717
59	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - EISI - 2º ano	admin	2026-01-15 15:31:13.985525
60	avaliacao_pdf	UPDATE	2	Avaliação PDF atualizada: Calendário de Avaliações 1ºano - TDM	admin	2026-01-15 20:32:13.522281
61	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - RSI - 1º ano	admin	2026-01-15 20:33:24.553764
62	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - RSI - 2º ano	admin	2026-01-15 20:33:56.849722
63	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - DWDM - 1º ano	admin	2026-01-15 21:38:35.294636
64	avaliacao_pdf	CREATE	novo	Avaliação PDF criada: Calendário de Avaliações - DWDM - 2º ano	admin	2026-01-15 21:39:01.797879
65	avaliacao_pdf	CREATE	696963977cea6790752fb255	Avaliação PDF criada no MongoDB: Calendário de Avaliações EI 2	admin	2026-01-15 22:00:56.544939
66	avaliacao_pdf	UPDATE	16	Avaliação PDF atualizada: Calendário de Avaliações EI 2	admin	2026-01-15 22:05:38.949521
67	horario_pdf	CREATE	69696a43e72c48a041d998f9	Horário PDF criado no MongoDB: Horario1 EI	admin	2026-01-15 22:29:32.984397
68	turno	CREATE	18	Turno criado: P (nº 7)	admin	2026-01-19 17:20:17.161672
69	turno	UPDATE	18	Turno atualizado: P (nº 7)	admin	2026-01-19 17:20:29.942137
70	turno	UPDATE	18	Turno atualizado: P (nº 7)	admin	2026-01-19 17:22:24.051868
71	turno	DELETE	None	Turno apagado: P (nº 7)	admin	2026-01-19 17:22:55.609431
72	user_aluno	UPDATE	1012	Campos alterados: username=Miguel Santa, email=miguel.santos@email.pt	admin	2026-01-19 17:38:39.412029
73	user_aluno	DELETE	1012	Utilizador apagado: Miguel Santa (Tipo: Aluno)	admin	2026-01-19 17:38:54.210036
74	turno	CREATE	19	Turno criado: T (nº 7)	admin	2026-01-19 17:40:10.947646
75	turno	UPDATE	19	Turno atualizado: T (nº 75)	admin	2026-01-19 17:40:34.323113
76	turno	UPDATE	19	Turno atualizado: TP (nº 75)	admin	2026-01-19 17:40:41.824618
77	turno	DELETE	None	Turno apagado: TP (nº 75)	admin	2026-01-19 17:40:48.377615
78	turno	DELETE	None	Turno apagado: Pratico (nº 4)	admin	2026-01-19 17:41:06.343722
79	turno	DELETE	None	Turno apagado: Pratico (nº 4)	admin	2026-01-19 17:41:08.9557
80	turno	DELETE	None	Turno apagado: Pratico (nº 4)	admin	2026-01-19 17:41:11.750506
81	turno	DELETE	None	Turno apagado: Pratico (nº 4)	admin	2026-01-19 17:41:14.845449
82	avaliacao_pdf	CREATE	696e7042352f3dd233e4f03d	Avaliação PDF criada no MongoDB: Calendário de Avaliações teste	admin	2026-01-19 17:56:18.862921
83	avaliacao_pdf	UPDATE	17	Avaliação PDF atualizada: Calendário de Avaliações teste	admin	2026-01-19 17:56:57.428275
84	avaliacao_pdf	DELETE	17	Avaliação PDF apagada do MongoDB: Calendário de Avaliações teste	admin	2026-01-19 18:01:33.359921
85	unidade_curricular	CREATE	114	UC criada: Teste	admin	2026-01-19 18:08:16.910419
86	turno	CREATE	20	Turno criado para UC Teste	admin	2026-01-19 18:09:22.248077
87	turno	UPDATE	20	Turno atualizado para UC Teste	admin	2026-01-19 18:09:33.798317
88	turno	CREATE	21	Turno criado para UC Teste	admin	2026-01-19 18:14:30.500556
89	turno	DELETE	20	Turno removido da UC Teste	admin	2026-01-19 18:14:38.632638
90	unidade_curricular	UPDATE	114	UC atualizada: Teste1	admin	2026-01-19 18:14:56.169244
91	turno	DELETE	21	Turno removido da UC Teste1	admin	2026-01-19 18:15:19.791842
92	unidade_curricular	UPDATE	114	UC atualizada: Teste1	admin	2026-01-19 18:15:23.505459
93	unidade_curricular	DELETE	None	UC apagada: Teste1	admin	2026-01-19 18:15:29.380798
94	unidade_curricular	CREATE	115	UC criada: TESTE	admin	2026-01-19 18:18:46.708088
95	turno	CREATE	22	Turno criado para UC TESTE	admin	2026-01-19 18:19:15.14177
96	unidade_curricular	UPDATE	115	UC atualizada: TESTE	admin	2026-01-19 18:19:18.82243
97	unidade_curricular	DELETE	None	UC apagada: TESTE (e 1 turnos associados)	admin	2026-01-19 18:19:25.384807
98	user_admin	CREATE	6	Novo utilizador criado: Patricia (po@ipv.pt)	admin	2026-01-19 18:21:08.627818
99	user_admin	DELETE	6	Utilizador apagado: Patricia (Tipo: Admin)		2026-01-19 18:21:32.271333
100	horario_pdf	CREATE	696e76563644be914bac95d1	Horário PDF criado no MongoDB: Horário do 1º ano - EI		2026-01-19 18:22:16.420579
101	horario_pdf	CREATE	696e76733644be914bac95d5	Horário PDF criado no MongoDB: Horário do 2º ano - EI	admin	2026-01-19 18:22:44.731357
102	horario_pdf	CREATE	696e76ac3644be914bac95dd	Horário PDF criado no MongoDB: Horário do 3º ano - EI	admin	2026-01-19 18:23:41.06133
103	horario_pdf	CREATE	696e76e03644be914bac95e1	Horário PDF criado no MongoDB: Horário do 1º ano - TDM		2026-01-19 18:24:33.741286
104	horario_pdf	CREATE	696e77093644be914bac95e5	Horário PDF criado no MongoDB: Horário do 2º ano - TDM	admin	2026-01-19 18:25:14.542415
105	horario_pdf	CREATE	696e77243644be914bac95ea	Horário PDF criado no MongoDB: Horário do 3º ano - TDM	admin	2026-01-19 18:25:41.241866
106	horario_pdf	CREATE	696e774e3644be914bac95ee	Horário PDF criado no MongoDB: Horário do 1º ano - EISI	admin	2026-01-19 18:26:23.619449
107	horario_pdf	CREATE	696e77703644be914bac95f3	Horário PDF criado no MongoDB: Horário do 2º ano - EISI	admin	2026-01-19 18:26:57.938747
108	horario_pdf	CREATE	696e779b3644be914bac95f7	Horário PDF criado no MongoDB: Horário do 1º ano - RSI	admin	2026-01-19 18:27:40.79936
109	horario_pdf	CREATE	696e77ae3644be914bac95fb	Horário PDF criado no MongoDB: Horário do 2º ano - RSI	admin	2026-01-19 18:27:59.022203
110	horario_pdf	CREATE	696e77f93644be914bac95ff	Horário PDF criado no MongoDB: Horário do 1º ano - DWDM	admin	2026-01-19 18:29:14.613695
111	horario_pdf	CREATE	696e780e3644be914bac9603	Horário PDF criado no MongoDB: Horário do 2º ano - DWDM	admin	2026-01-19 18:29:35.668419
112	avaliacao_pdf	DELETE	16	Avaliação PDF apagada do MongoDB: Calendário de Avaliações EI 2	admin	2026-01-19 18:30:33.042038
113	avaliacao_pdf	DELETE	15	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - DWDM - 2º ano	admin	2026-01-19 18:30:36.410598
114	avaliacao_pdf	DELETE	14	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - DWDM - 1º ano	admin	2026-01-19 18:30:40.166091
115	avaliacao_pdf	DELETE	13	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - RSI - 2º ano	admin	2026-01-19 18:30:43.176996
116	avaliacao_pdf	DELETE	12	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - RSI - 1º ano	admin	2026-01-19 18:30:50.007315
117	avaliacao_pdf	DELETE	2	Avaliação PDF apagada do MongoDB: Calendário de Avaliações 1ºano - TDM	admin	2026-01-19 18:30:53.089689
118	avaliacao_pdf	DELETE	11	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - EISI - 2º ano	admin	2026-01-19 18:30:56.087704
119	avaliacao_pdf	DELETE	10	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - EISI - 1º ano	admin	2026-01-19 18:30:59.019012
120	avaliacao_pdf	DELETE	9	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - TDM - 3º ano	admin	2026-01-19 18:31:01.521301
121	avaliacao_pdf	DELETE	8	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - TDM - 2º ano	admin	2026-01-19 18:31:04.304125
122	avaliacao_pdf	DELETE	7	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - EI - 3º ano	admin	2026-01-19 18:31:06.94674
123	avaliacao_pdf	DELETE	6	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - EI - 2º ano	admin	2026-01-19 18:31:09.590993
124	avaliacao_pdf	DELETE	5	Avaliação PDF apagada do MongoDB: Calendário de Avaliações - EI - 1º ano	admin	2026-01-19 18:31:13.349305
125	avaliacao_pdf	DELETE	4	Avaliação PDF apagada do MongoDB: Calendário de Avaliações	admin	2026-01-19 18:31:16.029485
126	avaliacao_pdf	CREATE	696e788b3644be914bac9616	Avaliação PDF criada no MongoDB: Calendário de Avaliações - EI - 1º ano	admin	2026-01-19 18:31:40.002523
127	avaliacao_pdf	CREATE	696e78c83644be914bac961b	Avaliação PDF criada no MongoDB: Calendário de Avaliações - EI - 2º ano	admin	2026-01-19 18:32:40.637656
128	avaliacao_pdf	CREATE	696e78db3644be914bac961f	Avaliação PDF criada no MongoDB: Calendário de Avaliações - EI - 3º ano	admin	2026-01-19 18:32:59.824293
129	avaliacao_pdf	CREATE	696e79073644be914bac9623	Avaliação PDF criada no MongoDB: Calendário de Avaliações - TDM - 1º ano	admin	2026-01-19 18:33:44.289873
130	avaliacao_pdf	CREATE	696e791b3644be914bac9627	Avaliação PDF criada no MongoDB: Calendário de Avaliações - TDM - 2º ano	admin	2026-01-19 18:34:04.457899
131	avaliacao_pdf	CREATE	696e79483644be914bac962b	Avaliação PDF criada no MongoDB: Calendário de Avaliações - TDM - 3º ano	admin	2026-01-19 18:34:48.832649
132	avaliacao_pdf	CREATE	696e798d3644be914bac962f	Avaliação PDF criada no MongoDB: Calendário de Avaliações - EISI - 1º ano	admin	2026-01-19 18:35:58.172744
133	avaliacao_pdf	CREATE	696e79a73644be914bac9633	Avaliação PDF criada no MongoDB: Calendário de Avaliações - EISI - 2º ano	admin	2026-01-19 18:36:23.720218
134	avaliacao_pdf	CREATE	696e79d63644be914bac9637	Avaliação PDF criada no MongoDB: Calendário de Avaliações - RSI - 1º ano	admin	2026-01-19 18:37:11.272485
135	avaliacao_pdf	CREATE	696e7a093644be914bac963b	Avaliação PDF criada no MongoDB: Calendário de Avaliações - RSI - 2º ano	admin	2026-01-19 18:38:01.772454
136	avaliacao_pdf	CREATE	696e7a273644be914bac963f	Avaliação PDF criada no MongoDB: Calendário de Avaliações - DWDM - 1º ano	admin	2026-01-19 18:38:32.422132
137	avaliacao_pdf	CREATE	696e7a4a3644be914bac9643	Avaliação PDF criada no MongoDB: Calendário de Avaliações - DWDM - 2º ano	admin	2026-01-19 18:39:06.842291
138	turno	CREATE	23	Turno criado para UC Análise Matemática	admin	2026-01-19 20:10:55.804095
139	turno	DELETE	23	Turno removido da UC Análise Matemática	admin	2026-01-19 20:11:02.693029
140	unidade_curricular	CREATE	116	UC criada: teste	admin	2026-01-19 20:11:20.283152
141	turno	CREATE	24	Turno criado para UC teste	admin	2026-01-19 20:15:29.27658
142	unidade_curricular	UPDATE	116	UC atualizada: teste	admin	2026-01-19 20:15:35.020184
143	unidade_curricular	DELETE	None	UC apagada: teste (e 1 turnos associados)	admin	2026-01-19 20:15:43.371723
144	aluno	INSERT	40001	Aluno criado: nome=Sofia Martins Silva, email=sofia.martins@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-20 13:34:36.104614
145	matricula	INSERT	15	Matrícula criada: n_mecanografico=40001, id_anoletivo=1, data_matricula=2025-09-15, estado=ativa	neondb_owner	2026-01-20 13:34:36.104614
146	aluno	INSERT	40002	Aluno criado: nome=Ricardo Pereira Costa, email=ricardo.pereira@alunos.ipv.pt, id_curso=1, id_anocurricular=1	neondb_owner	2026-01-20 13:34:36.104614
147	matricula	INSERT	16	Matrícula criada: n_mecanografico=40002, id_anoletivo=1, data_matricula=2025-09-20, estado=ativa	neondb_owner	2026-01-20 13:34:36.104614
\.


--
-- TOC entry 3816 (class 0 OID 24658)
-- Dependencies: 235
-- Data for Name: matricula; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.matricula (id_matricula, id_anoletivo, n_mecanografico, data_matricula, estado) FROM stdin;
2	1	1002	2025-09-01	ativa
3	1	1003	2025-09-01	ativa
4	1	1004	2025-09-02	ativa
5	1	1005	2025-09-03	ativa
6	1	1006	2025-09-04	ativa
7	1	1007	2025-09-05	ativa
8	1	1008	2025-09-05	ativa
9	1	1009	2025-09-05	ativa
10	1	1010	2025-09-05	ativa
11	1	1011	2025-09-15	ativa
12	1	9999	2025-11-27	ativa
14	1	12345	2025-12-14	true
15	1	40001	2025-09-15	ativa
16	1	40002	2025-09-20	ativa
\.


--
-- TOC entry 3850 (class 0 OID 172033)
-- Dependencies: 277
-- Data for Name: pedido_troca_turno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.pedido_troca_turno (id_pedido, id_inscricao_solicitante, id_turno_desejado, id_inscricao_contraparte, estado, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3818 (class 0 OID 24668)
-- Dependencies: 237
-- Data for Name: semestre; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.semestre (id_semestre, semestre) FROM stdin;
1	1º semestre
2	2º semestre
3	3º semestre
\.


--
-- TOC entry 3820 (class 0 OID 24676)
-- Dependencies: 239
-- Data for Name: turno; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.turno (id_turno, n_turno, tipo, capacidade) FROM stdin;
1	1	T	100
2	1	TP	50
3	1	P	50
4	2	T	100
5	2	TP	50
6	2	P	50
7	3	TP	50
8	3	P	50
15	1	TP	30
16	2	TP	30
17	2	P	25
\.


--
-- TOC entry 3821 (class 0 OID 24683)
-- Dependencies: 240
-- Data for Name: turno_uc; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.turno_uc (id_turno, id_unidadecurricular, hora_inicio, hora_fim) FROM stdin;
1	1	09:00:00	11:00:00
1	10	09:00:00	11:00:00
2	10	09:00:00	11:00:00
3	10	09:00:00	11:00:00
4	11	09:00:00	11:00:00
5	11	09:00:00	11:00:00
6	11	09:00:00	11:00:00
2	1	14:00:00	16:00:00
3	1	16:00:00	18:00:00
4	2	11:00:00	13:00:00
5	2	09:00:00	11:00:00
6	2	11:00:00	13:00:00
1	3	14:00:00	16:00:00
2	3	09:00:00	11:00:00
3	3	14:00:00	16:00:00
4	4	09:00:00	11:00:00
5	4	14:00:00	17:00:00
6	4	09:00:00	12:00:00
1	5	16:00:00	18:00:00
2	5	11:00:00	13:00:00
3	5	09:00:00	11:00:00
1	6	08:00:00	10:00:00
2	6	10:00:00	12:00:00
3	6	14:00:00	16:00:00
4	7	10:00:00	12:00:00
5	7	14:00:00	16:00:00
6	7	16:00:00	18:00:00
1	8	14:00:00	16:00:00
2	8	16:00:00	18:00:00
3	8	10:00:00	12:00:00
4	9	08:00:00	10:00:00
5	9	10:00:00	13:00:00
6	9	14:00:00	17:00:00
4	10	14:00:00	16:00:00
5	10	08:00:00	11:00:00
6	10	08:00:00	11:00:00
1	11	09:00:00	11:00:00
2	11	14:00:00	17:00:00
3	11	09:00:00	12:00:00
4	12	11:00:00	13:00:00
5	12	09:00:00	12:00:00
6	12	14:00:00	17:00:00
1	13	14:00:00	16:00:00
2	13	14:00:00	16:00:00
3	13	09:00:00	11:00:00
4	14	08:00:00	10:00:00
5	14	10:00:00	13:00:00
6	14	11:00:00	14:00:00
1	15	16:00:00	18:00:00
2	15	16:00:00	18:00:00
3	15	14:00:00	16:00:00
1	16	08:00:00	10:00:00
2	16	10:00:00	12:00:00
3	16	14:00:00	16:00:00
4	17	10:00:00	12:00:00
5	17	14:00:00	16:00:00
6	17	16:00:00	18:00:00
1	18	14:00:00	16:00:00
2	18	08:00:00	10:00:00
3	18	10:00:00	12:00:00
4	19	16:00:00	18:00:00
5	19	10:00:00	12:00:00
6	19	14:00:00	16:00:00
1	20	08:00:00	10:00:00
2	20	14:00:00	16:00:00
3	20	16:00:00	18:00:00
4	21	14:00:00	16:00:00
5	21	16:00:00	19:00:00
6	21	08:00:00	11:00:00
1	22	09:00:00	11:00:00
2	22	11:00:00	13:00:00
3	22	09:00:00	11:00:00
4	23	11:00:00	13:00:00
5	23	14:00:00	16:00:00
6	23	11:00:00	13:00:00
1	24	14:00:00	16:00:00
2	24	16:00:00	18:00:00
3	24	14:00:00	16:00:00
4	25	08:00:00	10:00:00
5	25	09:00:00	11:00:00
6	25	16:00:00	18:00:00
1	26	16:00:00	18:00:00
2	26	14:00:00	16:00:00
3	26	09:00:00	11:00:00
4	27	10:00:00	12:00:00
5	27	14:00:00	16:00:00
6	27	11:00:00	13:00:00
1	28	08:00:00	10:00:00
2	28	10:00:00	12:00:00
3	28	14:00:00	16:00:00
4	29	10:00:00	12:00:00
5	29	14:00:00	17:00:00
6	29	16:00:00	19:00:00
1	30	14:00:00	16:00:00
2	30	08:00:00	10:00:00
3	30	10:00:00	12:00:00
17	1	20:30:00	22:00:00
\.


--
-- TOC entry 3823 (class 0 OID 24692)
-- Dependencies: 242
-- Data for Name: unidade_curricular; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.unidade_curricular (id_unidadecurricular, id_semestre, id_anocurricular, ects, nome, id_curso) FROM stdin;
1	1	1	6	Análise Matemática	1
2	1	1	5	Álgebra	1
3	1	1	6	Sistemas Digitais	1
4	1	1	8	Algoritmos e Programação	1
5	1	1	6	Tecnologias dos Computadores	1
6	2	1	6	Arquiteturas de Computador	1
7	2	1	5	Matemática Discreta	1
8	2	1	5	Matemática Aplicada	1
9	2	1	7	Redes de Comunicação I	1
10	2	1	8	Estruturas de Dados	1
11	1	2	7	Programação Orientada a Objetos	1
12	1	2	7	Análise de Sistemas	1
13	1	2	6	Sistemas Operativos	1
14	1	2	7	Aplicações para a Internet I	1
15	1	2	5	Usabilidade	1
16	2	2	5	Engenharia de Software I	1
17	2	2	6	Bases de Dados I	1
18	2	2	5	Aplicações para a Internet II	1
19	2	2	5	Redes de Comunicação II	1
20	2	2	5	Programação para Dispositivos Móveis	1
21	2	2	5	Projeto Integrado	1
22	1	3	5	Segurança Informática	1
23	1	3	5	Redes de Comunicação III	1
24	1	3	5	Complementos de Sistemas Operativos	1
25	1	3	6	Bases de Dados II	1
26	1	3	5	Sistemas Embebidos	1
27	1	3	5	Sistemas Distribuídos	1
28	2	3	5	Inteligência Artificial	1
29	2	3	6	Engenharia de Software II	1
30	2	3	3	Empreendedorismo e Gestão de Empresas	1
31	2	3	16	Projeto	1
32	1	1	6	Programação e Resolução de Problemas	2
33	1	1	5	Fundamentos Multimédia	2
34	1	1	5	Criatividade e Comunicação Multimédia	2
35	1	1	4	Psicologia da Percepção	2
36	1	1	7	Design Multimédia	2
37	1	1	4	Desenho e Representação	2
38	2	1	4	Fundamentos Matemáticos	2
39	2	1	6	Composição e Fotografia	2
40	2	1	6	Design de Interação I	2
41	2	1	5	Design de Identidade	2
42	2	1	6	Programação e Estruturas de Dados	2
43	2	1	5	Projeto Integrado I	2
44	1	2	5	Introdução às Redes e Serviços de Comunicação	2
45	1	2	6	Conteúdos Audiovisuais I	2
46	1	2	5	Design de Interação II	2
47	1	2	6	Aplicações para a Internet I	2
48	1	2	5	Programação Orientada a Objectos	2
49	1	2	5	Projeto Integrado II	2
50	2	2	5	Bases de Dados	2
51	2	2	6	Conteúdos Interativos	2
52	2	2	5	Animação	2
53	2	2	5	Conteúdos Audiovisuais II	2
54	2	2	6	Aplicações para a Internet II	2
55	2	2	5	Projeto Integrado III	2
56	1	3	6	Computação Gráfica	2
57	1	3	6	Aplicações de Base de Dados	2
58	1	3	6	Aplicações para a Internet III	2
59	1	3	7	Aplicações para Dispositivos Móveis	2
60	1	3	7	Projeto Integrado IV	2
61	2	3	7	Desenvolvimento de Jogos	2
62	2	3	4	Marketing Digital	2
63	2	3	5	Aplicações Avançadas Multimédia	2
64	2	3	15	Projeto	2
65	1	1	7	Iniciação à Informática	3
66	1	1	5	Cálculo	3
67	1	1	7	Introdução à Programação	3
68	1	1	3	Comportamento Humano das Organizações	3
69	1	1	8	Arquitecturas e Protocolos de Comunicação	3
70	2	1	3	Metodologias do Projeto	3
71	2	1	3	Estruturas Discretas	3
72	2	1	5	Arquitetura de Sistemas Computacionais	3
73	2	1	7	Sistemas Operativos	3
74	2	1	8	Administração e Gestão de Redes	3
75	2	1	4	Bases de Dados	3
76	1	2	3	Deontologia e Regulamentação Informática	3
77	1	2	5	Segurança em Redes e Sistemas Informáticos	3
78	1	2	6	Serviços Telemáticos	3
79	1	2	6	Complementos de Sistemas Operativos	3
80	1	2	6	Administração de Sistemas	3
81	1	2	6	Projeto Integrado	3
82	2	2	30	Estágio em Empresa	3
83	1	1	5	Design Gráfico	4
84	1	1	7	Introdução à Programação	4
85	1	1	5	Modelação e Bases de Dados	4
86	1	1	7	Programação e Serviços Web	4
87	1	1	7	Tecnologias de Mercado	4
88	1	1	7	Tecnologias Emergentes	4
89	1	1	6	Tecnologias para o Desenvolvimento Web	4
90	2	1	3	Gestão de Projetos de Software	4
91	2	1	6	Métodos Matemáticos	4
92	2	1	7	Técnicas Avançadas de Programação	4
93	1	2	7	Análise e Desenho de Software	4
94	1	2	3	Deontologia e Regulamentação Informática	4
95	1	2	6	Introdução às Tecnologias dos Computadores	4
96	1	2	7	Programação para Dispositivos Móveis	4
97	2	2	7	Design de Interação	4
98	2	2	30	Estágio	4
99	1	1	6	Análise e Inteligente de Dados	5
100	1	1	6	Design de Interfaces	5
101	1	1	6	Integração em Sistemas Inteligentes	5
102	1	1	6	Planeamento e Gestão de Projetos	5
103	1	1	6	Sistemas de Informação em Dispositivos Móveis	5
104	2	1	6	Administração e Exploração Avançada de Bases de Dados	5
105	2	1	6	Armazenamento e Processamento Analítico de Dados	5
106	2	1	6	Desenvolvimento para a Web	5
107	2	1	6	Gestão de Sistemas de Informação	5
108	2	1	6	Tecnologias e Gestão de Serviços	5
109	1	2	6	Introdução à Dissertação/Projeto/Estágio	5
110	2	2	48	Dissertação/Projeto/Estágio	5
\.


--
-- TOC entry 3846 (class 0 OID 139265)
-- Dependencies: 273
-- Data for Name: utilizador; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.utilizador (id, tipo, ativo, user_id) FROM stdin;
1	admin	t	1
2	aluno	t	5
\.


--
-- TOC entry 3961 (class 0 OID 0)
-- Dependencies: 220
-- Name: ano_curricular_id_anocurricular_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.ano_curricular_id_anocurricular_seq', 1, false);


--
-- TOC entry 3962 (class 0 OID 0)
-- Dependencies: 222
-- Name: ano_letivo_id_anoletivo_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.ano_letivo_id_anoletivo_seq', 1, true);


--
-- TOC entry 3963 (class 0 OID 0)
-- Dependencies: 286
-- Name: auditoria_inscricao_id_auditoria_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auditoria_inscricao_id_auditoria_seq', 4, true);


--
-- TOC entry 3964 (class 0 OID 0)
-- Dependencies: 249
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- TOC entry 3965 (class 0 OID 0)
-- Dependencies: 251
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- TOC entry 3966 (class 0 OID 0)
-- Dependencies: 247
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 148, true);


--
-- TOC entry 3967 (class 0 OID 0)
-- Dependencies: 255
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- TOC entry 3968 (class 0 OID 0)
-- Dependencies: 253
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 6, true);


--
-- TOC entry 3969 (class 0 OID 0)
-- Dependencies: 257
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- TOC entry 3970 (class 0 OID 0)
-- Dependencies: 288
-- Name: core_avaliacaopdf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.core_avaliacaopdf_id_seq', 29, true);


--
-- TOC entry 3971 (class 0 OID 0)
-- Dependencies: 270
-- Name: core_horariopdf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.core_horariopdf_id_seq', 31, true);


--
-- TOC entry 3972 (class 0 OID 0)
-- Dependencies: 278
-- Name: core_pedidotrocaturno_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.core_pedidotrocaturno_id_seq', 1, false);


--
-- TOC entry 3973 (class 0 OID 0)
-- Dependencies: 224
-- Name: curso_id_curso_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.curso_id_curso_seq', 1, false);


--
-- TOC entry 3974 (class 0 OID 0)
-- Dependencies: 259
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- TOC entry 3975 (class 0 OID 0)
-- Dependencies: 245
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 37, true);


--
-- TOC entry 3976 (class 0 OID 0)
-- Dependencies: 243
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 27, true);


--
-- TOC entry 3977 (class 0 OID 0)
-- Dependencies: 226
-- Name: docente_id_docente_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.docente_id_docente_seq', 20, true);


--
-- TOC entry 3978 (class 0 OID 0)
-- Dependencies: 280
-- Name: forum_inscricaoturno_id_inscricao_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.forum_inscricaoturno_id_inscricao_seq', 1, false);


--
-- TOC entry 3979 (class 0 OID 0)
-- Dependencies: 284
-- Name: forum_pedidotrocaturno_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.forum_pedidotrocaturno_id_seq', 1, false);


--
-- TOC entry 3980 (class 0 OID 0)
-- Dependencies: 282
-- Name: forum_turno_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.forum_turno_id_seq', 1, false);


--
-- TOC entry 3981 (class 0 OID 0)
-- Dependencies: 228
-- Name: horario_id_horario_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.horario_id_horario_seq', 1, true);


--
-- TOC entry 3982 (class 0 OID 0)
-- Dependencies: 230
-- Name: inscricao_turno_id_inscricao_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.inscricao_turno_id_inscricao_seq', 664, true);


--
-- TOC entry 3983 (class 0 OID 0)
-- Dependencies: 274
-- Name: log_eventos_id_log_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.log_eventos_id_log_seq', 147, true);


--
-- TOC entry 3984 (class 0 OID 0)
-- Dependencies: 234
-- Name: matricula_id_matricula_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.matricula_id_matricula_seq', 16, true);


--
-- TOC entry 3985 (class 0 OID 0)
-- Dependencies: 276
-- Name: pedido_troca_turno_id_pedido_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.pedido_troca_turno_id_pedido_seq', 1, false);


--
-- TOC entry 3986 (class 0 OID 0)
-- Dependencies: 236
-- Name: semestre_id_semestre_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.semestre_id_semestre_seq', 1, false);


--
-- TOC entry 3987 (class 0 OID 0)
-- Dependencies: 238
-- Name: turno_id_turno_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.turno_id_turno_seq', 24, true);


--
-- TOC entry 3988 (class 0 OID 0)
-- Dependencies: 241
-- Name: unidade_curricular_id_unidadecurricular_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.unidade_curricular_id_unidadecurricular_seq', 116, true);


--
-- TOC entry 3989 (class 0 OID 0)
-- Dependencies: 272
-- Name: utilizador_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.utilizador_id_seq', 2, true);


--
-- TOC entry 3443 (class 2606 OID 16497)
-- Name: users_sync users_sync_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: neondb_owner
--

ALTER TABLE ONLY neon_auth.users_sync
    ADD CONSTRAINT users_sync_pkey PRIMARY KEY (id);


--
-- TOC entry 3581 (class 2606 OID 204807)
-- Name: auditoria_inscricao auditoria_inscricao_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auditoria_inscricao
    ADD CONSTRAINT auditoria_inscricao_pkey PRIMARY KEY (id_auditoria);


--
-- TOC entry 3514 (class 2606 OID 24916)
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- TOC entry 3519 (class 2606 OID 24847)
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- TOC entry 3522 (class 2606 OID 24816)
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3516 (class 2606 OID 24808)
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- TOC entry 3509 (class 2606 OID 24838)
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- TOC entry 3511 (class 2606 OID 24802)
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- TOC entry 3530 (class 2606 OID 24830)
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- TOC entry 3533 (class 2606 OID 24862)
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- TOC entry 3524 (class 2606 OID 24822)
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- TOC entry 3536 (class 2606 OID 24836)
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3539 (class 2606 OID 24876)
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- TOC entry 3527 (class 2606 OID 24911)
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- TOC entry 3584 (class 2606 OID 212999)
-- Name: core_avaliacaopdf core_avaliacaopdf_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_avaliacaopdf
    ADD CONSTRAINT core_avaliacaopdf_pkey PRIMARY KEY (id);


--
-- TOC entry 3550 (class 2606 OID 131077)
-- Name: core_horariopdf core_horariopdf_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_horariopdf
    ADD CONSTRAINT core_horariopdf_pkey PRIMARY KEY (id);


--
-- TOC entry 3562 (class 2606 OID 172062)
-- Name: core_pedidotrocaturno core_pedidotrocaturno_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_pedidotrocaturno
    ADD CONSTRAINT core_pedidotrocaturno_pkey PRIMARY KEY (id);


--
-- TOC entry 3542 (class 2606 OID 24897)
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- TOC entry 3504 (class 2606 OID 24796)
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- TOC entry 3506 (class 2606 OID 24794)
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- TOC entry 3502 (class 2606 OID 24788)
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- TOC entry 3546 (class 2606 OID 24924)
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- TOC entry 3566 (class 2606 OID 180229)
-- Name: forum_inscricaoturno forum_inscricaoturno_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_inscricaoturno
    ADD CONSTRAINT forum_inscricaoturno_pkey PRIMARY KEY (id_inscricao);


--
-- TOC entry 3572 (class 2606 OID 180241)
-- Name: forum_pedidotrocaturno forum_pedidotrocaturno_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_pedidotrocaturno
    ADD CONSTRAINT forum_pedidotrocaturno_pkey PRIMARY KEY (id);


--
-- TOC entry 3568 (class 2606 OID 180235)
-- Name: forum_turno forum_turno_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_turno
    ADD CONSTRAINT forum_turno_pkey PRIMARY KEY (id);


--
-- TOC entry 3556 (class 2606 OID 163849)
-- Name: log_eventos log_eventos_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.log_eventos
    ADD CONSTRAINT log_eventos_pkey PRIMARY KEY (id_log);


--
-- TOC entry 3558 (class 2606 OID 172041)
-- Name: pedido_troca_turno pedido_troca_turno_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.pedido_troca_turno
    ADD CONSTRAINT pedido_troca_turno_pkey PRIMARY KEY (id_pedido);


--
-- TOC entry 3448 (class 2606 OID 24582)
-- Name: aluno pk_aluno; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.aluno
    ADD CONSTRAINT pk_aluno PRIMARY KEY (n_mecanografico);


--
-- TOC entry 3451 (class 2606 OID 24592)
-- Name: ano_curricular pk_ano_curricular; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ano_curricular
    ADD CONSTRAINT pk_ano_curricular PRIMARY KEY (id_anocurricular);


--
-- TOC entry 3454 (class 2606 OID 24600)
-- Name: ano_letivo pk_ano_letivo; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ano_letivo
    ADD CONSTRAINT pk_ano_letivo PRIMARY KEY (id_anoletivo);


--
-- TOC entry 3457 (class 2606 OID 24610)
-- Name: curso pk_curso; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.curso
    ADD CONSTRAINT pk_curso PRIMARY KEY (id_curso);


--
-- TOC entry 3460 (class 2606 OID 24620)
-- Name: docente pk_docente; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.docente
    ADD CONSTRAINT pk_docente PRIMARY KEY (id_docente);


--
-- TOC entry 3464 (class 2606 OID 24628)
-- Name: horario pk_horario; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT pk_horario PRIMARY KEY (id_horario);


--
-- TOC entry 3469 (class 2606 OID 24638)
-- Name: inscricao_turno pk_inscricao_turno; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscricao_turno
    ADD CONSTRAINT pk_inscricao_turno PRIMARY KEY (id_inscricao);


--
-- TOC entry 3474 (class 2606 OID 24645)
-- Name: inscrito_uc pk_inscrito_uc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscrito_uc
    ADD CONSTRAINT pk_inscrito_uc PRIMARY KEY (n_mecanografico, id_unidadecurricular);


--
-- TOC entry 3476 (class 2606 OID 24653)
-- Name: leciona_uc pk_leciona_uc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.leciona_uc
    ADD CONSTRAINT pk_leciona_uc PRIMARY KEY (id_unidadecurricular, id_docente);


--
-- TOC entry 3483 (class 2606 OID 24663)
-- Name: matricula pk_matricula; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matricula
    ADD CONSTRAINT pk_matricula PRIMARY KEY (id_matricula);


--
-- TOC entry 3486 (class 2606 OID 24673)
-- Name: semestre pk_semestre; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.semestre
    ADD CONSTRAINT pk_semestre PRIMARY KEY (id_semestre);


--
-- TOC entry 3489 (class 2606 OID 24681)
-- Name: turno pk_turno; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.turno
    ADD CONSTRAINT pk_turno PRIMARY KEY (id_turno);


--
-- TOC entry 3492 (class 2606 OID 24687)
-- Name: turno_uc pk_turno_uc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.turno_uc
    ADD CONSTRAINT pk_turno_uc PRIMARY KEY (id_turno, id_unidadecurricular);


--
-- TOC entry 3498 (class 2606 OID 24697)
-- Name: unidade_curricular pk_unidade_curricular; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.unidade_curricular
    ADD CONSTRAINT pk_unidade_curricular PRIMARY KEY (id_unidadecurricular);


--
-- TOC entry 3552 (class 2606 OID 139269)
-- Name: utilizador utilizador_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.utilizador
    ADD CONSTRAINT utilizador_pkey PRIMARY KEY (id);


--
-- TOC entry 3554 (class 2606 OID 139271)
-- Name: utilizador utilizador_user_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.utilizador
    ADD CONSTRAINT utilizador_user_id_key UNIQUE (user_id);


--
-- TOC entry 3441 (class 1259 OID 16498)
-- Name: users_sync_deleted_at_idx; Type: INDEX; Schema: neon_auth; Owner: neondb_owner
--

CREATE INDEX users_sync_deleted_at_idx ON neon_auth.users_sync USING btree (deleted_at);


--
-- TOC entry 3444 (class 1259 OID 24583)
-- Name: aluno_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX aluno_pk ON public.aluno USING btree (n_mecanografico);


--
-- TOC entry 3449 (class 1259 OID 24593)
-- Name: ano_curricular_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ano_curricular_pk ON public.ano_curricular USING btree (id_anocurricular);


--
-- TOC entry 3452 (class 1259 OID 24601)
-- Name: ano_letivo_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ano_letivo_pk ON public.ano_letivo USING btree (id_anoletivo);


--
-- TOC entry 3574 (class 1259 OID 204828)
-- Name: auditoria_i_data_te_f7031c_idx; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_i_data_te_f7031c_idx ON public.auditoria_inscricao USING btree (data_tentativa);


--
-- TOC entry 3575 (class 1259 OID 204826)
-- Name: auditoria_i_n_mecan_a7f742_idx; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_i_n_mecan_a7f742_idx ON public.auditoria_inscricao USING btree (n_mecanografico, data_tentativa DESC);


--
-- TOC entry 3576 (class 1259 OID 204827)
-- Name: auditoria_i_resulta_8ca880_idx; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_i_resulta_8ca880_idx ON public.auditoria_inscricao USING btree (resultado);


--
-- TOC entry 3577 (class 1259 OID 204823)
-- Name: auditoria_inscricao_id_turno_229d73e0; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_inscricao_id_turno_229d73e0 ON public.auditoria_inscricao USING btree (id_turno);


--
-- TOC entry 3578 (class 1259 OID 204824)
-- Name: auditoria_inscricao_id_unidadecurricular_09ea8e74; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_inscricao_id_unidadecurricular_09ea8e74 ON public.auditoria_inscricao USING btree (id_unidadecurricular);


--
-- TOC entry 3579 (class 1259 OID 204825)
-- Name: auditoria_inscricao_n_mecanografico_f971f2ea; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auditoria_inscricao_n_mecanografico_f971f2ea ON public.auditoria_inscricao USING btree (n_mecanografico);


--
-- TOC entry 3512 (class 1259 OID 24917)
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- TOC entry 3517 (class 1259 OID 24858)
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- TOC entry 3520 (class 1259 OID 24859)
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- TOC entry 3507 (class 1259 OID 24844)
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- TOC entry 3528 (class 1259 OID 24874)
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- TOC entry 3531 (class 1259 OID 24873)
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- TOC entry 3534 (class 1259 OID 24888)
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- TOC entry 3537 (class 1259 OID 24887)
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- TOC entry 3525 (class 1259 OID 24912)
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- TOC entry 3582 (class 1259 OID 221195)
-- Name: core_avaliacaopdf_id_curso_dc587556; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX core_avaliacaopdf_id_curso_dc587556 ON public.core_avaliacaopdf USING btree (id_curso);


--
-- TOC entry 3548 (class 1259 OID 221194)
-- Name: core_horariopdf_id_curso_ac822a57; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX core_horariopdf_id_curso_ac822a57 ON public.core_horariopdf USING btree (id_curso);


--
-- TOC entry 3559 (class 1259 OID 172078)
-- Name: core_pedidotrocaturno_inscricao_contraparte_id_0b739849; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX core_pedidotrocaturno_inscricao_contraparte_id_0b739849 ON public.core_pedidotrocaturno USING btree (inscricao_contraparte_id);


--
-- TOC entry 3560 (class 1259 OID 172079)
-- Name: core_pedidotrocaturno_inscricao_solicitante_id_0e2fc1c6; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX core_pedidotrocaturno_inscricao_solicitante_id_0e2fc1c6 ON public.core_pedidotrocaturno USING btree (inscricao_solicitante_id);


--
-- TOC entry 3563 (class 1259 OID 172080)
-- Name: core_pedidotrocaturno_turno_desejado_id_ac3000d3; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX core_pedidotrocaturno_turno_desejado_id_ac3000d3 ON public.core_pedidotrocaturno USING btree (turno_desejado_id);


--
-- TOC entry 3455 (class 1259 OID 24611)
-- Name: curso_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX curso_pk ON public.curso USING btree (id_curso);


--
-- TOC entry 3540 (class 1259 OID 24908)
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- TOC entry 3543 (class 1259 OID 24909)
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- TOC entry 3544 (class 1259 OID 24926)
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- TOC entry 3547 (class 1259 OID 24925)
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- TOC entry 3496 (class 1259 OID 24700)
-- Name: do_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX do_fk ON public.unidade_curricular USING btree (id_semestre);


--
-- TOC entry 3458 (class 1259 OID 24621)
-- Name: docente_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX docente_pk ON public.docente USING btree (id_docente);


--
-- TOC entry 3461 (class 1259 OID 24630)
-- Name: esta_contido_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX esta_contido_fk ON public.horario USING btree (id_semestre);


--
-- TOC entry 3445 (class 1259 OID 24585)
-- Name: esta_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX esta_fk ON public.aluno USING btree (id_anocurricular);


--
-- TOC entry 3466 (class 1259 OID 24640)
-- Name: faz_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX faz_fk ON public.inscricao_turno USING btree (n_mecanografico);


--
-- TOC entry 3480 (class 1259 OID 24666)
-- Name: feita_no_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX feita_no_fk ON public.matricula USING btree (id_anoletivo);


--
-- TOC entry 3564 (class 1259 OID 180265)
-- Name: forum_inscricaoturno_id_turno_id_149df08e; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX forum_inscricaoturno_id_turno_id_149df08e ON public.forum_inscricaoturno USING btree (id_turno_id);


--
-- TOC entry 3569 (class 1259 OID 180262)
-- Name: forum_pedidotrocaturno_inscricao_contraparte_id_5d0d396b; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX forum_pedidotrocaturno_inscricao_contraparte_id_5d0d396b ON public.forum_pedidotrocaturno USING btree (inscricao_contraparte_id);


--
-- TOC entry 3570 (class 1259 OID 180263)
-- Name: forum_pedidotrocaturno_inscricao_solicitante_id_5385249b; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX forum_pedidotrocaturno_inscricao_solicitante_id_5385249b ON public.forum_pedidotrocaturno USING btree (inscricao_solicitante_id);


--
-- TOC entry 3573 (class 1259 OID 180264)
-- Name: forum_pedidotrocaturno_turno_desejado_id_f6ccf408; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX forum_pedidotrocaturno_turno_desejado_id_f6ccf408 ON public.forum_pedidotrocaturno USING btree (turno_desejado_id);


--
-- TOC entry 3462 (class 1259 OID 24629)
-- Name: horario_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX horario_pk ON public.horario USING btree (id_horario);


--
-- TOC entry 3592 (class 1259 OID 229442)
-- Name: idx_mv_conflitos_aluno; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_conflitos_aluno ON public.mv_conflitos_horario USING btree (n_mecanografico);


--
-- TOC entry 3585 (class 1259 OID 229389)
-- Name: idx_mv_estatisticas_turno_cheio; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_estatisticas_turno_cheio ON public.mv_estatisticas_turno USING btree (turno_cheio);


--
-- TOC entry 3586 (class 1259 OID 229390)
-- Name: idx_mv_estatisticas_turno_ocupacao; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_estatisticas_turno_ocupacao ON public.mv_estatisticas_turno USING btree (taxa_ocupacao_percent);


--
-- TOC entry 3587 (class 1259 OID 229388)
-- Name: idx_mv_estatisticas_turno_uc; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_estatisticas_turno_uc ON public.mv_estatisticas_turno USING btree (id_unidadecurricular);


--
-- TOC entry 3588 (class 1259 OID 229404)
-- Name: idx_mv_resumo_aluno_curso; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_resumo_aluno_curso ON public.mv_resumo_inscricoes_aluno USING btree (curso_nome);


--
-- TOC entry 3589 (class 1259 OID 229403)
-- Name: idx_mv_resumo_aluno_nmec; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_resumo_aluno_nmec ON public.mv_resumo_inscricoes_aluno USING btree (n_mecanografico);


--
-- TOC entry 3590 (class 1259 OID 229418)
-- Name: idx_mv_ucs_procuradas_total; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_ucs_procuradas_total ON public.mv_ucs_mais_procuradas USING btree (total_alunos_inscritos);


--
-- TOC entry 3591 (class 1259 OID 229417)
-- Name: idx_mv_ucs_procuradas_uc; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_ucs_procuradas_uc ON public.mv_ucs_mais_procuradas USING btree (id_unidadecurricular);


--
-- TOC entry 3467 (class 1259 OID 24639)
-- Name: inscricao_turno_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX inscricao_turno_pk ON public.inscricao_turno USING btree (id_inscricao);


--
-- TOC entry 3470 (class 1259 OID 24648)
-- Name: inscrito2_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX inscrito2_fk ON public.inscrito_uc USING btree (id_unidadecurricular);


--
-- TOC entry 3471 (class 1259 OID 24647)
-- Name: inscrito_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX inscrito_fk ON public.inscrito_uc USING btree (n_mecanografico);


--
-- TOC entry 3472 (class 1259 OID 24646)
-- Name: inscrito_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX inscrito_pk ON public.inscrito_uc USING btree (n_mecanografico, id_unidadecurricular);


--
-- TOC entry 3481 (class 1259 OID 24664)
-- Name: matricula_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX matricula_pk ON public.matricula USING btree (id_matricula);


--
-- TOC entry 3446 (class 1259 OID 24584)
-- Name: pertence_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX pertence_fk ON public.aluno USING btree (id_curso);


--
-- TOC entry 3465 (class 1259 OID 24631)
-- Name: possui_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX possui_fk ON public.horario USING btree (id_anoletivo);


--
-- TOC entry 3477 (class 1259 OID 24656)
-- Name: relationship_10_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX relationship_10_fk ON public.leciona_uc USING btree (id_docente);


--
-- TOC entry 3499 (class 1259 OID 24699)
-- Name: relationship_6_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX relationship_6_fk ON public.unidade_curricular USING btree (id_anocurricular);


--
-- TOC entry 3493 (class 1259 OID 24689)
-- Name: relationship_7_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX relationship_7_fk ON public.turno_uc USING btree (id_turno);


--
-- TOC entry 3494 (class 1259 OID 24688)
-- Name: relationship_7_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX relationship_7_pk ON public.turno_uc USING btree (id_turno, id_unidadecurricular);


--
-- TOC entry 3495 (class 1259 OID 24690)
-- Name: relationship_8_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX relationship_8_fk ON public.turno_uc USING btree (id_unidadecurricular);


--
-- TOC entry 3478 (class 1259 OID 24655)
-- Name: relationship_9_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX relationship_9_fk ON public.leciona_uc USING btree (id_unidadecurricular);


--
-- TOC entry 3479 (class 1259 OID 24654)
-- Name: relationship_9_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX relationship_9_pk ON public.leciona_uc USING btree (id_unidadecurricular, id_docente);


--
-- TOC entry 3487 (class 1259 OID 24674)
-- Name: semestre_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX semestre_pk ON public.semestre USING btree (id_semestre);


--
-- TOC entry 3484 (class 1259 OID 24665)
-- Name: tem_fk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX tem_fk ON public.matricula USING btree (n_mecanografico);


--
-- TOC entry 3490 (class 1259 OID 24682)
-- Name: turno_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX turno_pk ON public.turno USING btree (id_turno);


--
-- TOC entry 3500 (class 1259 OID 24698)
-- Name: unidade_curricular_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX unidade_curricular_pk ON public.unidade_curricular USING btree (id_unidadecurricular);


--
-- TOC entry 3637 (class 2620 OID 163853)
-- Name: aluno log_aluno_insert; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER log_aluno_insert AFTER INSERT ON public.aluno FOR EACH ROW EXECUTE FUNCTION public.trg_log_aluno_insert();


--
-- TOC entry 3638 (class 2620 OID 163851)
-- Name: docente log_docente_insert; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER log_docente_insert AFTER INSERT ON public.docente FOR EACH ROW EXECUTE FUNCTION public.trg_log_docente_insert();


--
-- TOC entry 3641 (class 2620 OID 163855)
-- Name: matricula log_matricula_insert; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER log_matricula_insert AFTER INSERT ON public.matricula FOR EACH ROW EXECUTE FUNCTION public.trg_log_matricula_insert();


--
-- TOC entry 3639 (class 2620 OID 147457)
-- Name: inscricao_turno trg_inscricao_duplicada; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_inscricao_duplicada BEFORE INSERT ON public.inscricao_turno FOR EACH ROW EXECUTE FUNCTION public.validar_inscricao_duplicada();


--
-- TOC entry 3640 (class 2620 OID 147459)
-- Name: inscricao_turno trg_validar_inscricao_uc; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_validar_inscricao_uc BEFORE INSERT ON public.inscricao_turno FOR EACH ROW EXECUTE FUNCTION public.validar_inscricao_uc();


--
-- TOC entry 3632 (class 2606 OID 204808)
-- Name: auditoria_inscricao auditoria_inscricao_id_turno_229d73e0_fk_turno_id_turno; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auditoria_inscricao
    ADD CONSTRAINT auditoria_inscricao_id_turno_229d73e0_fk_turno_id_turno FOREIGN KEY (id_turno) REFERENCES public.turno(id_turno) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3633 (class 2606 OID 204813)
-- Name: auditoria_inscricao auditoria_inscricao_id_unidadecurricular_09ea8e74_fk_unidade_c; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auditoria_inscricao
    ADD CONSTRAINT auditoria_inscricao_id_unidadecurricular_09ea8e74_fk_unidade_c FOREIGN KEY (id_unidadecurricular) REFERENCES public.unidade_curricular(id_unidadecurricular) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3634 (class 2606 OID 204818)
-- Name: auditoria_inscricao auditoria_inscricao_n_mecanografico_f971f2ea_fk_aluno_n_m; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auditoria_inscricao
    ADD CONSTRAINT auditoria_inscricao_n_mecanografico_f971f2ea_fk_aluno_n_m FOREIGN KEY (n_mecanografico) REFERENCES public.aluno(n_mecanografico) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3611 (class 2606 OID 24853)
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3612 (class 2606 OID 24848)
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3610 (class 2606 OID 24839)
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3613 (class 2606 OID 24868)
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3614 (class 2606 OID 24863)
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3615 (class 2606 OID 24882)
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3616 (class 2606 OID 24877)
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3635 (class 2606 OID 213000)
-- Name: core_avaliacaopdf core_avaliacaopdf_id_anocurricular_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_avaliacaopdf
    ADD CONSTRAINT core_avaliacaopdf_id_anocurricular_id_fkey FOREIGN KEY (id_anocurricular) REFERENCES public.ano_curricular(id_anocurricular);


--
-- TOC entry 3636 (class 2606 OID 221189)
-- Name: core_avaliacaopdf core_avaliacaopdf_id_curso_dc587556_fk_curso_id_curso; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_avaliacaopdf
    ADD CONSTRAINT core_avaliacaopdf_id_curso_dc587556_fk_curso_id_curso FOREIGN KEY (id_curso) REFERENCES public.curso(id_curso) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3619 (class 2606 OID 221184)
-- Name: core_horariopdf core_horariopdf_id_curso_ac822a57_fk_curso_id_curso; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_horariopdf
    ADD CONSTRAINT core_horariopdf_id_curso_ac822a57_fk_curso_id_curso FOREIGN KEY (id_curso) REFERENCES public.curso(id_curso) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3625 (class 2606 OID 172063)
-- Name: core_pedidotrocaturno core_pedidotrocaturn_inscricao_contrapart_0b739849_fk_inscricao; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_pedidotrocaturno
    ADD CONSTRAINT core_pedidotrocaturn_inscricao_contrapart_0b739849_fk_inscricao FOREIGN KEY (inscricao_contraparte_id) REFERENCES public.inscricao_turno(id_inscricao) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3626 (class 2606 OID 172068)
-- Name: core_pedidotrocaturno core_pedidotrocaturn_inscricao_solicitant_0e2fc1c6_fk_inscricao; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_pedidotrocaturno
    ADD CONSTRAINT core_pedidotrocaturn_inscricao_solicitant_0e2fc1c6_fk_inscricao FOREIGN KEY (inscricao_solicitante_id) REFERENCES public.inscricao_turno(id_inscricao) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3627 (class 2606 OID 172073)
-- Name: core_pedidotrocaturno core_pedidotrocaturn_turno_desejado_id_ac3000d3_fk_turno_id_; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_pedidotrocaturno
    ADD CONSTRAINT core_pedidotrocaturn_turno_desejado_id_ac3000d3_fk_turno_id_ FOREIGN KEY (turno_desejado_id) REFERENCES public.turno(id_turno) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3617 (class 2606 OID 24898)
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3618 (class 2606 OID 24903)
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3593 (class 2606 OID 24701)
-- Name: aluno fk_aluno_esta_ano_curr; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.aluno
    ADD CONSTRAINT fk_aluno_esta_ano_curr FOREIGN KEY (id_anocurricular) REFERENCES public.ano_curricular(id_anocurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3594 (class 2606 OID 24706)
-- Name: aluno fk_aluno_pertence_curso; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.aluno
    ADD CONSTRAINT fk_aluno_pertence_curso FOREIGN KEY (id_curso) REFERENCES public.curso(id_curso) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3620 (class 2606 OID 196608)
-- Name: core_horariopdf fk_horario_ano; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.core_horariopdf
    ADD CONSTRAINT fk_horario_ano FOREIGN KEY (id_anocurricular) REFERENCES public.ano_curricular(id_anocurricular);


--
-- TOC entry 3595 (class 2606 OID 24711)
-- Name: horario fk_horario_esta_cont_semestre; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT fk_horario_esta_cont_semestre FOREIGN KEY (id_semestre) REFERENCES public.semestre(id_semestre) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3596 (class 2606 OID 24716)
-- Name: horario fk_horario_possui_ano_leti; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT fk_horario_possui_ano_leti FOREIGN KEY (id_anoletivo) REFERENCES public.ano_letivo(id_anoletivo) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3597 (class 2606 OID 24721)
-- Name: inscricao_turno fk_inscrica_faz_aluno; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscricao_turno
    ADD CONSTRAINT fk_inscrica_faz_aluno FOREIGN KEY (n_mecanografico) REFERENCES public.aluno(n_mecanografico) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3598 (class 2606 OID 24726)
-- Name: inscricao_turno fk_inscrica_reference_turno_uc; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscricao_turno
    ADD CONSTRAINT fk_inscrica_reference_turno_uc FOREIGN KEY (id_turno, id_unidadecurricular) REFERENCES public.turno_uc(id_turno, id_unidadecurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3599 (class 2606 OID 24731)
-- Name: inscrito_uc fk_inscrito_inscrito__aluno; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscrito_uc
    ADD CONSTRAINT fk_inscrito_inscrito__aluno FOREIGN KEY (n_mecanografico) REFERENCES public.aluno(n_mecanografico) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3600 (class 2606 OID 24736)
-- Name: inscrito_uc fk_inscrito_inscrito__unidade_; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.inscrito_uc
    ADD CONSTRAINT fk_inscrito_inscrito__unidade_ FOREIGN KEY (id_unidadecurricular) REFERENCES public.unidade_curricular(id_unidadecurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3601 (class 2606 OID 24746)
-- Name: leciona_uc fk_leciona__leciona_u_docente; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.leciona_uc
    ADD CONSTRAINT fk_leciona__leciona_u_docente FOREIGN KEY (id_docente) REFERENCES public.docente(id_docente) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3602 (class 2606 OID 24741)
-- Name: leciona_uc fk_leciona__leciona_u_unidade_; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.leciona_uc
    ADD CONSTRAINT fk_leciona__leciona_u_unidade_ FOREIGN KEY (id_unidadecurricular) REFERENCES public.unidade_curricular(id_unidadecurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3603 (class 2606 OID 24751)
-- Name: matricula fk_matricul_feita_no_ano_leti; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matricula
    ADD CONSTRAINT fk_matricul_feita_no_ano_leti FOREIGN KEY (id_anoletivo) REFERENCES public.ano_letivo(id_anoletivo) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3604 (class 2606 OID 24756)
-- Name: matricula fk_matricul_tem_aluno; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matricula
    ADD CONSTRAINT fk_matricul_tem_aluno FOREIGN KEY (n_mecanografico) REFERENCES public.aluno(n_mecanografico) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3622 (class 2606 OID 172052)
-- Name: pedido_troca_turno fk_pedido_insc_contraparte; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.pedido_troca_turno
    ADD CONSTRAINT fk_pedido_insc_contraparte FOREIGN KEY (id_inscricao_contraparte) REFERENCES public.inscricao_turno(id_inscricao);


--
-- TOC entry 3623 (class 2606 OID 172042)
-- Name: pedido_troca_turno fk_pedido_insc_solicitante; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.pedido_troca_turno
    ADD CONSTRAINT fk_pedido_insc_solicitante FOREIGN KEY (id_inscricao_solicitante) REFERENCES public.inscricao_turno(id_inscricao);


--
-- TOC entry 3624 (class 2606 OID 172047)
-- Name: pedido_troca_turno fk_pedido_turno_desejado; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.pedido_troca_turno
    ADD CONSTRAINT fk_pedido_turno_desejado FOREIGN KEY (id_turno_desejado) REFERENCES public.turno(id_turno);


--
-- TOC entry 3605 (class 2606 OID 24766)
-- Name: turno_uc fk_turno_uc_turno_uc2_unidade_; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.turno_uc
    ADD CONSTRAINT fk_turno_uc_turno_uc2_unidade_ FOREIGN KEY (id_unidadecurricular) REFERENCES public.unidade_curricular(id_unidadecurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3606 (class 2606 OID 24761)
-- Name: turno_uc fk_turno_uc_turno_uc_turno; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.turno_uc
    ADD CONSTRAINT fk_turno_uc_turno_uc_turno FOREIGN KEY (id_turno) REFERENCES public.turno(id_turno) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3607 (class 2606 OID 188416)
-- Name: unidade_curricular fk_uc_curso; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.unidade_curricular
    ADD CONSTRAINT fk_uc_curso FOREIGN KEY (id_curso) REFERENCES public.curso(id_curso) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3608 (class 2606 OID 24771)
-- Name: unidade_curricular fk_unidade__do_semestre; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.unidade_curricular
    ADD CONSTRAINT fk_unidade__do_semestre FOREIGN KEY (id_semestre) REFERENCES public.semestre(id_semestre) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3609 (class 2606 OID 24776)
-- Name: unidade_curricular fk_unidade__relations_ano_curr; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.unidade_curricular
    ADD CONSTRAINT fk_unidade__relations_ano_curr FOREIGN KEY (id_anocurricular) REFERENCES public.ano_curricular(id_anocurricular) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3628 (class 2606 OID 180242)
-- Name: forum_inscricaoturno forum_inscricaoturno_id_turno_id_149df08e_fk_forum_turno_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_inscricaoturno
    ADD CONSTRAINT forum_inscricaoturno_id_turno_id_149df08e_fk_forum_turno_id FOREIGN KEY (id_turno_id) REFERENCES public.forum_turno(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3629 (class 2606 OID 180247)
-- Name: forum_pedidotrocaturno forum_pedidotrocatur_inscricao_contrapart_5d0d396b_fk_forum_ins; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_pedidotrocaturno
    ADD CONSTRAINT forum_pedidotrocatur_inscricao_contrapart_5d0d396b_fk_forum_ins FOREIGN KEY (inscricao_contraparte_id) REFERENCES public.forum_inscricaoturno(id_inscricao) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3630 (class 2606 OID 180252)
-- Name: forum_pedidotrocaturno forum_pedidotrocatur_inscricao_solicitant_5385249b_fk_forum_ins; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_pedidotrocaturno
    ADD CONSTRAINT forum_pedidotrocatur_inscricao_solicitant_5385249b_fk_forum_ins FOREIGN KEY (inscricao_solicitante_id) REFERENCES public.forum_inscricaoturno(id_inscricao) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3631 (class 2606 OID 180257)
-- Name: forum_pedidotrocaturno forum_pedidotrocatur_turno_desejado_id_f6ccf408_fk_forum_tur; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.forum_pedidotrocaturno
    ADD CONSTRAINT forum_pedidotrocatur_turno_desejado_id_f6ccf408_fk_forum_tur FOREIGN KEY (turno_desejado_id) REFERENCES public.forum_turno(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3621 (class 2606 OID 139272)
-- Name: utilizador utilizador_user_id_5a9520cd_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.utilizador
    ADD CONSTRAINT utilizador_user_id_5a9520cd_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3872 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO ana_almeida_user;
GRANT ALL ON SCHEMA public TO susana_tavares_user;
GRANT ALL ON SCHEMA public TO patricia_oliveira_user;
GRANT ALL ON SCHEMA public TO david_borges_user;


--
-- TOC entry 3873 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE aluno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.aluno TO ana_almeida_user;
GRANT ALL ON TABLE public.aluno TO susana_tavares_user;
GRANT ALL ON TABLE public.aluno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.aluno TO david_borges_user;


--
-- TOC entry 3874 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE ano_curricular; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.ano_curricular TO ana_almeida_user;
GRANT ALL ON TABLE public.ano_curricular TO susana_tavares_user;
GRANT ALL ON TABLE public.ano_curricular TO patricia_oliveira_user;
GRANT ALL ON TABLE public.ano_curricular TO david_borges_user;


--
-- TOC entry 3876 (class 0 OID 0)
-- Dependencies: 220
-- Name: SEQUENCE ano_curricular_id_anocurricular_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.ano_curricular_id_anocurricular_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.ano_curricular_id_anocurricular_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.ano_curricular_id_anocurricular_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.ano_curricular_id_anocurricular_seq TO david_borges_user;


--
-- TOC entry 3877 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE ano_letivo; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.ano_letivo TO ana_almeida_user;
GRANT ALL ON TABLE public.ano_letivo TO susana_tavares_user;
GRANT ALL ON TABLE public.ano_letivo TO patricia_oliveira_user;
GRANT ALL ON TABLE public.ano_letivo TO david_borges_user;


--
-- TOC entry 3879 (class 0 OID 0)
-- Dependencies: 222
-- Name: SEQUENCE ano_letivo_id_anoletivo_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.ano_letivo_id_anoletivo_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.ano_letivo_id_anoletivo_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.ano_letivo_id_anoletivo_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.ano_letivo_id_anoletivo_seq TO david_borges_user;


--
-- TOC entry 3880 (class 0 OID 0)
-- Dependencies: 287
-- Name: TABLE auditoria_inscricao; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auditoria_inscricao TO ana_almeida_user;
GRANT ALL ON TABLE public.auditoria_inscricao TO susana_tavares_user;
GRANT ALL ON TABLE public.auditoria_inscricao TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auditoria_inscricao TO david_borges_user;


--
-- TOC entry 3881 (class 0 OID 0)
-- Dependencies: 286
-- Name: SEQUENCE auditoria_inscricao_id_auditoria_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auditoria_inscricao_id_auditoria_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auditoria_inscricao_id_auditoria_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auditoria_inscricao_id_auditoria_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auditoria_inscricao_id_auditoria_seq TO david_borges_user;


--
-- TOC entry 3882 (class 0 OID 0)
-- Dependencies: 250
-- Name: TABLE auth_group; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_group TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_group TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_group TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_group TO david_borges_user;


--
-- TOC entry 3883 (class 0 OID 0)
-- Dependencies: 249
-- Name: SEQUENCE auth_group_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_group_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_group_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_group_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_group_id_seq TO david_borges_user;


--
-- TOC entry 3884 (class 0 OID 0)
-- Dependencies: 252
-- Name: TABLE auth_group_permissions; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_group_permissions TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_group_permissions TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_group_permissions TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_group_permissions TO david_borges_user;


--
-- TOC entry 3885 (class 0 OID 0)
-- Dependencies: 251
-- Name: SEQUENCE auth_group_permissions_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_group_permissions_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_group_permissions_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_group_permissions_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_group_permissions_id_seq TO david_borges_user;


--
-- TOC entry 3886 (class 0 OID 0)
-- Dependencies: 248
-- Name: TABLE auth_permission; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_permission TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_permission TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_permission TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_permission TO david_borges_user;


--
-- TOC entry 3887 (class 0 OID 0)
-- Dependencies: 247
-- Name: SEQUENCE auth_permission_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_permission_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_permission_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_permission_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_permission_id_seq TO david_borges_user;


--
-- TOC entry 3888 (class 0 OID 0)
-- Dependencies: 254
-- Name: TABLE auth_user; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_user TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_user TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_user TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_user TO david_borges_user;


--
-- TOC entry 3889 (class 0 OID 0)
-- Dependencies: 256
-- Name: TABLE auth_user_groups; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_user_groups TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_user_groups TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_user_groups TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_user_groups TO david_borges_user;


--
-- TOC entry 3890 (class 0 OID 0)
-- Dependencies: 255
-- Name: SEQUENCE auth_user_groups_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_user_groups_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_user_groups_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_user_groups_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_user_groups_id_seq TO david_borges_user;


--
-- TOC entry 3891 (class 0 OID 0)
-- Dependencies: 253
-- Name: SEQUENCE auth_user_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_user_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_user_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_user_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_user_id_seq TO david_borges_user;


--
-- TOC entry 3892 (class 0 OID 0)
-- Dependencies: 258
-- Name: TABLE auth_user_user_permissions; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.auth_user_user_permissions TO ana_almeida_user;
GRANT ALL ON TABLE public.auth_user_user_permissions TO susana_tavares_user;
GRANT ALL ON TABLE public.auth_user_user_permissions TO patricia_oliveira_user;
GRANT ALL ON TABLE public.auth_user_user_permissions TO david_borges_user;


--
-- TOC entry 3893 (class 0 OID 0)
-- Dependencies: 257
-- Name: SEQUENCE auth_user_user_permissions_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.auth_user_user_permissions_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.auth_user_user_permissions_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.auth_user_user_permissions_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.auth_user_user_permissions_id_seq TO david_borges_user;


--
-- TOC entry 3894 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE semestre; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.semestre TO ana_almeida_user;
GRANT ALL ON TABLE public.semestre TO susana_tavares_user;
GRANT ALL ON TABLE public.semestre TO patricia_oliveira_user;
GRANT ALL ON TABLE public.semestre TO david_borges_user;


--
-- TOC entry 3895 (class 0 OID 0)
-- Dependencies: 242
-- Name: TABLE unidade_curricular; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.unidade_curricular TO ana_almeida_user;
GRANT ALL ON TABLE public.unidade_curricular TO susana_tavares_user;
GRANT ALL ON TABLE public.unidade_curricular TO patricia_oliveira_user;
GRANT ALL ON TABLE public.unidade_curricular TO david_borges_user;


--
-- TOC entry 3896 (class 0 OID 0)
-- Dependencies: 264
-- Name: TABLE cadeirassemestre; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.cadeirassemestre TO ana_almeida_user;
GRANT ALL ON TABLE public.cadeirassemestre TO susana_tavares_user;
GRANT ALL ON TABLE public.cadeirassemestre TO patricia_oliveira_user;
GRANT ALL ON TABLE public.cadeirassemestre TO david_borges_user;


--
-- TOC entry 3897 (class 0 OID 0)
-- Dependencies: 289
-- Name: TABLE core_avaliacaopdf; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.core_avaliacaopdf TO ana_almeida_user;
GRANT ALL ON TABLE public.core_avaliacaopdf TO susana_tavares_user;
GRANT ALL ON TABLE public.core_avaliacaopdf TO patricia_oliveira_user;
GRANT ALL ON TABLE public.core_avaliacaopdf TO david_borges_user;


--
-- TOC entry 3899 (class 0 OID 0)
-- Dependencies: 288
-- Name: SEQUENCE core_avaliacaopdf_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.core_avaliacaopdf_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.core_avaliacaopdf_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.core_avaliacaopdf_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.core_avaliacaopdf_id_seq TO david_borges_user;


--
-- TOC entry 3900 (class 0 OID 0)
-- Dependencies: 271
-- Name: TABLE core_horariopdf; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.core_horariopdf TO ana_almeida_user;
GRANT ALL ON TABLE public.core_horariopdf TO susana_tavares_user;
GRANT ALL ON TABLE public.core_horariopdf TO patricia_oliveira_user;
GRANT ALL ON TABLE public.core_horariopdf TO david_borges_user;


--
-- TOC entry 3901 (class 0 OID 0)
-- Dependencies: 270
-- Name: SEQUENCE core_horariopdf_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.core_horariopdf_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.core_horariopdf_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.core_horariopdf_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.core_horariopdf_id_seq TO david_borges_user;


--
-- TOC entry 3902 (class 0 OID 0)
-- Dependencies: 279
-- Name: TABLE core_pedidotrocaturno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.core_pedidotrocaturno TO ana_almeida_user;
GRANT ALL ON TABLE public.core_pedidotrocaturno TO susana_tavares_user;
GRANT ALL ON TABLE public.core_pedidotrocaturno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.core_pedidotrocaturno TO david_borges_user;


--
-- TOC entry 3903 (class 0 OID 0)
-- Dependencies: 278
-- Name: SEQUENCE core_pedidotrocaturno_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.core_pedidotrocaturno_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.core_pedidotrocaturno_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.core_pedidotrocaturno_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.core_pedidotrocaturno_id_seq TO david_borges_user;


--
-- TOC entry 3904 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE curso; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.curso TO ana_almeida_user;
GRANT ALL ON TABLE public.curso TO susana_tavares_user;
GRANT ALL ON TABLE public.curso TO patricia_oliveira_user;
GRANT ALL ON TABLE public.curso TO david_borges_user;


--
-- TOC entry 3906 (class 0 OID 0)
-- Dependencies: 224
-- Name: SEQUENCE curso_id_curso_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.curso_id_curso_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.curso_id_curso_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.curso_id_curso_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.curso_id_curso_seq TO david_borges_user;


--
-- TOC entry 3907 (class 0 OID 0)
-- Dependencies: 260
-- Name: TABLE django_admin_log; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.django_admin_log TO ana_almeida_user;
GRANT ALL ON TABLE public.django_admin_log TO susana_tavares_user;
GRANT ALL ON TABLE public.django_admin_log TO patricia_oliveira_user;
GRANT ALL ON TABLE public.django_admin_log TO david_borges_user;


--
-- TOC entry 3908 (class 0 OID 0)
-- Dependencies: 259
-- Name: SEQUENCE django_admin_log_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.django_admin_log_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.django_admin_log_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.django_admin_log_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.django_admin_log_id_seq TO david_borges_user;


--
-- TOC entry 3909 (class 0 OID 0)
-- Dependencies: 246
-- Name: TABLE django_content_type; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.django_content_type TO ana_almeida_user;
GRANT ALL ON TABLE public.django_content_type TO susana_tavares_user;
GRANT ALL ON TABLE public.django_content_type TO patricia_oliveira_user;
GRANT ALL ON TABLE public.django_content_type TO david_borges_user;


--
-- TOC entry 3910 (class 0 OID 0)
-- Dependencies: 245
-- Name: SEQUENCE django_content_type_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.django_content_type_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.django_content_type_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.django_content_type_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.django_content_type_id_seq TO david_borges_user;


--
-- TOC entry 3911 (class 0 OID 0)
-- Dependencies: 244
-- Name: TABLE django_migrations; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.django_migrations TO ana_almeida_user;
GRANT ALL ON TABLE public.django_migrations TO susana_tavares_user;
GRANT ALL ON TABLE public.django_migrations TO patricia_oliveira_user;
GRANT ALL ON TABLE public.django_migrations TO david_borges_user;


--
-- TOC entry 3912 (class 0 OID 0)
-- Dependencies: 243
-- Name: SEQUENCE django_migrations_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.django_migrations_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.django_migrations_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.django_migrations_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.django_migrations_id_seq TO david_borges_user;


--
-- TOC entry 3913 (class 0 OID 0)
-- Dependencies: 261
-- Name: TABLE django_session; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.django_session TO ana_almeida_user;
GRANT ALL ON TABLE public.django_session TO susana_tavares_user;
GRANT ALL ON TABLE public.django_session TO patricia_oliveira_user;
GRANT ALL ON TABLE public.django_session TO david_borges_user;


--
-- TOC entry 3914 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE docente; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.docente TO ana_almeida_user;
GRANT ALL ON TABLE public.docente TO susana_tavares_user;
GRANT ALL ON TABLE public.docente TO patricia_oliveira_user;
GRANT ALL ON TABLE public.docente TO david_borges_user;


--
-- TOC entry 3916 (class 0 OID 0)
-- Dependencies: 226
-- Name: SEQUENCE docente_id_docente_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.docente_id_docente_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.docente_id_docente_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.docente_id_docente_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.docente_id_docente_seq TO david_borges_user;


--
-- TOC entry 3917 (class 0 OID 0)
-- Dependencies: 281
-- Name: TABLE forum_inscricaoturno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.forum_inscricaoturno TO ana_almeida_user;
GRANT ALL ON TABLE public.forum_inscricaoturno TO susana_tavares_user;
GRANT ALL ON TABLE public.forum_inscricaoturno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.forum_inscricaoturno TO david_borges_user;


--
-- TOC entry 3918 (class 0 OID 0)
-- Dependencies: 280
-- Name: SEQUENCE forum_inscricaoturno_id_inscricao_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.forum_inscricaoturno_id_inscricao_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.forum_inscricaoturno_id_inscricao_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.forum_inscricaoturno_id_inscricao_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.forum_inscricaoturno_id_inscricao_seq TO david_borges_user;


--
-- TOC entry 3919 (class 0 OID 0)
-- Dependencies: 285
-- Name: TABLE forum_pedidotrocaturno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.forum_pedidotrocaturno TO ana_almeida_user;
GRANT ALL ON TABLE public.forum_pedidotrocaturno TO susana_tavares_user;
GRANT ALL ON TABLE public.forum_pedidotrocaturno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.forum_pedidotrocaturno TO david_borges_user;


--
-- TOC entry 3920 (class 0 OID 0)
-- Dependencies: 284
-- Name: SEQUENCE forum_pedidotrocaturno_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.forum_pedidotrocaturno_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.forum_pedidotrocaturno_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.forum_pedidotrocaturno_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.forum_pedidotrocaturno_id_seq TO david_borges_user;


--
-- TOC entry 3921 (class 0 OID 0)
-- Dependencies: 283
-- Name: TABLE forum_turno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.forum_turno TO ana_almeida_user;
GRANT ALL ON TABLE public.forum_turno TO susana_tavares_user;
GRANT ALL ON TABLE public.forum_turno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.forum_turno TO david_borges_user;


--
-- TOC entry 3922 (class 0 OID 0)
-- Dependencies: 282
-- Name: SEQUENCE forum_turno_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.forum_turno_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.forum_turno_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.forum_turno_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.forum_turno_id_seq TO david_borges_user;


--
-- TOC entry 3923 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE horario; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.horario TO ana_almeida_user;
GRANT ALL ON TABLE public.horario TO susana_tavares_user;
GRANT ALL ON TABLE public.horario TO patricia_oliveira_user;
GRANT ALL ON TABLE public.horario TO david_borges_user;


--
-- TOC entry 3925 (class 0 OID 0)
-- Dependencies: 228
-- Name: SEQUENCE horario_id_horario_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.horario_id_horario_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.horario_id_horario_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.horario_id_horario_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.horario_id_horario_seq TO david_borges_user;


--
-- TOC entry 3926 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE inscricao_turno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.inscricao_turno TO ana_almeida_user;
GRANT ALL ON TABLE public.inscricao_turno TO susana_tavares_user;
GRANT ALL ON TABLE public.inscricao_turno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.inscricao_turno TO david_borges_user;


--
-- TOC entry 3928 (class 0 OID 0)
-- Dependencies: 230
-- Name: SEQUENCE inscricao_turno_id_inscricao_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.inscricao_turno_id_inscricao_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.inscricao_turno_id_inscricao_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.inscricao_turno_id_inscricao_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.inscricao_turno_id_inscricao_seq TO david_borges_user;


--
-- TOC entry 3929 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE inscrito_uc; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.inscrito_uc TO ana_almeida_user;
GRANT ALL ON TABLE public.inscrito_uc TO susana_tavares_user;
GRANT ALL ON TABLE public.inscrito_uc TO patricia_oliveira_user;
GRANT ALL ON TABLE public.inscrito_uc TO david_borges_user;


--
-- TOC entry 3930 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE leciona_uc; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.leciona_uc TO ana_almeida_user;
GRANT ALL ON TABLE public.leciona_uc TO susana_tavares_user;
GRANT ALL ON TABLE public.leciona_uc TO patricia_oliveira_user;
GRANT ALL ON TABLE public.leciona_uc TO david_borges_user;


--
-- TOC entry 3931 (class 0 OID 0)
-- Dependencies: 275
-- Name: TABLE log_eventos; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.log_eventos TO ana_almeida_user;
GRANT ALL ON TABLE public.log_eventos TO susana_tavares_user;
GRANT ALL ON TABLE public.log_eventos TO patricia_oliveira_user;
GRANT ALL ON TABLE public.log_eventos TO david_borges_user;


--
-- TOC entry 3933 (class 0 OID 0)
-- Dependencies: 274
-- Name: SEQUENCE log_eventos_id_log_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.log_eventos_id_log_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.log_eventos_id_log_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.log_eventos_id_log_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.log_eventos_id_log_seq TO david_borges_user;


--
-- TOC entry 3934 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE matricula; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.matricula TO ana_almeida_user;
GRANT ALL ON TABLE public.matricula TO susana_tavares_user;
GRANT ALL ON TABLE public.matricula TO patricia_oliveira_user;
GRANT ALL ON TABLE public.matricula TO david_borges_user;


--
-- TOC entry 3936 (class 0 OID 0)
-- Dependencies: 234
-- Name: SEQUENCE matricula_id_matricula_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.matricula_id_matricula_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.matricula_id_matricula_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.matricula_id_matricula_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.matricula_id_matricula_seq TO david_borges_user;


--
-- TOC entry 3937 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE turno_uc; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.turno_uc TO ana_almeida_user;
GRANT ALL ON TABLE public.turno_uc TO susana_tavares_user;
GRANT ALL ON TABLE public.turno_uc TO patricia_oliveira_user;
GRANT ALL ON TABLE public.turno_uc TO david_borges_user;


--
-- TOC entry 3938 (class 0 OID 0)
-- Dependencies: 293
-- Name: TABLE mv_conflitos_horario; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.mv_conflitos_horario TO ana_almeida_user;
GRANT ALL ON TABLE public.mv_conflitos_horario TO susana_tavares_user;
GRANT ALL ON TABLE public.mv_conflitos_horario TO patricia_oliveira_user;
GRANT ALL ON TABLE public.mv_conflitos_horario TO david_borges_user;


--
-- TOC entry 3939 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE turno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.turno TO ana_almeida_user;
GRANT ALL ON TABLE public.turno TO susana_tavares_user;
GRANT ALL ON TABLE public.turno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.turno TO david_borges_user;


--
-- TOC entry 3940 (class 0 OID 0)
-- Dependencies: 290
-- Name: TABLE mv_estatisticas_turno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.mv_estatisticas_turno TO ana_almeida_user;
GRANT ALL ON TABLE public.mv_estatisticas_turno TO susana_tavares_user;
GRANT ALL ON TABLE public.mv_estatisticas_turno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.mv_estatisticas_turno TO david_borges_user;


--
-- TOC entry 3941 (class 0 OID 0)
-- Dependencies: 291
-- Name: TABLE mv_resumo_inscricoes_aluno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.mv_resumo_inscricoes_aluno TO ana_almeida_user;
GRANT ALL ON TABLE public.mv_resumo_inscricoes_aluno TO susana_tavares_user;
GRANT ALL ON TABLE public.mv_resumo_inscricoes_aluno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.mv_resumo_inscricoes_aluno TO david_borges_user;


--
-- TOC entry 3942 (class 0 OID 0)
-- Dependencies: 292
-- Name: TABLE mv_ucs_mais_procuradas; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.mv_ucs_mais_procuradas TO ana_almeida_user;
GRANT ALL ON TABLE public.mv_ucs_mais_procuradas TO susana_tavares_user;
GRANT ALL ON TABLE public.mv_ucs_mais_procuradas TO patricia_oliveira_user;
GRANT ALL ON TABLE public.mv_ucs_mais_procuradas TO david_borges_user;


--
-- TOC entry 3943 (class 0 OID 0)
-- Dependencies: 277
-- Name: TABLE pedido_troca_turno; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.pedido_troca_turno TO ana_almeida_user;
GRANT ALL ON TABLE public.pedido_troca_turno TO susana_tavares_user;
GRANT ALL ON TABLE public.pedido_troca_turno TO patricia_oliveira_user;
GRANT ALL ON TABLE public.pedido_troca_turno TO david_borges_user;


--
-- TOC entry 3945 (class 0 OID 0)
-- Dependencies: 276
-- Name: SEQUENCE pedido_troca_turno_id_pedido_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.pedido_troca_turno_id_pedido_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.pedido_troca_turno_id_pedido_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.pedido_troca_turno_id_pedido_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.pedido_troca_turno_id_pedido_seq TO david_borges_user;


--
-- TOC entry 3947 (class 0 OID 0)
-- Dependencies: 236
-- Name: SEQUENCE semestre_id_semestre_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.semestre_id_semestre_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.semestre_id_semestre_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.semestre_id_semestre_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.semestre_id_semestre_seq TO david_borges_user;


--
-- TOC entry 3949 (class 0 OID 0)
-- Dependencies: 238
-- Name: SEQUENCE turno_id_turno_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.turno_id_turno_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.turno_id_turno_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.turno_id_turno_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.turno_id_turno_seq TO david_borges_user;


--
-- TOC entry 3950 (class 0 OID 0)
-- Dependencies: 263
-- Name: TABLE uc_mais4etcs; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.uc_mais4etcs TO ana_almeida_user;
GRANT ALL ON TABLE public.uc_mais4etcs TO susana_tavares_user;
GRANT ALL ON TABLE public.uc_mais4etcs TO patricia_oliveira_user;
GRANT ALL ON TABLE public.uc_mais4etcs TO david_borges_user;


--
-- TOC entry 3952 (class 0 OID 0)
-- Dependencies: 241
-- Name: SEQUENCE unidade_curricular_id_unidadecurricular_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.unidade_curricular_id_unidadecurricular_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.unidade_curricular_id_unidadecurricular_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.unidade_curricular_id_unidadecurricular_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.unidade_curricular_id_unidadecurricular_seq TO david_borges_user;


--
-- TOC entry 3953 (class 0 OID 0)
-- Dependencies: 273
-- Name: TABLE utilizador; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.utilizador TO ana_almeida_user;
GRANT ALL ON TABLE public.utilizador TO susana_tavares_user;
GRANT ALL ON TABLE public.utilizador TO patricia_oliveira_user;
GRANT ALL ON TABLE public.utilizador TO david_borges_user;


--
-- TOC entry 3954 (class 0 OID 0)
-- Dependencies: 272
-- Name: SEQUENCE utilizador_id_seq; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON SEQUENCE public.utilizador_id_seq TO ana_almeida_user;
GRANT ALL ON SEQUENCE public.utilizador_id_seq TO susana_tavares_user;
GRANT ALL ON SEQUENCE public.utilizador_id_seq TO patricia_oliveira_user;
GRANT ALL ON SEQUENCE public.utilizador_id_seq TO david_borges_user;


--
-- TOC entry 3955 (class 0 OID 0)
-- Dependencies: 269
-- Name: TABLE vw_alunos_inscricoes_2025; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_alunos_inscricoes_2025 TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_alunos_inscricoes_2025 TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_alunos_inscricoes_2025 TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_alunos_inscricoes_2025 TO david_borges_user;


--
-- TOC entry 3956 (class 0 OID 0)
-- Dependencies: 262
-- Name: TABLE vw_alunos_matriculados_por_dia; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_alunos_matriculados_por_dia TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_alunos_matriculados_por_dia TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_alunos_matriculados_por_dia TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_alunos_matriculados_por_dia TO david_borges_user;


--
-- TOC entry 3957 (class 0 OID 0)
-- Dependencies: 265
-- Name: TABLE vw_alunos_por_ordem_alfabetica; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_alunos_por_ordem_alfabetica TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_alunos_por_ordem_alfabetica TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_alunos_por_ordem_alfabetica TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_alunos_por_ordem_alfabetica TO david_borges_user;


--
-- TOC entry 3958 (class 0 OID 0)
-- Dependencies: 267
-- Name: TABLE vw_cursos; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_cursos TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_cursos TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_cursos TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_cursos TO david_borges_user;


--
-- TOC entry 3959 (class 0 OID 0)
-- Dependencies: 268
-- Name: TABLE vw_top_docente_uc_ano_corrente; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_top_docente_uc_ano_corrente TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_top_docente_uc_ano_corrente TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_top_docente_uc_ano_corrente TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_top_docente_uc_ano_corrente TO david_borges_user;


--
-- TOC entry 3960 (class 0 OID 0)
-- Dependencies: 266
-- Name: TABLE vw_turnos; Type: ACL; Schema: public; Owner: neondb_owner
--

GRANT ALL ON TABLE public.vw_turnos TO ana_almeida_user;
GRANT ALL ON TABLE public.vw_turnos TO susana_tavares_user;
GRANT ALL ON TABLE public.vw_turnos TO patricia_oliveira_user;
GRANT ALL ON TABLE public.vw_turnos TO david_borges_user;


--
-- TOC entry 2275 (class 826 OID 16394)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- TOC entry 2273 (class 826 OID 32781)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: neondb_owner
--

ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON SEQUENCES TO ana_almeida_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON SEQUENCES TO susana_tavares_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON SEQUENCES TO patricia_oliveira_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON SEQUENCES TO david_borges_user;


--
-- TOC entry 2274 (class 826 OID 16393)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- TOC entry 2272 (class 826 OID 32780)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: neondb_owner
--

ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON TABLES TO ana_almeida_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON TABLES TO susana_tavares_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON TABLES TO patricia_oliveira_user;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public GRANT ALL ON TABLES TO david_borges_user;


--
-- TOC entry 3866 (class 0 OID 229430)
-- Dependencies: 293 3868
-- Name: mv_conflitos_horario; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: neondb_owner
--

REFRESH MATERIALIZED VIEW public.mv_conflitos_horario;


--
-- TOC entry 3863 (class 0 OID 229376)
-- Dependencies: 290 3868
-- Name: mv_estatisticas_turno; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: neondb_owner
--

REFRESH MATERIALIZED VIEW public.mv_estatisticas_turno;


--
-- TOC entry 3864 (class 0 OID 229391)
-- Dependencies: 291 3868
-- Name: mv_resumo_inscricoes_aluno; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: neondb_owner
--

REFRESH MATERIALIZED VIEW public.mv_resumo_inscricoes_aluno;


--
-- TOC entry 3865 (class 0 OID 229405)
-- Dependencies: 292 3868
-- Name: mv_ucs_mais_procuradas; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: neondb_owner
--

REFRESH MATERIALIZED VIEW public.mv_ucs_mais_procuradas;


-- Completed on 2026-01-20 14:43:58

--
-- PostgreSQL database dump complete
--

\unrestrict jSA7kiBeniMLqA4KdFr8HtiDmabyeR2a9owlsxM1IpacjyvFEfuNMk6cduvghuz

