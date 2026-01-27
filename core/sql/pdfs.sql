-- ============================================================================
-- FUNÇÕES DE GESTÃO DE PDFs
-- ============================================================================

-- Função para obter PDF horário por ID
CREATE OR REPLACE FUNCTION fn_get_pdf_horario(p_pdf_id INTEGER)
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_curso INTEGER, id_anocurricular INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_curso, id_anocurricular, atualizado_em
    FROM core_horariopdf
    WHERE id = p_pdf_id;
$$;

-- Função para obter PDF avaliação por ID
CREATE OR REPLACE FUNCTION fn_get_pdf_avaliacao(p_pdf_id INTEGER)
RETURNS TABLE(id INTEGER, nome TEXT, ficheiro TEXT, id_curso INTEGER, id_anocurricular INTEGER, atualizado_em TIMESTAMP)
LANGUAGE sql
AS $$
    SELECT id, nome, ficheiro, id_curso, id_anocurricular, atualizado_em
    FROM core_avaliacaopdf
    WHERE id = p_pdf_id;
$$;

-- Função para deletar PDF horário
CREATE OR REPLACE FUNCTION fn_delete_pdf_horario(p_pdf_id INTEGER)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM core_horariopdf WHERE id = p_pdf_id;
    RETURN FOUND;
END;
$$;

-- Função para deletar PDF avaliação
CREATE OR REPLACE FUNCTION fn_delete_pdf_avaliacao(p_pdf_id INTEGER)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM core_avaliacaopdf WHERE id = p_pdf_id;
    RETURN FOUND;
END;
$$;
