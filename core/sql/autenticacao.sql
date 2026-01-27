-- ============================================================================
-- FUNÇÕES DE AUTENTICAÇÃO
-- ============================================================================

-- Função para buscar admin por username ou email
CREATE OR REPLACE FUNCTION fn_fetch_admin(p_username_or_email TEXT)
RETURNS TABLE(id INTEGER, username TEXT, email TEXT, password TEXT, is_staff BOOLEAN, is_active BOOLEAN)
LANGUAGE sql
AS $$
    SELECT id, username, email, password, is_staff, is_active
    FROM auth_user
    WHERE (username = p_username_or_email OR email = p_username_or_email)
    LIMIT 1;
$$;

-- Função para buscar aluno por email
CREATE OR REPLACE FUNCTION fn_fetch_aluno_por_email(p_email TEXT)
RETURNS TABLE(n_mecanografico INTEGER, nome TEXT, email TEXT, password TEXT, id_curso INTEGER, id_anocurricular INTEGER)
LANGUAGE sql
AS $$
    SELECT n_mecanografico, nome, email, password, id_curso, id_anocurricular
    FROM aluno
    WHERE email = p_email
    LIMIT 1;
$$;

-- Função para buscar docente por email
CREATE OR REPLACE FUNCTION fn_fetch_docente_por_email(p_email TEXT)
RETURNS TABLE(id_docente INTEGER, nome TEXT, email TEXT, cargo TEXT)
LANGUAGE sql
AS $$
    SELECT id_docente, nome, email, cargo
    FROM docente
    WHERE email = p_email
    LIMIT 1;
$$;
