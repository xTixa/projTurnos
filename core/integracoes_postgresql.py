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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
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
            with connections["admin"].cursor() as cursor:
                for view in views:
                    cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")
                    logger.info(f"View {view} atualizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar views: {e}")
            return False
    #verificar mais tarde
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
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM mv_estatisticas_turno")
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return []


class PostgreSQLConsultas:
    """Consultas auxiliares (listas e dashboards) via functions SQL."""

    @staticmethod
    def cadeiras_semestre() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_cadeiras_semestre()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar cadeiras_semestre: {e}")
            return []

    @staticmethod
    def alunos_por_ordem_alfabetica() -> List[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_alunos_por_ordem_alfabetica()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar alunos por ordem: {e}")
            return []

    @staticmethod
    def turnos_list() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_turnos_list()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos: {e}")
            return []

    @staticmethod
    def cursos_list() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_cursos_list()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar cursos: {e}")
            return []

    @staticmethod
    def dashboard_totais() -> Dict[str, Any]:
        fallback = {
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
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_dashboard_totais()")
                row = cursor.fetchone()
                if not row:
                    return fallback
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter totais dashboard: {e}")
            return fallback

    @staticmethod
    def alunos_por_uc_top10() -> List[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_alunos_por_uc_top10()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter top10 alunos por UC: {e}")
            return []

    @staticmethod
    def anos_curriculares() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_anos_curriculares()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar anos curriculares: {e}")
            return []

    @staticmethod
    def docentes() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_docentes()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar docentes: {e}")
            return []

    @staticmethod
    def ucs_por_curso(id_curso: int) -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_ucs_por_curso(%s)", [id_curso])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs do curso {id_curso}: {e}")
            return []

    @staticmethod
    def pdfs_por_ano_curso(model_table: str, id_curso: int) -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_pdfs_por_ano_curso(%s, %s)", [model_table, id_curso])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar PDFs de {model_table}: {e}")
            return []

    @staticmethod
    def users_combinado() -> List[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_users_combinado()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar users combinado: {e}")
            return []

    @staticmethod
    def get_user_by_id(user_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_user_by_id(%s)", [user_id])
                row = cursor.fetchone()
                if not row:
                    return None, None
                cols = [col[0] for col in cursor.description]
                data = dict(zip(cols, row))
                user_type = data.pop("tipo", None)
                return data, user_type
        except Exception as e:
            logger.error(f"Erro ao obter utilizador {user_id}: {e}")
            return None, None

    @staticmethod
    def update_user(user_id: int, user_type: str, username: str, email: str) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_update_user(%s, %s, %s, %s)",
                    [user_id, user_type, username, email],
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao atualizar {user_type} {user_id}: {e}")
            return False

    @staticmethod
    def delete_aluno_cascade(n_mecanografico: int) -> Dict[str, int]:
        fallback = {"matriculas": 0, "inscricoes_turno": 0, "inscrito_uc": 0}
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_delete_aluno_cascade(%s)", [n_mecanografico])
                row = cursor.fetchone()
                if not row:
                    return fallback
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao deletar aluno {n_mecanografico} em cascata: {e}")
            return fallback

    @staticmethod
    def delete_docente_cascade(id_docente: int) -> Dict[str, int]:
        fallback = {"leciona_uc": 0}
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_delete_docente_cascade(%s)", [id_docente])
                row = cursor.fetchone()
                if not row:
                    return fallback
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao deletar docente {id_docente} em cascata: {e}")
            return fallback

    @staticmethod
    def delete_admin_user(user_id: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_admin_user(%s)", [user_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao deletar admin {user_id}: {e}")
            return False

    @staticmethod
    def turnos_sem_uc() -> List[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_turnos_sem_uc()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos sem UC: {e}")
            return []

    @staticmethod
    def get_turno_by_id(turno_id: int) -> Optional[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_turno_by_id(%s)", [turno_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter turno {turno_id}: {e}")
            return None

    @staticmethod
    def create_turno(n_turno: str, capacidade: int, tipo: str) -> Optional[int]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_create_turno(%s, %s, %s)", [n_turno, capacidade, tipo])
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] is not None else None
        except Exception as e:
            logger.error(f"Erro ao criar turno: {e}")
            return None

    @staticmethod
    def update_turno(turno_id: int, n_turno: str, capacidade: int, tipo: str) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_update_turno(%s, %s, %s, %s)", [turno_id, n_turno, capacidade, tipo])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao atualizar turno {turno_id}: {e}")
            return False

    @staticmethod
    def delete_turno(turno_id: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_turno(%s)", [turno_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao deletar turno {turno_id}: {e}")
            return False

    @staticmethod
    def get_horario_pdf_by_id(pdf_id: int) -> Optional[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_horario_pdf_by_id(%s)", [pdf_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter horario_pdf {pdf_id}: {e}")
            return None

    @staticmethod
    def create_horario_pdf(nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> Optional[int]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_create_horario_pdf(%s, %s, %s, %s)",
                    [nome, ficheiro, id_anocurricular, id_curso],
                )
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] is not None else None
        except Exception as e:
            logger.error(f"Erro ao criar horario_pdf: {e}")
            return None

    @staticmethod
    def update_horario_pdf(pdf_id: int, nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_update_horario_pdf(%s, %s, %s, %s, %s)",
                    [pdf_id, nome, ficheiro, id_anocurricular, id_curso],
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao atualizar horario_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def delete_horario_pdf(pdf_id: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_horario_pdf(%s)", [pdf_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao deletar horario_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def list_horario_pdfs() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_list_horario_pdfs()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar horario_pdfs: {e}")
            return []

    @staticmethod
    def get_latest_horario_pdf() -> Optional[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_latest_horario_pdf()")
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter latest horario_pdf: {e}")
            return None

    @staticmethod
    def get_avaliacao_pdf_by_id(pdf_id: int) -> Optional[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_avaliacao_pdf_by_id(%s)", [pdf_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter avaliacao_pdf {pdf_id}: {e}")
            return None

    @staticmethod
    def create_avaliacao_pdf(nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> Optional[int]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_create_avaliacao_pdf(%s, %s, %s, %s)",
                    [nome, ficheiro, id_anocurricular, id_curso],
                )
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] is not None else None
        except Exception as e:
            logger.error(f"Erro ao criar avaliacao_pdf: {e}")
            return None

    @staticmethod
    def update_avaliacao_pdf(pdf_id: int, nome: str, ficheiro: str, id_anocurricular: int, id_curso: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_update_avaliacao_pdf(%s, %s, %s, %s, %s)",
                    [pdf_id, nome, ficheiro, id_anocurricular, id_curso],
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao atualizar avaliacao_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def delete_avaliacao_pdf(pdf_id: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_avaliacao_pdf(%s)", [pdf_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao deletar avaliacao_pdf {pdf_id}: {e}")
            return False

    @staticmethod
    def list_avaliacao_pdfs() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_list_avaliacao_pdfs()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar avaliacao_pdfs: {e}")
            return []

    @staticmethod
    def get_uc_by_id(uc_id: int) -> Optional[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_uc_by_id(%s)", [uc_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter UC {uc_id}: {e}")
            return None

    @staticmethod
    def list_all_ucs() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_list_all_ucs()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs: {e}")
            return []

    @staticmethod
    def create_uc(nome: str, id_curso: int, id_anocurricular: int, id_semestre: int, ects: float) -> Optional[int]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_create_uc(%s, %s, %s, %s, %s)",
                    [nome, id_curso, id_anocurricular, id_semestre, ects],
                )
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] is not None else None
        except Exception as e:
            logger.error(f"Erro ao criar UC: {e}")
            return None

    @staticmethod
    def update_uc(uc_id: int, nome: str, id_curso: int, id_anocurricular: int, id_semestre: int, ects: float) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_update_uc(%s, %s, %s, %s, %s, %s)",
                    [uc_id, nome, id_curso, id_anocurricular, id_semestre, ects],
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao atualizar UC {uc_id}: {e}")
            return False

    @staticmethod
    def delete_uc(uc_id: int) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_uc(%s)", [uc_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao deletar UC {uc_id}: {e}")
            return False

    @staticmethod
    def get_turnos_uc_by_uc_id(uc_id: int) -> List[Dict[str, Any]]:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_turnos_uc_by_uc_id(%s)", [uc_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar turnos_uc da UC {uc_id}: {e}")
            return []

    @staticmethod
    def delete_turnos_uc_by_uc_id(uc_id: int) -> int:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT fn_delete_turnos_uc_by_uc_id(%s)", [uc_id])
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] is not None else 0
        except Exception as e:
            logger.error(f"Erro ao deletar turnos_uc da UC {uc_id}: {e}")
            return 0

    @staticmethod
    def create_turno_uc(id_turno: int, id_uc: int, hora_inicio: str, hora_fim: str) -> bool:
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute(
                    "SELECT fn_create_turno_uc(%s, %s, %s, %s)",
                    [id_turno, id_uc, hora_inicio, hora_fim],
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao criar turno_uc: {e}")
            return False

    @staticmethod
    def get_semestres() -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_semestres()")
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar semestres: {e}")
            return []

# ============================= CORREÇÃO
class PostgreSQLDAPE:
    
    # =============================
    # PROPOSTAS
    # =============================
    @staticmethod
    def listar_propostas(filtro: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        filtro = filtro or {}
        curso_id = filtro.get("curso_id")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM dape_listar_propostas(%s)", [curso_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro a listar propostas DAPE: {e}")
            return []

    @staticmethod
    def obter_proposta_por_id(id_proposta: int) -> Optional[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM dape_obter_proposta(%s)", [id_proposta])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
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
        Chama function dape_criar_proposta.
        Retorna id_proposta ou None.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT dape_criar_proposta(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [aluno_id, titulo, entidade, descricao, requisitos, modelo,
                     orientador_empresa, telefone, email, logo]
                )
                row = cursor.fetchone()
                return int(row[0]) if row and row[0] else None
        except Exception as e:
            logger.error(f"Erro a criar proposta DAPE: {e}")
            return None

    @staticmethod
    def atualizar_proposta(aluno_id: int, titulo_atual: str, updates: Dict[str, Any]) -> bool:
        """Atualiza proposta do aluno via procedure dape_atualizar_proposta."""
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
        except Exception as e:
            logger.error(f"Erro a atualizar proposta DAPE: {e}")
            return False

    @staticmethod
    def eliminar_proposta(aluno_id: int, titulo: str) -> bool:
        """Elimina proposta do aluno via procedure dape_eliminar_proposta."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL dape_eliminar_proposta(%s,%s)", [aluno_id, titulo])
                return True
        except Exception as e:
            logger.error(f"Erro a eliminar proposta DAPE: {e}")
            return False

    # =============================
    # ADMIN OPS POR ID
    # =============================
    @staticmethod
    def admin_atualizar_proposta(id_proposta: int, updates: Dict[str, Any]) -> bool:
        """Atualiza proposta por ID (admin) via procedure dape_admin_atualizar_proposta."""
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
        except Exception as e:
            logger.error(f"Erro admin atualizar proposta DAPE: {e}")
            return False

    @staticmethod
    def admin_eliminar_proposta(id_proposta: int) -> bool:
        """Elimina proposta por ID (admin) via procedure dape_admin_eliminar_proposta."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL dape_admin_eliminar_proposta(%s)", [id_proposta])
                return True
        except Exception as e:
            logger.error(f"Erro admin eliminar proposta DAPE: {e}")
            return False

    # =============================
    # FAVORITOS
    # =============================
    @staticmethod
    def listar_favoritos(aluno_id: int) -> List[Dict[str, Any]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM dape_listar_favoritos(%s)", [aluno_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro a listar favoritos DAPE: {e}")
            return []

    @staticmethod
    def verificar_favorito(aluno_id: int, id_proposta: int) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dape_verificar_favorito(%s, %s)", [aluno_id, id_proposta])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro a verificar favorito DAPE: {e}")
            return False

    @staticmethod
    def toggle_favorito(aluno_id: int, id_proposta: int) -> Dict[str, Any]:
        """Adiciona/remove favorito via função dape_toggle_favorito. Retorna {added: bool}."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dape_toggle_favorito(%s,%s)", [aluno_id, id_proposta])
                row = cursor.fetchone()
                return {"added": bool(row[0])} if row is not None else {"added": False}
        except Exception as e:
            logger.error(f"Erro a toggle favorito DAPE: {e}")
            return {"added": False}


class PostgreSQLAuth:
    """Autenticação via SQL para admin, aluno e docente."""

    @staticmethod
    def fetch_admin(username_or_email: str) -> Optional[Dict[str, Any]]:
        """Obtém admin por username ou email via fn_fetch_admin."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_fetch_admin(%s)", [username_or_email])
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
        """Busca aluno por email via fn_fetch_aluno_por_email."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_fetch_aluno_por_email(%s)", [email])
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
        """Busca docente por email via fn_fetch_docente_por_email."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_fetch_docente_por_email(%s)", [email])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter docente: {e}")
            return None


class PostgreSQLPDF:
    """Operações com PDFs via funções SQL."""

    @staticmethod
    def delete_pdf(pdf_id: int, pdf_type: str) -> bool:
        """Apaga um PDF (horario ou avaliacao) por ID via fn_delete_pdf_horario/fn_delete_pdf_avaliacao."""
        try:
            with connections["admin"].cursor() as cursor:
                if pdf_type == 'horario':
                    cursor.execute("SELECT fn_delete_pdf_horario(%s)", [pdf_id])
                else:
                    cursor.execute("SELECT fn_delete_pdf_avaliacao(%s)", [pdf_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao apagar PDF: {e}")
            return False

    @staticmethod
    def get_pdf(pdf_id: int, pdf_type: str) -> Optional[Dict[str, Any]]:
        """Obtém um PDF específico via fn_get_pdf_horario/fn_get_pdf_avaliacao."""
        try:
            with connection.cursor() as cursor:
                if pdf_type == 'horario':
                    cursor.execute("SELECT * FROM fn_get_pdf_horario(%s)", [pdf_id])
                else:
                    cursor.execute("SELECT * FROM fn_get_pdf_avaliacao(%s)", [pdf_id])
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"Erro ao obter PDF: {e}")
            return None


class PostgreSQLLogs:
    """Operações com logs de eventos via funções SQL."""

    @staticmethod
    def list_logs(operacao_filter: Optional[str] = None, entidade_filter: Optional[str] = None, limite: int = 100) -> List[Dict[str, Any]]:
        """Lista logs com filtros opcionais via fn_list_logs."""
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT * FROM fn_list_logs(%s, %s, %s)", [operacao_filter, entidade_filter, limite])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar logs: {e}")
            return []

    @staticmethod
    def get_distinct_operacoes() -> List[str]:
        """Obtém lista de operações distintas via fn_get_distinct_operacoes."""
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT operacao FROM fn_get_distinct_operacoes()")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter operações: {e}")
            return []

    @staticmethod
    def get_distinct_entidades() -> List[str]:
        """Obtém lista de entidades distintas via fn_get_distinct_entidades."""
        try:
            with connections["admin"].cursor() as cursor:
                cursor.execute("SELECT entidade FROM fn_get_distinct_entidades()")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter entidades: {e}")
            return []


class PostgreSQLTurnos:
    """Operações de inscrição em turnos via SQL e procedures/functions existentes."""

    @staticmethod
    def get_aluno(n_mecanografico: int) -> Optional[Dict[str, Any]]:
        """Obtém aluno por número mecanográfico via fn_get_aluno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_aluno(%s)", [n_mecanografico])
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
        """Obtém turno por ID via fn_get_turno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_turno(%s)", [turno_id])
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
        """Obtém UC por ID via fn_get_uc."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_get_uc(%s)", [uc_id])
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
        """Verifica se turno pertence a UC via fn_turno_pertence_uc."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_turno_pertence_uc(%s, %s)", [turno_id, uc_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao validar turno/UC: {e}")
            return False

    @staticmethod
    def inscrito_na_uc(n_mecanografico: int, uc_id: int) -> bool:
        """Verifica se aluno está inscrito em UC via fn_inscrito_na_uc."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_inscrito_na_uc(%s, %s)", [n_mecanografico, uc_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao verificar inscrito_uc: {e}")
            return False

    @staticmethod
    def count_inscritos(turno_id: int, uc_id: int) -> int:
        """Conta inscritos em turno/UC via fn_count_inscritos."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_count_inscritos(%s, %s)", [turno_id, uc_id])
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except Exception as e:
            logger.error(f"Erro ao contar inscritos: {e}")
            return 0

    @staticmethod
    def create_inscricao_turno(n_mecanografico: int, turno_id: int, uc_id: int) -> bool:
        """Cria inscrição em turno via fn_create_inscricao_turno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_create_inscricao_turno(%s, %s, %s)", [n_mecanografico, turno_id, uc_id])
                row = cursor.fetchone()
                return bool(row[0]) if row else False
        except Exception as e:
            logger.error(f"Erro ao criar inscricao_turno: {e}")
            return False

    @staticmethod
    def delete_inscricao_turno(n_mecanografico: int, turno_id: int, uc_id: Optional[int] = None) -> int:
        """Apaga inscrição no turno via fn_delete_inscricao_turno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_delete_inscricao_turno(%s, %s, %s)", [n_mecanografico, turno_id, uc_id])
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except Exception as e:
            logger.error(f"Erro ao apagar inscricao_turno: {e}")
            return 0

    @staticmethod
    def turno_uc_por_uc(uc_id: int) -> List[Dict[str, Any]]:
        """Lista turnos de uma UC via fn_turno_uc_por_uc."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_turno_uc_por_uc(%s)", [uc_id])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao buscar turnos da UC {uc_id}: {e}")
            return []

    @staticmethod
    def ucs_inscritas_por_aluno(n_mecanografico: int) -> List[Dict[str, Any]]:
        """Lista UCs inscritas por aluno via fn_ucs_inscritas_por_aluno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_ucs_inscritas_por_aluno(%s)", [n_mecanografico])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar UCs inscritas do aluno {n_mecanografico}: {e}")
            return []

    @staticmethod
    def inscricoes_turno_por_aluno(n_mecanografico: int) -> List[Dict[str, Any]]:
        """Lista inscrições em turnos do aluno via fn_inscricoes_turno_por_aluno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_inscricoes_turno_por_aluno(%s)", [n_mecanografico])
                cols = [col[0] for col in cursor.description]
                return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar inscricoes turno: {e}")
            return []

    @staticmethod
    def turno_uc_por_turno(turno_id: int) -> List[Dict[str, Any]]:
        """Obtém turno_uc por turno via fn_turno_uc_por_turno."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM fn_turno_uc_por_turno(%s)", [turno_id])
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