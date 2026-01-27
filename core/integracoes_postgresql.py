"""
Integração de Procedures, Functions e Triggers do PostgreSQL
"""

from django.db import connection, connections
from django.contrib.auth.hashers import check_password
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PostgreSQLProcedures:
    @staticmethod
    def criar_aluno(n_mecanografico: int, id_curso: int, id_anocurricular: int, nome: str, email: str, password: str) -> bool:
        """
        Chama procedure criar_aluno
        Retorna True se sucesso, False se erro
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL criar_aluno(%s, %s, %s, %s, %s, %s)",
                    [n_mecanografico, id_curso, id_anocurricular, nome, email, password]
                )
            logger.info(f"Aluno {n_mecanografico} criado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar aluno: {e}")
            return False
    
    @staticmethod
    def atualizar_aluno(n_mecanografico: int, id_curso: int = None, id_anocurricular: int = None, nome: str = None, email: str = None, password: str = None) -> bool:
        """Chama procedure atualizar_aluno"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL atualizar_aluno(%s, %s, %s, %s, %s, %s)",
                    [n_mecanografico, id_curso, id_anocurricular, nome, email, password]
                )
            logger.info(f"Aluno {n_mecanografico} atualizado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar aluno: {e}")
            return False
    
    @staticmethod
    def apagar_aluno(n_mecanografico: int) -> bool:
        """Chama procedure apagar_aluno"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL apagar_aluno(%s)", [n_mecanografico])
            logger.info(f"Aluno {n_mecanografico} apagado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao apagar aluno: {e}")
            return False
    
    @staticmethod
    def criar_docente(nome: str, email: str, cargo: str) -> bool:
        """Chama procedure criar_docente"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL criar_docente(%s, %s, %s)",
                    [nome, email, cargo]
                )
            logger.info(f"Docente {nome} criado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar docente: {e}")
            return False
    
    @staticmethod
    def atualizar_docente(id_docente: int, nome: str = None, email: str = None, cargo: str = None) -> bool:
        """Chama procedure atualizar_docente"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL atualizar_docente(%s, %s, %s, %s)",
                    [id_docente, nome, email, cargo]
                )
            logger.info(f"Docente {id_docente} atualizado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar docente: {e}")
            return False
    
    @staticmethod
    def apagar_docente(id_docente: int) -> bool:
        """Chama procedure apagar_docente"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL apagar_docente(%s)", [id_docente])
            logger.info(f"Docente {id_docente} apagado via procedure")
            return True
        except Exception as e:
            logger.error(f"Erro ao apagar docente: {e}")
            return False


class PostgreSQLFunctions:
    @staticmethod
    def alunos_por_uc(id_uc: int, tipo_de_turno: str) -> List[Dict[str, Any]]:
        """
        Chama function alunos_por_uc
        Retorna lista de alunos inscritos em UC com tipo de turno específico
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM alunos_por_uc(%s, %s)",
                    [id_uc, tipo_de_turno]
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar alunos_por_uc: {e}")
            return []
    
    @staticmethod
    def alunos_inscritos_por_dia(data_inscricao) -> List[Dict[str, Any]]:
        """Chama function alunos_inscritos_por_dia"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM alunos_inscritos_por_dia(%s)",
                    [data_inscricao]
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar alunos_inscritos_por_dia: {e}")
            return []
    
    @staticmethod
    def inserir_matricula(id_anoletivo: int, n_mecanografico: int, data_matricula, estado: str) -> Tuple[str, bool]:
        """
        Chama function inserir_matricula
        Retorna (mensagem, sucesso)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM inserir_matricula(%s, %s, %s, %s)",
                    [id_anoletivo, n_mecanografico, data_matricula, estado]
                )
                result = cursor.fetchone()
                return result if result else ("Erro desconhecido", False)
        except Exception as e:
            logger.error(f"Erro ao inserir matrícula: {e}")
            return (str(e), False)
    
    @staticmethod
    def registar_log(entidade: str, operacao: str, chave_primaria: str, detalhes: str = None) -> bool:
        """Chama function registar_log"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT registar_log(%s, %s, %s, %s)",
                    [entidade, operacao, chave_primaria, detalhes]
                )
            logger.debug(f"Log registado: {entidade} - {operacao}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registar log: {e}")
            return False


class PostgreSQLViews:
    """Encapsula materialized views do PostgreSQL"""
    
    @staticmethod
    def refresh_all_views() -> bool:
        """Atualiza todas as materialized views"""
        views = [
            'mv_conflitos_horario',
            'mv_estatisticas_turno',
            'mv_resumo_inscricoes_aluno',
            'mv_ucs_mais_procuradas'
        ]
        
        try:
            with connection.cursor() as cursor:
                for view in views:
                    cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")
                    logger.info(f"View {view} atualizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar views: {e}")
            return False
    
    @staticmethod
    def conflitos_horario() -> List[Dict[str, Any]]:
        """Lê dados da view mv_conflitos_horario"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM mv_conflitos_horario")
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar conflitos: {e}")
            return []
    
    @staticmethod
    def estatisticas_turno() -> List[Dict[str, Any]]:
        """Lê dados da view mv_estatisticas_turno"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM mv_estatisticas_turno")
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return []


class PostgreSQLConsultas:
    """Consultas auxiliares (listas e dashboards) em SQL puro."""

    @staticmethod
    def cadeiras_semestre() -> List[Dict[str, Any]]:
        sql = """
            SELECT id_unidadecurricular, nome, ects, semestre_id, semestre_nome
            FROM cadeirassemestre
            ORDER BY semestre_id, nome
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar cadeiras_semestre: {e}")
            return []

    @staticmethod
    def alunos_por_ordem_alfabetica() -> List[Dict[str, Any]]:
        sql = """
            SELECT n_mecanografico, nome, email, id_anocurricular
            FROM vw_alunos_por_ordem_alfabetica
            ORDER BY nome
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar alunos por ordem: {e}")
            return []

    @staticmethod
    def turnos_list() -> List[Dict[str, Any]]:
        sql = """
            SELECT id_turno, n_turno, capacidade, tipo
            FROM vw_turnos
            ORDER BY id_turno
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos: {e}")
            return []

    @staticmethod
    def cursos_list() -> List[Dict[str, Any]]:
        sql = """
            SELECT id_curso, nome, grau
            FROM vw_cursos
            ORDER BY id_curso
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar cursos: {e}")
            return []

    @staticmethod
    def dashboard_totais() -> Dict[str, Any]:
        result = {
            "total_users": 0,
            "total_turnos": 0,
            "total_ucs": 0,
            "total_cursos": 0,
            "total_horarios": 0,
            "total_avaliacoes": 0,
            "vagas_total": 0,
            "vagas_ocupadas": 0,
        }
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                result["total_users"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM turno")
                result["total_turnos"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM unidade_curricular")
                result["total_ucs"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM curso")
                result["total_cursos"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM core_horariopdf")
                result["total_horarios"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM core_avaliacaopdf")
                result["total_avaliacoes"] = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(capacidade),0) FROM turno")
                result["vagas_total"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM inscricao_turno")
                result["vagas_ocupadas"] = cursor.fetchone()[0]

            return result
        except Exception as e:
            logger.error(f"Erro ao obter totais dashboard: {e}")
            return result

    @staticmethod
    def alunos_por_uc_top10() -> List[Dict[str, Any]]:
        sql = """
            SELECT uc.nome AS uc_nome, COUNT(*) AS total
            FROM inscrito_uc iu
            JOIN unidade_curricular uc ON uc.id_unidadecurricular = iu.id_unidadecurricular
            WHERE iu.estado = TRUE
            GROUP BY uc.nome
            ORDER BY total DESC
            LIMIT 10
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter top10 alunos por UC: {e}")
            return []

    @staticmethod
    def anos_curriculares() -> List[Dict[str, Any]]:
        sql = """
            SELECT id_anocurricular, ano_curricular
            FROM ano_curricular
            ORDER BY id_anocurricular
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar anos curriculares: {e}")
            return []

    @staticmethod
    def docentes() -> List[Dict[str, Any]]:
        sql = """
            SELECT id_docente, nome, email, cargo
            FROM docente
            ORDER BY nome
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar docentes: {e}")
            return []

    @staticmethod
    def ucs_por_curso(id_curso: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT uc.id_unidadecurricular, uc.nome, uc.id_anocurricular, uc.id_semestre, s.semestre
            FROM unidade_curricular uc
            JOIN semestre s ON s.id_semestre = uc.id_semestre
            WHERE uc.id_curso = %s
            ORDER BY uc.id_anocurricular, uc.id_semestre
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [id_curso])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs do curso {id_curso}: {e}")
            return []

    @staticmethod
    def pdfs_por_ano_curso(model_table: str, id_curso: int) -> List[Dict[str, Any]]:
        """model_table pode ser 'core_horariopdf' ou 'core_avaliacaopdf'"""
        sql = f"""
            SELECT ac.id_anocurricular, ac.ano_curricular, p.id, p.nome, p.ficheiro, p.atualizado_em, p.id_curso
            FROM {model_table} p
            JOIN ano_curricular ac ON ac.id_anocurricular = p.id_anocurricular
            WHERE p.id_curso = %s OR p.id_curso IS NULL
            ORDER BY ac.id_anocurricular DESC, p.atualizado_em DESC
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [id_curso])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar PDFs de {model_table}: {e}")
            return []

    @staticmethod
    def users_combinado() -> List[Dict[str, Any]]:
        """Lista combinada de admins (auth_user), alunos e docentes."""
        sql = """
            SELECT u.id::text AS id, u.username, u.email, u.date_joined, u.is_active, u.is_staff, 'Admin' AS tipo
            FROM auth_user u
            UNION ALL
            SELECT a.n_mecanografico::text, a.nome, a.email, NULL, true, false, 'Aluno'
            FROM aluno a
            UNION ALL
            SELECT d.id_docente::text, d.nome, d.email, NULL, true, false, 'Docente'
            FROM docente d
            ORDER BY tipo, id
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar users combinado: {e}")
            return []

    @staticmethod
    def get_user_by_id(user_id: int) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Encontra um user por ID em admin (auth_user), aluno ou docente.
        Retorna (user_dict, tipo) onde tipo é 'Admin', 'Aluno', 'Docente' ou None se não encontrado.
        """
        # Tenta admin primeiro
        sql_admin = "SELECT id, username, email, is_staff, is_active FROM auth_user WHERE id = %s LIMIT 1"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_admin, [user_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row)), "Admin"
        except Exception as e:
            logger.error(f"Erro ao obter admin {user_id}: {e}")

        # Tenta aluno
        sql_aluno = "SELECT n_mecanografico, nome, email, id_curso, id_anocurricular FROM aluno WHERE n_mecanografico = %s LIMIT 1"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_aluno, [user_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row)), "Aluno"
        except Exception as e:
            logger.error(f"Erro ao obter aluno {user_id}: {e}")

        # Tenta docente
        sql_docente = "SELECT id_docente, nome, email, cargo FROM docente WHERE id_docente = %s LIMIT 1"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_docente, [user_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row)), "Docente"
        except Exception as e:
            logger.error(f"Erro ao obter docente {user_id}: {e}")

        return None, None

    @staticmethod
    def update_user(user_id: int, user_type: str, username: str, email: str) -> bool:
        """Atualiza um user em auth_user, aluno ou docente."""
        if user_type == "Admin":
            sql = "UPDATE auth_user SET username = %s, email = %s WHERE id = %s"
        elif user_type == "Aluno":
            sql = "UPDATE aluno SET nome = %s, email = %s WHERE n_mecanografico = %s"
        elif user_type == "Docente":
            sql = "UPDATE docente SET nome = %s, email = %s WHERE id_docente = %s"
        else:
            return False

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [username, email, user_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar {user_type} {user_id}: {e}")
            return False

    @staticmethod
    def delete_aluno_cascade(n_mecanografico: int) -> Dict[str, int]:
        """
        Deleta um aluno e todas as suas referências (matriculas, inscricoes_turno, inscrito_uc).
        Retorna dict com contagens deletadas.
        """
        result = {"matriculas": 0, "inscricoes_turno": 0, "inscrito_uc": 0}
        try:
            with connection.cursor() as cursor:
                # Delete matricula
                cursor.execute("DELETE FROM matricula WHERE n_mecanografico = %s", [n_mecanografico])
                result["matriculas"] = cursor.rowcount

                # Delete inscricao_turno
                cursor.execute("DELETE FROM inscricao_turno WHERE n_mecanografico = %s", [n_mecanografico])
                result["inscricoes_turno"] = cursor.rowcount

                # Delete inscrito_uc
                cursor.execute("DELETE FROM inscrito_uc WHERE n_mecanografico = %s", [n_mecanografico])
                result["inscrito_uc"] = cursor.rowcount

                # Delete aluno
                cursor.execute("DELETE FROM aluno WHERE n_mecanografico = %s", [n_mecanografico])

            return result
        except Exception as e:
            logger.error(f"Erro ao deletar aluno {n_mecanografico} em cascata: {e}")
            return result

    @staticmethod
    def delete_docente_cascade(id_docente: int) -> Dict[str, int]:
        """
        Deleta um docente e todas as suas referências (leciona_uc).
        Retorna dict com contagens deletadas.
        """
        result = {"leciona_uc": 0}
        try:
            with connection.cursor() as cursor:
                # Delete leciona_uc
                cursor.execute("DELETE FROM leciona_uc WHERE id_docente = %s", [id_docente])
                result["leciona_uc"] = cursor.rowcount

                # Delete docente
                cursor.execute("DELETE FROM docente WHERE id_docente = %s", [id_docente])

            return result
        except Exception as e:
            logger.error(f"Erro ao deletar docente {id_docente} em cascata: {e}")
            return result

    @staticmethod
    def delete_admin_user(user_id: int) -> bool:
        """Deleta um admin user."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM auth_user WHERE id = %s", [user_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar admin {user_id}: {e}")
            return False

    @staticmethod
    def turnos_sem_uc() -> List[Dict[str, Any]]:
        """Lista turnos que não estão associados a nenhuma UC."""
        sql = """
            SELECT id_turno, n_turno, capacidade, tipo
            FROM turno
            WHERE id_turno NOT IN (SELECT DISTINCT id_turno FROM turno_uc)
            ORDER BY id_turno
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos sem UC: {e}")
            return []

    @staticmethod
    def get_turno_by_id(turno_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um turno pelo ID."""
        sql = "SELECT id_turno, n_turno, capacidade, tipo FROM turno WHERE id_turno = %s"
        try:
            ##alteracao_user_para
            with connections["admin"].cursor() as cursor:
                cursor.execute(sql, [turno_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"Erro ao obter turno {turno_id}: {e}")
            return None

    @staticmethod
    def create_turno(n_turno: str, capacidade: int, tipo: str) -> Optional[int]:
        """Cria um novo turno. Retorna o id_turno ou None se erro."""
        sql = "INSERT INTO turno (n_turno, capacidade, tipo) VALUES (%s, %s, %s) RETURNING id_turno"
        try:
            #with connection.cursor() as cursor:
            with connections["admin"].cursor() as cursor:
                cursor.execute(sql, [n_turno, capacidade, tipo])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao criar turno: {e}")
            return None

    @staticmethod
    def update_turno(turno_id: int, n_turno: str, capacidade: int, tipo: str) -> bool:
        """Atualiza um turno."""
        sql = "UPDATE turno SET n_turno = %s, capacidade = %s, tipo = %s WHERE id_turno = %s"
        try:
            #with connection.cursor() as cursor:
            with connections["admin"].cursor() as cursor:
                cursor.execute(sql, [n_turno, capacidade, tipo, turno_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar turno {turno_id}: {e}")
            return False

    @staticmethod
    def delete_turno(turno_id: int) -> bool:
        """Deleta um turno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM turno WHERE id_turno = %s", [turno_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar turno {turno_id}: {e}")
            return False

    @staticmethod
    def get_horario_pdf_by_id(pdf_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um horário PDF pelo ID."""
        sql = """
            SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
            FROM core_horariopdf
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [pdf_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"Erro ao obter horario_pdf {pdf_id}: {e}")
            return None

    @staticmethod
    def create_horario_pdf(nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> Optional[int]:
        """Cria um novo registro de horário PDF. Retorna o id ou None."""
        sql = """
            INSERT INTO core_horariopdf (nome, ficheiro, id_anocurricular, id_curso)
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, ficheiro, id_anocurricular, id_curso])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao criar horario_pdf: {e}")
            return None

    @staticmethod
    def update_horario_pdf(pdf_id: int, nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> bool:
        """Atualiza um registro de horário PDF."""
        sql = """
            UPDATE core_horariopdf
            SET nome = %s, ficheiro = %s, id_anocurricular = %s, id_curso = %s
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, ficheiro, id_anocurricular, id_curso, pdf_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar horario_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def delete_horario_pdf(pdf_id: int) -> bool:
        """Deleta um registro de horário PDF."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM core_horariopdf WHERE id = %s", [pdf_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar horario_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def list_horario_pdfs() -> List[Dict[str, Any]]:
        """Lista todos os horários PDF."""
        sql = """
            SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
            FROM core_horariopdf
            ORDER BY atualizado_em DESC
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar horario_pdfs: {e}")
            return []

    @staticmethod
    def get_latest_horario_pdf() -> Optional[Dict[str, Any]]:
        """Obtém o horário PDF mais recente."""
        sql = """
            SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
            FROM core_horariopdf
            ORDER BY atualizado_em DESC
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"Erro ao obter latest horario_pdf: {e}")
            return None

    @staticmethod
    def get_avaliacao_pdf_by_id(pdf_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um PDF de avaliação pelo ID."""
        sql = """
            SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
            FROM core_avaliacaopdf
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [pdf_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"Erro ao obter avaliacao_pdf {pdf_id}: {e}")
            return None

    @staticmethod
    def create_avaliacao_pdf(nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> Optional[int]:
        """Cria um novo registro de PDF de avaliação. Retorna o id ou None."""
        sql = """
            INSERT INTO core_avaliacaopdf (nome, ficheiro, id_anocurricular, id_curso)
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, ficheiro, id_anocurricular, id_curso])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao criar avaliacao_pdf: {e}")
            return None

    @staticmethod
    def update_avaliacao_pdf(pdf_id: int, nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> bool:
        """Atualiza um registro de PDF de avaliação."""
        sql = """
            UPDATE core_avaliacaopdf
            SET nome = %s, ficheiro = %s, id_anocurricular = %s, id_curso = %s
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, ficheiro, id_anocurricular, id_curso, pdf_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar avaliacao_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def delete_avaliacao_pdf(pdf_id: int) -> bool:
        """Deleta um registro de PDF de avaliação."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM core_avaliacaopdf WHERE id = %s", [pdf_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar avaliacao_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def list_avaliacao_pdfs() -> List[Dict[str, Any]]:
        """Lista todos os PDFs de avaliação."""
        sql = """
            SELECT id, nome, ficheiro, id_anocurricular, id_curso, atualizado_em
            FROM core_avaliacaopdf
            ORDER BY atualizado_em DESC
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar avaliacao_pdfs: {e}")
            return []

    @staticmethod
    def get_uc_by_id(uc_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma UC pelo ID."""
        sql = """
            SELECT id_unidadecurricular, nome, id_curso, id_anocurricular, id_semestre, ects
            FROM unidade_curricular
            WHERE id_unidadecurricular = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [uc_id])
                row = cursor.fetchone()
                if row:
                    cols = [col[0] for col in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"Erro ao obter UC {uc_id}: {e}")
            return None

    @staticmethod
    def list_all_ucs() -> List[Dict[str, Any]]:
        """Lista todas as UCs."""
        sql = """
            SELECT id_unidadecurricular, nome, id_curso, id_anocurricular, id_semestre, ects
            FROM unidade_curricular
            ORDER BY id_unidadecurricular
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs: {e}")
            return []

    @staticmethod
    def create_uc(nome: str, id_curso: int, id_anocurricular: int, id_semestre: int, ects: float) -> Optional[int]:
        """Cria uma nova UC. Retorna o id_unidadecurricular ou None."""
        sql = """
            INSERT INTO unidade_curricular (nome, id_curso, id_anocurricular, id_semestre, ects)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_unidadecurricular
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, id_curso, id_anocurricular, id_semestre, ects])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Erro ao criar UC: {e}")
            return None

    @staticmethod
    def update_uc(uc_id: int, nome: str, id_curso: int, id_anocurricular: int, id_semestre: int, ects: float) -> bool:
        """Atualiza uma UC."""
        sql = """
            UPDATE unidade_curricular
            SET nome = %s, id_curso = %s, id_anocurricular = %s, id_semestre = %s, ects = %s
            WHERE id_unidadecurricular = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [nome, id_curso, id_anocurricular, id_semestre, ects, uc_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar UC {uc_id}: {e}")
            return False

    @staticmethod
    def delete_uc(uc_id: int) -> bool:
        """Deleta uma UC."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM unidade_curricular WHERE id_unidadecurricular = %s", [uc_id])
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar UC {uc_id}: {e}")
            return False

    @staticmethod
    def get_turnos_uc_by_uc_id(uc_id: int) -> List[Dict[str, Any]]:
        """Lista os turnos associados a uma UC."""
        sql = """
            SELECT tu.id_turno, t.n_turno, t.tipo, t.capacidade, tu.hora_inicio, tu.hora_fim
            FROM turno_uc tu
            JOIN turno t ON t.id_turno = tu.id_turno
            WHERE tu.id_unidadecurricular = %s
            ORDER BY t.n_turno
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [uc_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos_uc da UC {uc_id}: {e}")
            return []

    @staticmethod
    def delete_turnos_uc_by_uc_id(uc_id: int) -> int:
        """Deleta todos os turnos_uc associados a uma UC. Retorna número de registos deletados."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM turno_uc WHERE id_unidadecurricular = %s", [uc_id])
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Erro ao deletar turnos_uc da UC {uc_id}: {e}")
            return 0

    @staticmethod
    def create_turno_uc(id_turno: int, id_uc: int, hora_inicio: str, hora_fim: str) -> bool:
        """Cria um turno_uc (associação turno-UC)."""
        sql = """
            INSERT INTO turno_uc (id_turno, id_unidadecurricular, hora_inicio, hora_fim)
            VALUES (%s, %s, %s, %s)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [id_turno, id_uc, hora_inicio, hora_fim])
                return True
        except Exception as e:
            logger.error(f"Erro ao criar turno_uc: {e}")
            return False

    @staticmethod
    def get_semestres() -> List[Dict[str, Any]]:
        """Lista todos os semestres."""
        sql = "SELECT id_semestre, semestre FROM semestre ORDER BY id_semestre"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar semestres: {e}")
            return []


class PostgreSQLDAPE:
    """Operações DAPE (propostas de estágio e favoritos) via SQL/procedures."""

    # =============================
    # PROPOSTAS
    # =============================
    @staticmethod
    def listar_propostas(filtro: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista propostas. Filtros suportados:
        - aluno_id: int
        - titulo: str (match exato)
        """
        base_sql = """
            SELECT p.id_proposta, p.aluno_id, p.titulo, p.entidade, p.descricao,
                   p.requisitos, p.modelo, p.orientador_empresa, p.telefone,
                   p.email, p.logo, p.aluno_atribuido, p.criado_em, p.atualizado_em
            FROM proposta_estagio p
        """
        where_clauses = []
        params: List[Any] = []

        filtro = filtro or {}
        if "aluno_id" in filtro and filtro["aluno_id"]:
            where_clauses.append("p.aluno_id = %s")
            params.append(filtro["aluno_id"])
        if "titulo" in filtro and filtro["titulo"]:
            where_clauses.append("p.titulo = %s")
            params.append(filtro["titulo"])

        sql = base_sql
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY p.atualizado_em DESC, p.id_proposta DESC"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                cols = [c[0] for c in cursor.description]
                return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro a listar propostas DAPE: {e}")
            return []

    @staticmethod
    def obter_proposta_por_id(id_proposta: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id_proposta, aluno_id, titulo, entidade, descricao,
                   requisitos, modelo, orientador_empresa, telefone,
                   email, logo, aluno_atribuido, criado_em, atualizado_em
            FROM proposta_estagio WHERE id_proposta = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [id_proposta])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [c[0] for c in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro a obter proposta {id_proposta}: {e}")
            return None

    @staticmethod
    def criar_proposta(aluno_id: Optional[int], titulo: str, entidade: Optional[str],
                       descricao: Optional[str], requisitos: Optional[str],
                       modelo: Optional[str], orientador_empresa: Optional[str],
                       telefone: Optional[str], email: Optional[str], logo: Optional[str]) -> Optional[int]:
        """
        Tenta chamar a procedure dape_criar_proposta; caso não exista, faz INSERT direto.
        Retorna id_proposta ou None.
        """
        # Tenta procedure (function que retorna id)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT dape_criar_proposta(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [aluno_id, titulo, entidade, descricao, requisitos, modelo,
                     orientador_empresa, telefone, email, logo]
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return int(row[0])
        except Exception as e:
            logger.debug(f"Procedure dape_criar_proposta indisponível, fallback INSERT. Erro: {e}")

        # Fallback INSERT
        insert_sql = """
            INSERT INTO proposta_estagio (
                aluno_id, titulo, entidade, descricao, requisitos, modelo,
                orientador_empresa, telefone, email, logo
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_proposta
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(insert_sql, [aluno_id, titulo, entidade, descricao, requisitos,
                                            modelo, orientador_empresa, telefone, email, logo])
                r = cursor.fetchone()
                return int(r[0]) if r else None
        except Exception as e:
            logger.error(f"Erro a criar proposta DAPE: {e}")
            return None

    @staticmethod
    def atualizar_proposta(aluno_id: int, titulo_atual: str, updates: Dict[str, Any]) -> bool:
        """Atualiza proposta do aluno. Tenta procedure; fallback UPDATE direto."""
        # Tenta procedure
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL dape_atualizar_proposta(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [aluno_id,
                     titulo_atual,
                     updates.get("titulo"), updates.get("entidade"), updates.get("descricao"),
                     updates.get("requisitos"), updates.get("modelo"), updates.get("orientador_empresa"),
                     updates.get("telefone"), updates.get("email")]
                )
                return True
        except Exception:
            pass

        # Fallback UPDATE dinâmico
        allowed = [
            "titulo", "entidade", "descricao", "requisitos", "modelo",
            "orientador_empresa", "telefone", "email", "logo"
        ]
        set_parts = []
        params: List[Any] = []
        for k in allowed:
            if k in updates and updates[k] is not None:
                set_parts.append(f"{k} = %s")
                params.append(updates[k])
        if not set_parts:
            return True
        params.extend([aluno_id, titulo_atual])
        sql = f"UPDATE proposta_estagio SET {', '.join(set_parts)}, atualizado_em = NOW() WHERE aluno_id = %s AND titulo = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro a atualizar proposta DAPE: {e}")
            return False

    @staticmethod
    def eliminar_proposta(aluno_id: int, titulo: str) -> bool:
        """Elimina proposta do aluno. Tenta procedure; fallback DELETE direto."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL dape_eliminar_proposta(%s,%s)", [aluno_id, titulo])
                return True
        except Exception:
            pass
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM proposta_estagio WHERE aluno_id = %s AND titulo = %s", [aluno_id, titulo])
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro a eliminar proposta DAPE: {e}")
            return False

    # =============================
    # ADMIN OPS POR ID
    # =============================
    @staticmethod
    def admin_atualizar_proposta(id_proposta: int, updates: Dict[str, Any]) -> bool:
        """Atualiza proposta por ID (admin). Tenta procedure; fallback UPDATE direto."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL dape_admin_atualizar_proposta(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [id_proposta,
                     updates.get("titulo"), updates.get("entidade"), updates.get("descricao"),
                     updates.get("requisitos"), updates.get("modelo"), updates.get("orientador_empresa"),
                     updates.get("telefone"), updates.get("email"), updates.get("logo")]
                )
                return True
        except Exception:
            pass

        allowed = [
            "titulo", "entidade", "descricao", "requisitos", "modelo",
            "orientador_empresa", "telefone", "email", "logo"
        ]
        set_parts = []
        params: List[Any] = []
        for k in allowed:
            if k in updates and updates[k] is not None:
                set_parts.append(f"{k} = %s")
                params.append(updates[k])
        if not set_parts:
            return True
        params.append(id_proposta)
        sql = f"UPDATE proposta_estagio SET {', '.join(set_parts)}, atualizado_em = NOW() WHERE id_proposta = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro admin atualizar proposta DAPE: {e}")
            return False

    @staticmethod
    def admin_eliminar_proposta(id_proposta: int) -> bool:
        """Elimina proposta por ID (admin). Tenta procedure; fallback DELETE direto."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL dape_admin_eliminar_proposta(%s)", [id_proposta])
                return True
        except Exception:
            pass
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM favorito_proposta WHERE id_proposta = %s", [id_proposta])
                cursor.execute("DELETE FROM proposta_estagio WHERE id_proposta = %s", [id_proposta])
                return True
        except Exception as e:
            logger.error(f"Erro admin eliminar proposta DAPE: {e}")
            return False

    # =============================
    # FAVORITOS
    # =============================
    @staticmethod
    def listar_favoritos(aluno_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.*
            FROM favorito_proposta f
            JOIN proposta_estagio p ON p.id_proposta = f.id_proposta
            WHERE f.aluno_id = %s
            ORDER BY p.atualizado_em DESC, p.id_proposta DESC
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [aluno_id])
                cols = [c[0] for c in cursor.description]
                return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro a listar favoritos DAPE: {e}")
            return []

    @staticmethod
    def verificar_favorito(aluno_id: int, id_proposta: int) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM favorito_proposta WHERE aluno_id = %s AND id_proposta = %s",
                    [aluno_id, id_proposta]
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Erro a verificar favorito DAPE: {e}")
            return False

    @staticmethod
    def toggle_favorito(aluno_id: int, id_proposta: int) -> Dict[str, Any]:
        """Adiciona/remove favorito (upsert/delete). Retorna {added: bool}."""
        # Tenta procedure
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dape_toggle_favorito(%s,%s)", [aluno_id, id_proposta])
                row = cursor.fetchone()
                if row is not None:
                    return {"added": bool(row[0])}
        except Exception:
            pass

        # Fallback lógico
        if PostgreSQLDAPE.verificar_favorito(aluno_id, id_proposta):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM favorito_proposta WHERE aluno_id = %s AND id_proposta = %s",
                        [aluno_id, id_proposta]
                    )
                return {"added": False}
            except Exception as e:
                logger.error(f"Erro a remover favorito DAPE: {e}")
                return {"added": False}
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO favorito_proposta (aluno_id, id_proposta)
                        VALUES (%s, %s)
                        ON CONFLICT (aluno_id, id_proposta) DO NOTHING
                        """,
                        [aluno_id, id_proposta]
                    )
                return {"added": True}
            except Exception as e:
                logger.error(f"Erro a adicionar favorito DAPE: {e}")
                return {"added": False}


class PostgreSQLAuth:
    """Autenticação via SQL puro (sem ORM) para admin, aluno e docente."""

    @staticmethod
    def fetch_admin(username_or_email: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, username, email, password, is_staff, is_active
            FROM auth_user
            WHERE (username = %s OR email = %s)
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [username_or_email, username_or_email])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter admin: {e}")
            return None

    @staticmethod
    def validar_password(hash_pwd: str, password: str) -> bool:
        """Valida hash Django (auth_user.password) contra password fornecida."""
        try:
            return check_password(password, hash_pwd)
        except Exception:
            return False

    @staticmethod
    def fetch_aluno_por_email(email: str) -> Optional[Dict[str, Any]]:
        """Busca aluno por email na tabela aluno."""
        sql = """
            SELECT n_mecanografico, nome, email, password, id_curso, id_anocurricular
            FROM aluno
            WHERE email = %s
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [email])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter aluno: {e}")
            return None

    @staticmethod
    def fetch_docente_por_email(email: str) -> Optional[Dict[str, Any]]:
        """Busca docente por email na tabela docente."""
        sql = """
            SELECT id_docente, nome, email, password, cargo
            FROM docente
            WHERE email = %s
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [email])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter docente: {e}")
            return None


class PostgreSQLPDF:
    """Operações com PDFs via SQL puro."""

    @staticmethod
    def delete_pdf(pdf_id: int, pdf_type: str) -> bool:
        """Apaga um PDF (horario ou avaliacao) por ID."""
        table_name = 'core_horariopdf' if pdf_type == 'horario' else 'core_avaliacaopdf'
        sql = f"""
            DELETE FROM {table_name}
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [pdf_id])
            return True
        except Exception as e:
            logger.error(f"Erro ao apagar PDF: {e}")
            return False

    @staticmethod
    def get_pdf(pdf_id: int, pdf_type: str) -> Optional[Dict[str, Any]]:
        """Obtém um PDF específico."""
        table_name = 'core_horariopdf' if pdf_type == 'horario' else 'core_avaliacaopdf'
        sql = f"""
            SELECT id, nome, ficheiro, id_curso, id_anocurricular, atualizado_em
            FROM {table_name}
            WHERE id = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [pdf_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter PDF: {e}")
            return None


class PostgreSQLLogs:
    """Operações com logs de eventos via SQL puro."""

    @staticmethod
    def list_logs(operacao_filter: Optional[str] = None, entidade_filter: Optional[str] = None, limite: int = 100) -> List[Dict[str, Any]]:
        """Lista logs com filtros opcionais."""
        sql = "SELECT * FROM log_eventos WHERE 1=1"
        params = []

        if operacao_filter:
            sql += " AND operacao ILIKE %s"
            params.append(f"%{operacao_filter}%")

        if entidade_filter:
            sql += " AND entidade ILIKE %s"
            params.append(f"%{entidade_filter}%")

        sql += " ORDER BY data_hora DESC LIMIT %s"
        params.append(limite)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar logs: {e}")
            return []

    @staticmethod
    def get_distinct_operacoes() -> List[str]:
        """Obtém lista de operações distintas."""
        sql = "SELECT DISTINCT operacao FROM log_eventos WHERE operacao IS NOT NULL AND operacao != '' ORDER BY operacao"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter operações: {e}")
            return []

    @staticmethod
    def get_distinct_entidades() -> List[str]:
        """Obtém lista de entidades distintas."""
        sql = "SELECT DISTINCT entidade FROM log_eventos WHERE entidade IS NOT NULL AND entidade != '' ORDER BY entidade"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter entidades: {e}")
            return []


class PostgreSQLTurnos:
    """Operações de inscrição em turnos via SQL (sem ORM)."""

    @staticmethod
    def get_aluno(n_mecanografico: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT n_mecanografico, nome, email, id_curso, id_anocurricular
            FROM aluno
            WHERE n_mecanografico = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [n_mecanografico])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter aluno {n_mecanografico}: {e}")
            return None

    @staticmethod
    def get_turno(turno_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id_turno, n_turno, tipo, capacidade
            FROM turno
            WHERE id_turno = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [turno_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter turno {turno_id}: {e}")
            return None

    @staticmethod
    def get_uc(uc_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id_unidadecurricular, nome, id_curso, id_anocurricular
            FROM unidade_curricular
            WHERE id_unidadecurricular = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [uc_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter UC {uc_id}: {e}")
            return None

    @staticmethod
    def turno_pertence_uc(turno_id: int, uc_id: int) -> bool:
        sql = """
            SELECT 1 FROM turno_uc
            WHERE id_turno = %s AND id_unidadecurricular = %s
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [turno_id, uc_id])
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Erro ao validar turno/UC: {e}")
            return False

    @staticmethod
    def inscrito_na_uc(n_mecanografico: int, uc_id: int) -> bool:
        sql = """
            SELECT 1 FROM inscrito_uc
            WHERE n_mecanografico = %s AND id_unidadecurricular = %s AND estado = TRUE
            LIMIT 1
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [n_mecanografico, uc_id])
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Erro ao verificar inscrito_uc: {e}")
            return False

    @staticmethod
    def count_inscritos(turno_id: int, uc_id: int) -> int:
        sql = """
            SELECT COUNT(*) FROM inscricao_turno
            WHERE id_turno = %s AND id_unidadecurricular = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [turno_id, uc_id])
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error(f"Erro ao contar inscritos: {e}")
            return 0

    @staticmethod
    def create_inscricao_turno(n_mecanografico: int, turno_id: int, uc_id: int) -> bool:
        sql = """
            INSERT INTO inscricao_turno (n_mecanografico, id_turno, id_unidadecurricular, data_inscricao)
            VALUES (%s, %s, %s, CURRENT_DATE)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [n_mecanografico, turno_id, uc_id])
            return True
        except Exception as e:
            logger.error(f"Erro ao criar inscricao_turno: {e}")
            return False

    @staticmethod
    def delete_inscricao_turno(n_mecanografico: int, turno_id: int, uc_id: Optional[int] = None) -> int:
        if uc_id is not None:
            sql = """
                DELETE FROM inscricao_turno
                WHERE n_mecanografico = %s AND id_turno = %s AND id_unidadecurricular = %s
            """
            params = [n_mecanografico, turno_id, uc_id]
        else:
            sql = """
                DELETE FROM inscricao_turno
                WHERE n_mecanografico = %s AND id_turno = %s
            """
            params = [n_mecanografico, turno_id]
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Erro ao apagar inscricao_turno: {e}")
            return 0

    @staticmethod
    def turno_uc_por_uc(uc_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT tu.id_unidadecurricular, t.id_turno, t.n_turno, t.tipo, t.capacidade, tu.hora_inicio, tu.hora_fim
            FROM turno_uc tu
            JOIN turno t ON t.id_turno = tu.id_turno
            WHERE tu.id_unidadecurricular = %s
            ORDER BY t.id_turno
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [uc_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar turnos da UC {uc_id}: {e}")
            return []

    @staticmethod
    def ucs_inscritas_por_aluno(n_mecanografico: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT iu.id_unidadecurricular,
                   uc.nome,
                   uc.id_curso,
                   uc.id_anocurricular
            FROM inscrito_uc iu
            JOIN unidade_curricular uc ON uc.id_unidadecurricular = iu.id_unidadecurricular
            WHERE iu.n_mecanografico = %s AND iu.estado = TRUE
            ORDER BY uc.nome
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [n_mecanografico])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs inscritas do aluno {n_mecanografico}: {e}")
            return []

    @staticmethod
    def inscricoes_turno_por_aluno(n_mecanografico: int) -> List[Dict[str, Any]]:
        sql = """
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
            WHERE it.n_mecanografico = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [n_mecanografico])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar inscricoes turno: {e}")
            return []

    @staticmethod
    def turno_uc_por_turno(turno_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT id_turno, id_unidadecurricular, hora_inicio, hora_fim
            FROM turno_uc
            WHERE id_turno = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [turno_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter turno_uc por turno: {e}")
            return []

    @staticmethod
    def validar_password(hash_pwd: str, password: str) -> bool:
        try:
            return check_password(password, hash_pwd)
        except Exception:
            return False
