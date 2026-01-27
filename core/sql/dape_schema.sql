-- DAPE schema and procedures

-- Tables
CREATE TABLE IF NOT EXISTS proposta_estagio (
    id_proposta SERIAL PRIMARY KEY,
    aluno_id INTEGER NULL,
    titulo TEXT NOT NULL,
    entidade TEXT NULL,
    descricao TEXT NULL,
    requisitos TEXT NULL,
    modelo TEXT NULL,
    orientador_empresa TEXT NULL,
    telefone TEXT NULL,
    email TEXT NULL,
    logo TEXT NULL,
    aluno_atribuido INTEGER NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proposta_estagio_aluno ON proposta_estagio(aluno_id);

CREATE TABLE IF NOT EXISTS favorito_proposta (
    aluno_id INTEGER NOT NULL,
    id_proposta INTEGER NOT NULL REFERENCES proposta_estagio(id_proposta) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (aluno_id, id_proposta)
);

-- Trigger to update atualizado_em
CREATE OR REPLACE FUNCTION trg_proposta_touch() RETURNS TRIGGER AS $$
BEGIN
  NEW.atualizado_em := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Admin: update by ID
CREATE OR REPLACE PROCEDURE dape_admin_atualizar_proposta(
    p_id_proposta INTEGER,
    p_titulo TEXT,
    p_entidade TEXT,
    p_descricao TEXT,
    p_requisitos TEXT,
    p_modelo TEXT,
    p_orientador_empresa TEXT,
    p_telefone TEXT,
    p_email TEXT,
    p_logo TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE proposta_estagio
    SET titulo = COALESCE(p_titulo, titulo),
        entidade = COALESCE(p_entidade, entidade),
        descricao = COALESCE(p_descricao, descricao),
        requisitos = COALESCE(p_requisitos, requisitos),
        modelo = COALESCE(p_modelo, modelo),
        orientador_empresa = COALESCE(p_orientador_empresa, orientador_empresa),
        telefone = COALESCE(p_telefone, telefone),
        email = COALESCE(p_email, email),
        logo = COALESCE(p_logo, logo)
    WHERE id_proposta = p_id_proposta;
END;
$$;

-- Admin: delete by ID
CREATE OR REPLACE PROCEDURE dape_admin_eliminar_proposta(
    p_id_proposta INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM favorito_proposta WHERE id_proposta = p_id_proposta;
    DELETE FROM proposta_estagio WHERE id_proposta = p_id_proposta;
END;
$$;

DROP TRIGGER IF EXISTS trg_proposta_touch ON proposta_estagio;
CREATE TRIGGER trg_proposta_touch
BEFORE UPDATE ON proposta_estagio
FOR EACH ROW EXECUTE FUNCTION trg_proposta_touch();

-- Functions/Procedures
-- Returns new id_proposta
CREATE OR REPLACE FUNCTION dape_criar_proposta(
    p_aluno_id INTEGER,
    p_titulo TEXT,
    p_entidade TEXT,
    p_descricao TEXT,
    p_requisitos TEXT,
    p_modelo TEXT,
    p_orientador_empresa TEXT,
    p_telefone TEXT,
    p_email TEXT,
    p_logo TEXT
) RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    INSERT INTO proposta_estagio (
        aluno_id, titulo, entidade, descricao, requisitos, modelo,
        orientador_empresa, telefone, email, logo
    ) VALUES (
        p_aluno_id, p_titulo, p_entidade, p_descricao, p_requisitos, p_modelo,
        p_orientador_empresa, p_telefone, p_email, p_logo
    ) RETURNING id_proposta INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Update by (aluno_id, titulo_atual)
CREATE OR REPLACE PROCEDURE dape_atualizar_proposta(
    p_aluno_id INTEGER,
    p_titulo_atual TEXT,
    p_titulo TEXT,
    p_entidade TEXT,
    p_descricao TEXT,
    p_requisitos TEXT,
    p_modelo TEXT,
    p_orientador_empresa TEXT,
    p_telefone TEXT,
    p_email TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE proposta_estagio
    SET titulo = COALESCE(p_titulo, titulo),
        entidade = COALESCE(p_entidade, entidade),
        descricao = COALESCE(p_descricao, descricao),
        requisitos = COALESCE(p_requisitos, requisitos),
        modelo = COALESCE(p_modelo, modelo),
        orientador_empresa = COALESCE(p_orientador_empresa, orientador_empresa),
        telefone = COALESCE(p_telefone, telefone),
        email = COALESCE(p_email, email)
    WHERE aluno_id = p_aluno_id AND titulo = p_titulo_atual;
END;
$$;

CREATE OR REPLACE PROCEDURE dape_eliminar_proposta(
    p_aluno_id INTEGER,
    p_titulo TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM proposta_estagio
    WHERE aluno_id = p_aluno_id AND titulo = p_titulo;
END;
$$;

-- Toggle favorito: returns true if added, false if removed
CREATE OR REPLACE FUNCTION dape_toggle_favorito(
    p_aluno_id INTEGER,
    p_id_proposta INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM favorito_proposta
        WHERE aluno_id = p_aluno_id AND id_proposta = p_id_proposta
    ) INTO v_exists;

    IF v_exists THEN
        DELETE FROM favorito_proposta
        WHERE aluno_id = p_aluno_id AND id_proposta = p_id_proposta;
        RETURN FALSE;
    ELSE
        INSERT INTO favorito_proposta (aluno_id, id_proposta)
        VALUES (p_aluno_id, p_id_proposta)
        ON CONFLICT DO NOTHING;
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;