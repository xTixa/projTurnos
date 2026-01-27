-- Função para importar alunos em lote a partir de JSON
CREATE OR REPLACE FUNCTION importar_alunos_json(json_alunos JSON)
RETURNS VOID AS $$
DECLARE
    aluno JSON;
    n_mec INT;
    nome TEXT;
    email TEXT;
    curso_nome TEXT;
    ano_nome TEXT;
    passw TEXT;
    id_curso_int INT;
    id_ano_int INT;
BEGIN
    FOR aluno IN SELECT * FROM json_array_elements(json_alunos) LOOP
        n_mec := (aluno->>'n_mecanografico')::integer;
        nome := aluno->>'nome';
        email := aluno->>'email';
        curso_nome := aluno->>'curso';
        ano_nome := aluno->>'ano_curricular';
        passw := aluno->>'password';
        -- Normalizar curso e ano
        curso_nome := replace(replace(replace(replace(replace(replace(replace(replace(lower(trim(curso_nome)), 'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ã','a'),'ç','c'),'Âº','º');
        ano_nome := replace(replace(replace(replace(replace(replace(replace(replace(lower(trim(ano_nome)), 'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ã','a'),'ç','c'),'Âº','º');
        SELECT id_curso INTO id_curso_int FROM curso WHERE lower(trim(curso.nome)) = curso_nome LIMIT 1;
        SELECT id_anocurricular INTO id_ano_int FROM ano_curricular WHERE lower(trim(ano_curricular.ano_curricular)) = ano_nome LIMIT 1;
        IF id_curso_int IS NOT NULL AND id_ano_int IS NOT NULL AND passw IS NOT NULL THEN
            IF NOT EXISTS (SELECT 1 FROM aluno WHERE n_mecanografico = n_mec) THEN
                INSERT INTO aluno (n_mecanografico, nome, email, id_curso, id_anocurricular, password)
                VALUES (n_mec, nome, email, id_curso_int, id_ano_int, passw);
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Função para importar alunos em lote a partir de CSV, só insere se não existir
CREATE OR REPLACE FUNCTION importar_alunos_csv(conteudo_csv TEXT)
RETURNS VOID AS $$
DECLARE
    linha TEXT;
    campos TEXT[];
    i INT := 0;
    id_curso_int INT;
    id_ano_int INT;
BEGIN
    FOR linha IN SELECT unnest(string_to_array(conteudo_csv, E'\n')) LOOP
        i := i + 1;
        -- Ignora cabeçalho
        IF i = 1 THEN
            CONTINUE;
        END IF;
        campos := string_to_array(linha, ',');
        -- Ignorar cabeçalho ou linhas onde campos[1] não é numérico
        IF i = 1 OR campos[1] ~ '[^0-9]' THEN
            CONTINUE;
        END IF;
        IF array_length(campos, 1) = 6 THEN
            -- Normalizar/remover acentos simples (básico, para debug)
            campos[5] := replace(campos[5], 'Âº', 'º');
            campos[5] := replace(campos[5], 'á', 'a');
            campos[5] := replace(campos[5], 'é', 'e');
            campos[5] := replace(campos[5], 'í', 'i');
            campos[5] := replace(campos[5], 'ó', 'o');
            campos[5] := replace(campos[5], 'ú', 'u');
            campos[5] := replace(campos[5], 'ã', 'a');
            campos[5] := replace(campos[5], 'ç', 'c');
            campos[4] := replace(campos[4], 'á', 'a');
            campos[4] := replace(campos[4], 'é', 'e');
            campos[4] := replace(campos[4], 'í', 'i');
            campos[4] := replace(campos[4], 'ó', 'o');
            campos[4] := replace(campos[4], 'ú', 'u');
            campos[4] := replace(campos[4], 'ã', 'a');
            campos[4] := replace(campos[4], 'ç', 'c');
            -- Buscar id_curso pelo nome do curso
            id_curso_int := NULL;
            id_ano_int := NULL;
            SELECT id_curso INTO id_curso_int FROM curso WHERE TRIM(LOWER(nome)) = TRIM(LOWER(campos[4])) LIMIT 1;
            -- Buscar id_anocurricular pelo texto do ano curricular
            SELECT id_anocurricular INTO id_ano_int FROM ano_curricular WHERE TRIM(LOWER(ano_curricular)) = TRIM(LOWER(campos[5])) LIMIT 1;
            RAISE NOTICE 'Linha: %, Curso: %, Ano: %, id_curso: %, id_ano: %', linha, campos[4], campos[5], id_curso_int, id_ano_int;
            -- Só insere se encontrou curso e ano e n_mecanografico não existe
            IF id_curso_int IS NOT NULL AND id_ano_int IS NOT NULL THEN
                IF NOT EXISTS (
                    SELECT 1 FROM aluno WHERE n_mecanografico = campos[1]::integer
                ) THEN
                    INSERT INTO aluno (n_mecanografico, nome, email, id_curso, id_anocurricular, password)
                    VALUES (campos[1]::integer, campos[2], campos[3], id_curso_int, id_ano_int, campos[6]);
                END IF;
            END IF;
        END IF;
        END LOOP;
END;
$$ LANGUAGE plpgsql;
