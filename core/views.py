from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse, FileResponse
import json
from core.integracoes_postgresql import PostgreSQLAuth, PostgreSQLTurnos, PostgreSQLConsultas, PostgreSQLProcedures, PostgreSQLDAPE, PostgreSQLPDF, PostgreSQLLogs
from bd2_projeto.services.mongo_service import (
    adicionar_log, listar_eventos_mongo, listar_logs, registar_auditoria_inscricao,
    validar_inscricao_disponivel, registar_consulta_aluno, registar_erro, registar_auditoria_user
)
from bd2_projeto.services.gridfs_service import (upload_pdf_horario, upload_pdf_avaliacao, download_pdf, eliminar_pdf)
from core.utils import registar_log, admin_required, aluno_required, user_required
import logging
import time

logger = logging.getLogger(__name__)

def _listar_pdfs_por_ano(model_table, course_id):
    """Obtém PDFs mais recentes por ano curricular via SQL."""
    pdfs_raw = PostgreSQLConsultas.pdfs_por_ano_curso(model_table, course_id)
    anos_dict = {}
    
    for pdf in pdfs_raw:
        ano_id = pdf.get('id_anocurricular')
        if ano_id not in anos_dict:
            anos_dict[ano_id] = {
                'id_anocurricular': ano_id,
                'ano_curricular': pdf.get('ano_curricular'),
                'pdf': pdf
            }
        # Mantém o primeiro (mais recente) para cada ano
    
    return sorted(anos_dict.values(), key=lambda x: x['id_anocurricular'])

#view pagina inicial DI
def index(request):
    return render(request, "di/index_di.html", {"area": "di"})

#view para login
def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username") # le o valor introduzido no username, pode ser username ou email
        password = request.POST.get("password") # le o valor introduzido na password

        # limpa qualquer sessão anterior
        request.session.flush()

        # 1) Admin (auth_user) via SQL
        admin_row = PostgreSQLAuth.fetch_admin(username_or_email)
        if admin_row and admin_row.get("is_staff") and admin_row.get("is_active"):
            if PostgreSQLAuth.validar_password(admin_row.get("password"), password):
                request.session["user_tipo"] = "admin"
                request.session["user_id"] = admin_row.get("id")
                request.session["user_nome"] = admin_row.get("username")
                request.session["user_email"] = admin_row.get("email")
                return redirect("home:admin_dashboard")

        # 2) Aluno (tabela aluno)
        aluno_row = PostgreSQLAuth.fetch_aluno_por_email(username_or_email)
        if aluno_row and aluno_row.get("password") == password:
            request.session["user_tipo"] = "aluno"
            request.session["user_id"] = aluno_row.get("n_mecanografico")
            request.session["user_nome"] = aluno_row.get("nome")
            request.session["user_email"] = aluno_row.get("email")
            return redirect("home:index")

        # 3) Docente (tabela docente)
        docente_row = PostgreSQLAuth.fetch_docente_por_email(username_or_email)
        if docente_row and docente_row.get("password") == password:
            request.session["user_tipo"] = "docente"
            request.session["user_id"] = docente_row.get("id_docente")
            request.session["user_nome"] = docente_row.get("nome")
            request.session["user_email"] = docente_row.get("email")
            return redirect("home:index")
        
        #caso nao exista ninguem com os dados fornecidos, da msg de erro
        messages.error(request, "Utilizador ou palavra-passe incorretos.")
        return redirect("home:login")

    return render(request, "auth/login.html")

#view para logout
def do_logout(request):
    request.session.flush()  # limpa toda a sessão
    return redirect("home:login")  # redireciona para a página de login novamente

#view para ingresso em EI
def ingresso(request):
    return render(request, "ei/ingresso.html", { "area": "ei" })

#view para plano curricular de EI
def plano_curricular(request):
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "plano_curricular", {"curso": "EI"})
    
    unidades = PostgreSQLConsultas.ucs_por_curso(1)
    
    plano = {}
    for uc in unidades:
        ano = uc.get('id_anocurricular')
        semestre = uc.get('semestre')
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "ei/plano_curricular.html", {"plano": plano, "area": "ei"})

#view para horarios de EI
def horarios(request):
    #se o utilizador for aluno, regista a consulta na coleçao do MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "horarios", {"curso": "EI"})

    horarios_por_ano = _listar_pdfs_por_ano('core_horariopdf', course_id=1)
    
    # Verificar se o aluno pertence ao curso de EI (id_curso = 1)
    pode_inscrever = False
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        aluno_row = PostgreSQLTurnos.get_aluno(request.session["user_id"])
        if aluno_row and aluno_row.get("id_curso") == 1:
            pode_inscrever = True

    return render(request, "ei/horarios.html", {
        "horarios_por_ano": horarios_por_ano,
        "area": "ei",
        "pode_inscrever": pode_inscrever
    })

#view para avaliacoes de EI
def avaliacoes(request):
    #se o utilizador for aluno, regista a consulta na coleçao do MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "avaliacoes", {"curso": "EI"})

    avaliacoes_por_ano = _listar_pdfs_por_ano('core_avaliacaopdf', course_id=1)

    return render(request, "ei/avaliacoes.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "ei"})

#view para contactos de EI
def contactos(request):
    docentes = PostgreSQLConsultas.docentes()
    curso = {'id_curso': 1, 'nome': 'Engenharia Informática'}
    return render(request, "ei/contactos.html", {"curso": curso, "docentes": docentes, "area": "ei"})

#view para inscricao em turnos de EI (pagina apenas)
def inscricao_turno(request):
    #verifica se o user é aluno, caso nao seja redireciona para a login page
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    n_meca = request.session["user_id"]
    aluno_row = PostgreSQLTurnos.get_aluno(n_meca)
    if not aluno_row:
        messages.error(request, "Aluno não encontrado.")
        return redirect("home:login")

    if aluno_row.get("id_curso") != 1:
        messages.error(request, "Esta página é apenas para alunos de Engenharia Informática.")
        if aluno_row.get("id_curso") == 2:
            return redirect("home:inscricao_turno_tdm")
        return redirect("home:index")

    turnos_inscritos_rows = PostgreSQLTurnos.inscricoes_turno_por_aluno(n_meca)
    turnos_inscritos = {row.get("id_turno") for row in turnos_inscritos_rows}

    inscricoes_uc = PostgreSQLTurnos.ucs_inscritas_por_aluno(n_meca)

    lista_uc = []
    turnos_no_horario = []

    def _mapear_dia_semana(hora_inicio):
        try:
            h_int = hora_inicio.hour
            if 8 <= h_int < 10:
                return "Segunda"
            if 10 <= h_int < 12:
                return "Terça"
            if 12 <= h_int < 14:
                return "Quarta"
            if 14 <= h_int < 16:
                return "Quinta"
            return "Sexta"
        except Exception:
            return "?"

    for uc_row in inscricoes_uc:
        uc_id = uc_row.get("id_unidadecurricular")
        turnos_uc = PostgreSQLTurnos.turno_uc_por_uc(uc_id)

        turnos = []
        for tu in turnos_uc:
            turno_id = tu.get("id_turno")
            ocupados = PostgreSQLTurnos.count_inscritos(turno_id, uc_id)
            capacidade = tu.get("capacidade") or 0
            vagas = capacidade - ocupados
            if vagas < 0:
                vagas = 0

            hora_inicio = tu.get("hora_inicio")
            hora_fim = tu.get("hora_fim")
            hora_inicio_str = hora_inicio.strftime("%H:%M") if hora_inicio else "?"
            hora_fim_str = hora_fim.strftime("%H:%M") if hora_fim else "?"
            dia_semana = _mapear_dia_semana(hora_inicio) if hora_inicio else "?"

            ja_inscrito = turno_id in turnos_inscritos

            turno_info = {
                "id": turno_id,
                "nome": f"T{tu.get('n_turno')}",
                "tipo": tu.get("tipo"),
                "capacidade": capacidade,
                "vagas": vagas,
                "horario": f"{dia_semana} {hora_inicio_str}-{hora_fim_str}",
                "ja_inscrito": ja_inscrito,
                "dia": dia_semana,
                "hora_inicio": hora_inicio_str,
                "hora_fim": hora_fim_str,
            }

            turnos.append(turno_info)

            if ja_inscrito:
                turnos_no_horario.append({
                    "uc_nome": uc_row.get("nome"),
                    "turno_nome": f"T{tu.get('n_turno')}",
                    "tipo": tu.get("tipo"),
                    "dia": dia_semana,
                    "hora_inicio": hora_inicio_str,
                    "hora_fim": hora_fim_str,
                })

        lista_uc.append({
            "id": uc_id,
            "nome": uc_row.get("nome"),
            "turnos": turnos,
        })

    #lista de periodos de 30min para construir o horario personalizado
    horas = [
        "08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30",
        "12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30",
        "16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30",
        "20:00","20:30","21:00","21:30","22:00","22:30","23:00","23:30"
    ]

    #lista de dias da semana para construir o horario personalziado
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    return render(request, "ei/inscricao_turno.html", {"unidades": lista_uc, "horas": horas, "dias": dias, "turnos_horario": turnos_no_horario, "area": "ei"})

#view para informacoes de EI
def informacoes(request):
    return render(request, "ei/informacoes.html", { "area": "ei" })

#view para o perfil do user autentiasdo
@user_required
def perfil(request):
    user_tipo = request.session.get("user_tipo")
    user_id = request.session.get("user_id")
    
    #dicionario que é enviado para o template
    context = {}

    if user_tipo == "aluno":
        aluno_row = PostgreSQLTurnos.get_aluno(user_id)
        if not aluno_row:
            messages.error(request, "Aluno não encontrado.")
            return redirect("home:login")

        context["user_obj"] = aluno_row
        context["tipo"] = "Aluno"

        inscricoes = PostgreSQLTurnos.inscricoes_turno_por_aluno(user_id)

        turnos_info = []
        for insc in inscricoes:
            hora_inicio = insc.get("hora_inicio")
            hora_fim = insc.get("hora_fim")
            hora_inicio_str = hora_inicio.strftime("%H:%M") if hora_inicio else "?"
            hora_fim_str = hora_fim.strftime("%H:%M") if hora_fim else "?"

            try:
                h_int = hora_inicio.hour if hora_inicio else None
                if h_int is None:
                    dia_semana = "?"
                elif 8 <= h_int < 10:
                    dia_semana = "Segunda"
                elif 10 <= h_int < 12:
                    dia_semana = "Terça"
                elif 12 <= h_int < 14:
                    dia_semana = "Quarta"
                elif 14 <= h_int < 16:
                    dia_semana = "Quinta"
                else:
                    dia_semana = "Sexta"
            except Exception:
                dia_semana = "?"

            turnos_info.append({
                "uc": insc.get("uc_nome"),
                "turno": f"T{insc.get('turno_numero')}",
                "tipo": insc.get("turno_tipo"),
                "horario": f"{dia_semana}, {hora_inicio_str} - {hora_fim_str}"
            })

        context["turnos"] = turnos_info

    elif user_tipo == "docente":
        docente = get_object_or_404(Docente, id_docente=user_id)
        context["user_obj"] = docente
        context["tipo"] = "Docente"

    return render(request, "profile/perfil.html", context)

#view para inscrever o aluno nos turnos (açao)
@aluno_required
def inscrever_turno(request, turno_id, uc_id):
    inicio_tempo = time.time()
    resultado = None
    motivo = None

    try:
        aluno_row = PostgreSQLTurnos.get_aluno(request.session["user_id"])
        if not aluno_row:
            messages.error(request, "Aluno não encontrado.")
            return redirect("home:login")

        if aluno_row.get("id_curso") != 1:
            messages.error(request, "Esta funcionalidade é apenas para alunos de Engenharia Informática.")
            return redirect("home:index")

        turno_row = PostgreSQLTurnos.get_turno(turno_id)
        uc_row = PostgreSQLTurnos.get_uc(uc_id)
        if not turno_row or not uc_row:
            messages.error(request, "Turno ou UC inválidos.")
            return redirect("home:inscricao_turno")

        if not PostgreSQLTurnos.turno_pertence_uc(turno_id, uc_id):
            resultado = "nao_autorizado"
            motivo = "Este turno não pertence a esta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        if not PostgreSQLTurnos.inscrito_na_uc(aluno_row["n_mecanografico"], uc_id):
            resultado = "nao_autorizado"
            motivo = "Não estás inscrito nesta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        pode_inscrever, msg_validacao = validar_inscricao_disponivel(aluno_row["n_mecanografico"], turno_id)
        if not pode_inscrever:
            resultado = "uc_duplicada"
            motivo = msg_validacao
            messages.warning(request, "Já estás inscrito neste turno.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        ocupados = PostgreSQLTurnos.count_inscritos(turno_id, uc_id)
        if ocupados >= (turno_row.get("capacidade") or 0):
            resultado = "turno_cheio"
            motivo = f"Turno cheio (capacidade: {turno_row.get('capacidade')}, ocupado: {ocupados})"
            messages.error(request, "Este turno já está cheio.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        criado = PostgreSQLTurnos.create_inscricao_turno(aluno_row["n_mecanografico"], turno_id, uc_id)
        tempo_ms = int((time.time() - inicio_tempo) * 1000)

        if not criado:
            resultado = "erro_sistema"
            motivo = "Falha ao gravar inscrição"
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), resultado, motivo, tempo_ms)
            messages.error(request, "Erro ao processar inscrição. Tente novamente.")
            return redirect("home:inscricao_turno")

        # auditoria em PostgreSQL (sem ORM)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auditoria_inscricao (n_mecanografico, id_turno, id_unidadecurricular, resultado, motivo_rejeicao, tempo_processamento_ms)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [aluno_row["n_mecanografico"], turno_id, uc_id, 'sucesso', None, tempo_ms]
                )
        except Exception as e:
            logger.error(f"Erro ao registar auditoria_inscricao: {e}")

        registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, uc_row.get("nome", ""), 'sucesso', None, tempo_ms)
        adicionar_log("inscricao_turno_sucesso", {"aluno": aluno_row.get("nome"), "uc": uc_row.get("nome"), "turno": turno_id, "tempo_ms": tempo_ms}, request)
        messages.success(request, "Inscrição no turno efetuada com sucesso!")
        return redirect("home:inscricao_turno")

    except Exception as e:
        resultado = "erro_sistema"
        motivo = str(e)
        tempo_ms = int((time.time() - inicio_tempo) * 1000)

        registar_erro("inscrever_turno", str(e), {"turno_id": turno_id, "uc_id": uc_id})
        registar_auditoria_inscricao(request.session.get("user_id"), turno_id, uc_id, "desconhecido",  resultado, motivo, tempo_ms)
        messages.error(request, "Erro ao processar inscrição. Tente novamente.")
        return redirect("home:inscricao_turno")

#view para remover a inscriçao do turno
@aluno_required
def desinscrever_turno(request, turno_id, uc_id):
    try:
        aluno_row = PostgreSQLTurnos.get_aluno(request.session["user_id"])
        if not aluno_row:
            return JsonResponse({"erro": "Aluno não encontrado"}, status=404)

        uc_row = PostgreSQLTurnos.get_uc(uc_id)
        turno_row = PostgreSQLTurnos.get_turno(turno_id)

        removidas = PostgreSQLTurnos.delete_inscricao_turno(aluno_row["n_mecanografico"], turno_id, uc_id)
        if removidas == 0:
            removidas = PostgreSQLTurnos.delete_inscricao_turno(aluno_row["n_mecanografico"], turno_id, None)

        if removidas > 0:
            registar_auditoria_inscricao(aluno_row["n_mecanografico"], turno_id, uc_id, (uc_row or {}).get("nome", ""), 'desinscrever', None, 0)
            adicionar_log("desinscrever_turno", {"aluno": aluno_row["n_mecanografico"], "turno": turno_id, "uc": uc_id, "registos_removidos": removidas, }, request)
            if turno_row and uc_row:
                messages.success(request, f"Desinscrição em {uc_row.get('nome')} — {turno_row.get('tipo')} efetuada!")
            else:
                messages.success(request, "Desinscrição efetuada!")
        else:
            messages.warning(request, "Inscrição não encontrada.")

        return redirect("home:inscricao_turno")

    except Exception as e:
        registar_erro("desinscrever_turno", str(e), {"turno_id": turno_id, "uc_id": uc_id})
        messages.error(request, "Erro ao remover inscrição.")
        return redirect("home:inscricao_turno")

#view para verificar se existe conflito de horario
def api_verificar_conflitos(request, turno_id):
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        return JsonResponse({"erro": "Não autorizado"}, status=403)

    try:
        aluno_row = PostgreSQLTurnos.get_aluno(request.session["user_id"])
        if not aluno_row:
            return JsonResponse({"erro": "Aluno não encontrado"}, status=404)

        turnos_uc_novo = PostgreSQLTurnos.turno_uc_por_turno(turno_id)
        if not turnos_uc_novo:
            return JsonResponse({"conflitos": []})

        inscricoes = PostgreSQLTurnos.inscricoes_turno_por_aluno(aluno_row["n_mecanografico"])

        conflitos = []
        for tu_novo in turnos_uc_novo:
            hora_inicio_novo = tu_novo.get("hora_inicio")
            hora_fim_novo = tu_novo.get("hora_fim")
            for insc in inscricoes:
                hora_inicio_existente = insc.get("hora_inicio")
                hora_fim_existente = insc.get("hora_fim")
                if not hora_inicio_novo or not hora_fim_novo or not hora_inicio_existente or not hora_fim_existente:
                    continue
                if (hora_inicio_novo < hora_fim_existente and hora_fim_novo > hora_inicio_existente):
                    conflitos.append({
                        "uc": insc.get("uc_nome") or "UC",
                        "turno": insc.get("turno_tipo") or "",
                        "horario": f"{hora_inicio_existente.strftime('%H:%M')} - {hora_fim_existente.strftime('%H:%M')}"
                    })

        conflitos_unicos = []
        chaves_vistas = set()
        for c in conflitos:
            chave = (c['uc'], c['turno'], c['horario'])
            if chave not in chaves_vistas:
                chaves_vistas.add(chave)
                conflitos_unicos.append(c)

        return JsonResponse({"conflitos": conflitos_unicos})

    except Exception as e:
        import traceback
        registar_erro("api_verificar_conflitos", str(e), {"turno_id": turno_id, "traceback": traceback.format_exc()})
        return JsonResponse({"erro": str(e), "debug": traceback.format_exc()}, status=500)

#view para obter as ucs por semestre
def cadeiras_semestre(request):
    data = PostgreSQLConsultas.cadeiras_semestre()
    return JsonResponse(data, safe=False)

#view para obter os launos alfabeticamente
def alunos_por_ordem_alfabetica(request):
    data = PostgreSQLConsultas.alunos_por_ordem_alfabetica()
    return JsonResponse(data, safe=False)

#view para obter os turnos
def turnos_list(request):
    data = PostgreSQLConsultas.turnos_list()
    return JsonResponse(data, safe=False)

#view para obter os cursos
def cursos_list(request):
    data = PostgreSQLConsultas.cursos_list()
    return JsonResponse(data, safe=False)

#view para o dashboard do admin
@admin_required
def admin_dashboard(request):
    stats = PostgreSQLConsultas.dashboard_totais()
    alunos_por_uc = PostgreSQLConsultas.alunos_por_uc_top10()

    chart_alunos_labels = json.dumps([item.get('uc_nome') for item in alunos_por_uc])
    chart_alunos_values = json.dumps([item.get('total') for item in alunos_por_uc])

    vagas_disponiveis = (stats.get("vagas_total", 0) or 0) - (stats.get("vagas_ocupadas", 0) or 0)

    return render(request, "admin/dashboard.html", {
        "total_users": stats.get("total_users", 0),
        "total_turnos": stats.get("total_turnos", 0),
        "total_ucs": stats.get("total_ucs", 0),
        "total_cursos": stats.get("total_cursos", 0),
        "total_horarios": stats.get("total_horarios", 0),
        "total_avaliacoes": stats.get("total_avaliacoes", 0),
        "chart_alunos_labels": chart_alunos_labels,
        "chart_alunos_values": chart_alunos_values,
        "vagas_ocupadas": stats.get("vagas_ocupadas", 0),
        "vagas_disponiveis": vagas_disponiveis,
    })


#view para a página de exportação de dados
@admin_required
def admin_export_data(request):
    return render(request, "admin/export_data.html")


#view para listar os utilizadores admin, alunos e docentes
def admin_users_list(request):
    users_sorted = PostgreSQLConsultas.users_combinado()
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    
    return render(request, "admin/users_list.html", {"users": users_sorted, "cursos": cursos, "anos": anos})

#view para criar um user e listar os restantes
def admin_users_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_tipo = request.POST.get("tipo", "admin")

        if not username or not password:
            messages.error(request, "Username e password são obrigatórios.")
            users_sorted = PostgreSQLConsultas.users_combinado()
            cursos = PostgreSQLConsultas.cursos_list()
            anos = PostgreSQLConsultas.anos_curriculares()
            return render(request, "admin/users_form.html", {"users": users_sorted, "cursos": cursos, "anos": anos})

        try:
            if user_tipo == "aluno":
                n_mecanografico = request.POST.get("n_mecanografico")
                id_curso = request.POST.get("id_curso")
                id_anocurricular = request.POST.get("id_anocurricular")
                
                if not n_mecanografico or not id_curso or not id_anocurricular:
                    messages.error(request, "Nº Mecanografico, Curso e Ano Curricular são obrigatórios para alunos.")
                    return redirect("home:admin_users_create")
                
                PostgreSQLProcedures.criar_aluno(int(n_mecanografico), int(id_curso), int(id_anocurricular), username, email, password)
                registar_log(request, operacao="CREATE", entidade="aluno", chave=str(n_mecanografico), detalhes=f"Novo aluno criado: {username} ({email})")
                messages.success(request, f"Aluno {username} criado com sucesso!")
                
            elif user_tipo == "docente":
                PostgreSQLProcedures.criar_docente(username, email, "professor")
                registar_log(request, operacao="CREATE", entidade="docente", chave=username, detalhes=f"Novo docente criado: {username} ({email})")
                messages.success(request, f"Docente {username} criado com sucesso!")
                
            else:  # admin - usar SQL direto
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO auth_user (username, email, password, is_active, is_staff) VALUES (%s, %s, %s, true, true)",
                            [username, PostgreSQLAuth.validar_password("", password) or password, email]
                        )
                    registar_log(request, operacao="CREATE", entidade="user_admin", chave=username, detalhes=f"Novo admin criado: {username} ({email})")
                    messages.success(request, "Admin criado com sucesso!")
                except Exception as e:
                    messages.error(request, f"Erro ao criar admin: {str(e)}")
                    return redirect("home:admin_users_create")
            
            return redirect("home:admin_users_list")
            
        except Exception as e:
            messages.error(request, f"Erro ao criar utilizador: {str(e)}")
            return redirect("home:admin_users_create")

    users_sorted = PostgreSQLConsultas.users_combinado()
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    
    return render(request, "admin/users_form.html", {"users": users_sorted, "cursos": cursos, "anos": anos})

#view para editar os dados de um user
def admin_users_edit(request, id):
    # SQL: Encontra o user em admin, aluno ou docente
    user, user_type = PostgreSQLConsultas.get_user_by_id(id)
    
    if not user or not user_type:
        return redirect("home:admin_users_list")

    # POST: Atualiza o user
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        
        # Guarda dados antigos para logs
        old_username = user.get('username') if user_type == "Admin" else user.get('nome')
        old_data = {'username': old_username, 'email': user.get('email')}
        
        # SQL: Atualiza o user
        success = PostgreSQLConsultas.update_user(id, user_type, username, email)
        
        if success:
            # Registra log e auditoria
            registar_log(request, operacao="UPDATE", entidade=f"user_{user_type.lower()}", chave=str(id), detalhes=f"Campos alterados: username={username}, email={email}")
            registar_auditoria_user("UPDATE", id, user_type, {"username": username, "email": email, "alterado_de": old_data}, request)
            messages.success(request, "Utilizador atualizado com sucesso!")
        else:
            messages.error(request, "Erro ao atualizar utilizador.")
        
        return redirect("home:admin_users_list")

    # GET: Prepara dados do user para o form
    user_data = {
        'id': user.get('id') if user_type == "Admin" else (user.get('n_mecanografico') if user_type == "Aluno" else user.get('id_docente')),
        'username': user.get('username') if user_type == "Admin" else user.get('nome'),
        'email': user.get('email'),
        'tipo': user_type
    }
    
    # SQL: Lista combinada de users (admin + aluno + docente)
    users = PostgreSQLConsultas.users_combinado()
    users_sorted = sorted(users, key=lambda x: x.get('id', 0) if isinstance(x.get('id'), int) else int(x.get('id', 0)) if x.get('id') else 0)
    
    return render(request, "admin/users_form.html", {"user": user_data, "users": users_sorted})

#view para apagar um user
def admin_users_delete(request, id):
    # SQL: Encontra o user em admin, aluno ou docente
    user, user_type = PostgreSQLConsultas.get_user_by_id(id)
    
    if not user or not user_type:
        messages.error(request, "Utilizador não encontrado.")
        return redirect("home:admin_users_list")

    # Pega o username para o log
    username = user.get('username') if user_type == "Admin" else user.get('nome')
    email = user.get('email')
    
    # SQL: Deleta o user e suas referências
    if user_type == "Aluno":
        cascade_result = PostgreSQLConsultas.delete_aluno_cascade(id)
        messages.info(request, f"Removidas {cascade_result['matriculas']} matrículas, {cascade_result['inscricoes_turno']} inscrições em turnos e {cascade_result['inscrito_uc']} inscrições em UCs.")
    elif user_type == "Docente":
        cascade_result = PostgreSQLConsultas.delete_docente_cascade(id)
        messages.info(request, f"Removidas {cascade_result['leciona_uc']} associações com UCs.")
    elif user_type == "Admin":
        PostgreSQLConsultas.delete_admin_user(id)

    # Registra log e auditoria
    registar_log(request, operacao="DELETE", entidade=f"user_{user_type.lower()}", chave=str(id), detalhes=f"Utilizador apagado: {username} (Tipo: {user_type})")
    registar_auditoria_user("DELETE", id, user_type, {"username": username, "email": email, "tipo": user_type}, request)

    messages.success(request, f"{user_type} '{username}' apagado com sucesso!")
    return redirect("home:admin_users_list")

#view para listar todos os turnos no admin
def admin_turnos_list(request):
    # SQL: Lista turnos sem UC
    turnos = PostgreSQLConsultas.turnos_sem_uc()
    return render(request, "admin/turnos_list.html", {"turnos": turnos})

#view para criar um novo turno
def admin_turnos_create(request):
    if request.method == "POST":
        n_turno = request.POST.get("n_turno")
        capacidade = request.POST.get("capacidade")
        tipo = request.POST.get("tipo")

        # SQL: Cria o turno
        turno_id = PostgreSQLConsultas.create_turno(n_turno, int(capacidade), tipo)
        
        if turno_id:
            registar_log(request, operacao="CREATE", entidade="turno", chave=str(turno_id), detalhes=f"Turno criado: {tipo} (nº {n_turno})")
            messages.success(request, "Turno criado com sucesso!")
        else:
            messages.error(request, "Erro ao criar turno.")
        
        return redirect("home:admin_turnos_list")

    return render(request, "admin/turnos_form.html")

#view para editar turno
def admin_turnos_edit(request, id):
    # SQL: Obtém o turno
    turno = PostgreSQLConsultas.get_turno_by_id(id)
    
    if not turno:
        messages.error(request, "Turno não encontrado.")
        return redirect("home:admin_turnos_list")

    # POST: Atualiza o turno
    if request.method == "POST":
        n_turno = request.POST.get("n_turno")
        capacidade = request.POST.get("capacidade")
        tipo = request.POST.get("tipo")
        
        # SQL: Atualiza o turno
        success = PostgreSQLConsultas.update_turno(id, n_turno, int(capacidade), tipo)
        
        if success:
            registar_log(request, operacao="UPDATE", entidade="turno", chave=str(id), detalhes=f"Turno atualizado: {tipo} (nº {n_turno})")
            messages.success(request, "Turno atualizado!")
        else:
            messages.error(request, "Erro ao atualizar turno.")
        
        return redirect("home:admin_turnos_list")

    # GET: Mostra o form preenchido
    return render(request, "admin/turnos_form.html", {"turno": turno})

#view para eliminar turno
def admin_turnos_delete(request, id):
    # SQL: Obtém o turno antes de deletar
    turno = PostgreSQLConsultas.get_turno_by_id(id)
    
    if not turno:
        messages.error(request, "Turno não encontrado.")
        return redirect("home:admin_turnos_list")
    
    # SQL: Deleta o turno
    success = PostgreSQLConsultas.delete_turno(id)
    
    if success:
        registar_log(request, operacao="DELETE", entidade="turno", chave=str(id), detalhes=f"Turno apagado: {turno['tipo']} (nº {turno['n_turno']})")
        messages.success(request, "Turno apagado!")
    else:
        messages.error(request, "Erro ao apagar turno.")
    
    return redirect("home:admin_turnos_list")

#view para upload pdf com o horario
def admin_horarios_create(request):
    # SQL: Lista cursos e anos curriculares
    cursos = PostgreSQLConsultas.cursos_list()
    anos_curriculares = PostgreSQLConsultas.anos_curriculares()
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        ficheiro = request.FILES.get("ficheiro")
        curso_id = request.POST.get("id_curso")
        ano_id = request.POST.get("id_anocurricular")

        #verifica se o ficheiro e valido
        if not ficheiro:
            messages.error(request, "É necessário enviar um ficheiro PDF.")
            return redirect("home:admin_horarios_create")
        
        #verifica se o admin selecionou um curso e um ano curricular
        if not curso_id or not ano_id:
            messages.error(request, "É necessário selecionar o curso e o ano curricular.")
            return redirect("home:admin_horarios_create")

        try:
            # ==========================================
            # UPLOAD PARA MongoDB (GridFS)
            # ==========================================
            # Faz upload do PDF para o MongoDB usando GridFS
            # O ficheiro é dividido em chunks de 64KB e armazenado
            resultado_upload = upload_pdf_horario(
                ficheiro_file=ficheiro,
                nome=nome,
                id_curso=int(curso_id),
                id_anocurricular=int(ano_id)
            )
            
            # Obtém o file_id retornado pelo GridFS
            file_id_mongodb = resultado_upload["file_id"]
            
            # ==========================================
            # GUARDAR REFERÊNCIA NA BD (SQL)
            # ==========================================
            # Em vez de guardar o ficheiro no filesystem,
            # guardamos apenas o ID do GridFS como referência
            pdf_id = PostgreSQLConsultas.create_horario_pdf(
                nome=nome,
                ficheiro=f"mongodb_gridfs:{file_id_mongodb}",
                id_anocurricular=int(ano_id),
                id_curso=int(curso_id)
            )
            
            if pdf_id:
                # Regista a operação no log
                registar_log(request, operacao="CREATE", entidade="horario_pdf", chave=file_id_mongodb, detalhes=f"Horário PDF criado no MongoDB: {nome}")
                messages.success(request, "Horário carregado com sucesso no MongoDB!")
            else:
                messages.error(request, "Erro ao guardar referência do horário.")
            
            return redirect("home:admin_horarios_list")
        
        except Exception as e:
            # Se algo correr mal, mostra a mensagem de erro
            messages.error(request, f"Erro ao carregar horário: {str(e)}")
            return redirect("home:admin_horarios_create")

    return render(request, "admin/horarios_form.html", {'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para editar o pdf com o horario
def admin_horarios_edit(request, id):
    # SQL: Obtém o horário PDF
    horario = PostgreSQLConsultas.get_horario_pdf_by_id(id)
    
    if not horario:
        messages.error(request, "Horário não encontrado.")
        return redirect("home:admin_horarios_list")
    
    # SQL: Lista cursos e anos curriculares
    cursos = PostgreSQLConsultas.cursos_list()
    anos_curriculares = PostgreSQLConsultas.anos_curriculares()

    if request.method == "POST":
        nome = request.POST.get("nome")
        curso_id = request.POST.get("id_curso")
        ano_id = request.POST.get("id_anocurricular")
        
        # Se foi efetuado o upload de um PDF, este substitui o PDF atual
        ficheiro_ref = horario['ficheiro']  # Keep existing if no new upload
        if "ficheiro" in request.FILES:
            ficheiro = request.FILES["ficheiro"]
            try:
                resultado_upload = upload_pdf_horario(
                    ficheiro_file=ficheiro,
                    nome=nome,
                    id_curso=int(curso_id),
                    id_anocurricular=int(ano_id)
                )
                file_id_mongodb = resultado_upload["file_id"]
                ficheiro_ref = f"mongodb_gridfs:{file_id_mongodb}"
            except Exception as e:
                messages.error(request, f"Erro ao carregar novo horário: {str(e)}")
                return redirect("home:admin_horarios_edit", id=id)
        
        # SQL: Atualiza o horário PDF
        success = PostgreSQLConsultas.update_horario_pdf(
            id, nome, ficheiro_ref, int(ano_id), int(curso_id)
        )
        
        if success:
            messages.success(request, "Horário atualizado!")
        else:
            messages.error(request, "Erro ao atualizar horário.")
        
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html", {"horario": horario, 'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para eliminar o pdf do horario
def admin_horarios_delete(request, id):
    # SQL: Deleta o horário PDF
    success = PostgreSQLConsultas.delete_horario_pdf(id)
    
    if success:
        messages.success(request, "Horário apagado!")
    else:
        messages.error(request, "Erro ao apagar horário.")
    
    return redirect("home:admin_horarios_list")

#view para listar os horarios
def admin_horarios_list(request):
    # SQL: Lista todos os horários
    horarios = PostgreSQLConsultas.list_horario_pdfs()
    return render(request, "admin/horarios_list.html", {"horarios": horarios})

#view para mostrar na web o mais recente
def horarios_admin(request):
    # SQL: Obtém o horário mais recente
    pdf = PostgreSQLConsultas.get_latest_horario_pdf()
    return render(request, "home/horarios.html", {"pdf": pdf})

#view para listar os pdf das avaliacoes
@admin_required
def admin_avaliacoes_list(request):
    # SQL: Lista todos os PDFs de avaliação
    avaliacoes = PostgreSQLConsultas.list_avaliacao_pdfs()
    return render(request, "admin/avaliacoes_list.html", {"avaliacoes": avaliacoes})

#view para upload pdf para avaliacoes
@admin_required
def admin_avaliacoes_create(request):
    # SQL: Lista cursos e anos curriculares
    cursos = PostgreSQLConsultas.cursos_list()
    anos_curriculares = PostgreSQLConsultas.anos_curriculares()

    if request.method == "POST":
        nome = request.POST.get("nome")
        ficheiro = request.FILES.get("ficheiro")
        ano_id = request.POST.get("id_anocurricular")
        curso_id = request.POST.get("id_curso")

        #obriga a enviar um pdf
        if not ficheiro:
            messages.error(request, "É necessário enviar um ficheiro PDF.")
            return redirect("home:admin_avaliacoes_create")
        
        #obriga a selecionar um curso e um ano curricular
        if not curso_id or not ano_id:
            messages.error(request, "É necessário selecionar o curso e o ano curricular.")
            return redirect("home:admin_avaliacoes_create")

        try:
            # ==========================================
            # UPLOAD PARA MongoDB (GridFS)
            # ==========================================
            # Faz upload do PDF para o MongoDB usando GridFS
            # O ficheiro é dividido em chunks e armazenado
            resultado_upload = upload_pdf_avaliacao(
                ficheiro_file=ficheiro,
                nome=nome,
                id_curso=int(curso_id),
                id_anocurricular=int(ano_id)
            )
            
            # Obtém o file_id retornado pelo GridFS
            file_id_mongodb = resultado_upload["file_id"]
            
            # ==========================================
            # GUARDAR REFERÊNCIA NA BD (SQL)
            # ==========================================
            # Guardamos apenas o ID do GridFS como referência
            pdf_id = PostgreSQLConsultas.create_avaliacao_pdf(
                nome=nome,
                ficheiro=f"mongodb_gridfs:{file_id_mongodb}",
                id_anocurricular=int(ano_id),
                id_curso=int(curso_id)
            )

            if pdf_id:
                registar_log(request, operacao="CREATE", entidade="avaliacao_pdf", chave=file_id_mongodb, detalhes=f"Avaliação PDF criada no MongoDB: {nome}")
                messages.success(request, "Calendário de avaliações carregado com sucesso no MongoDB!")
            else:
                messages.error(request, "Erro ao guardar referência da avaliação.")
            
            return redirect("home:admin_avaliacoes_list")
        
        except Exception as e:
            messages.error(request, f"Erro ao carregar avaliação: {str(e)}")
            return redirect("home:admin_avaliacoes_create")

    return render(request, "admin/avaliacoes_form.html", {'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view editar um pdf de avaliacoes
@admin_required
def admin_avaliacoes_edit(request, id):
    # SQL: Obtém o PDF de avaliação
    avaliacao = PostgreSQLConsultas.get_avaliacao_pdf_by_id(id)
    
    if not avaliacao:
        messages.error(request, "Avaliação não encontrada.")
        return redirect("home:admin_avaliacoes_list")
    
    # SQL: Lista cursos e anos curriculares
    cursos = PostgreSQLConsultas.cursos_list()
    anos_curriculares = PostgreSQLConsultas.anos_curriculares()

    if request.method == "POST":
        nome = request.POST.get("nome")
        ano_id = request.POST.get("id_anocurricular")
        curso_id = request.POST.get("id_curso")
        
        # Se foi efetuado o upload de um PDF, este substitui o PDF atual
        ficheiro_ref = avaliacao['ficheiro']  # Keep existing if no new upload
        if "ficheiro" in request.FILES:
            ficheiro = request.FILES["ficheiro"]
            try:
                resultado_upload = upload_pdf_avaliacao(
                    ficheiro_file=ficheiro,
                    nome=nome,
                    id_curso=int(curso_id),
                    id_anocurricular=int(ano_id)
                )
                file_id_mongodb = resultado_upload["file_id"]
                ficheiro_ref = f"mongodb_gridfs:{file_id_mongodb}"
            except Exception as e:
                messages.error(request, f"Erro ao carregar nova avaliação: {str(e)}")
                return redirect("home:admin_avaliacoes_edit", id=id)
        
        # SQL: Atualiza o PDF de avaliação
        success = PostgreSQLConsultas.update_avaliacao_pdf(
            id, nome, ficheiro_ref, int(ano_id), int(curso_id)
        )
        
        if success:
            registar_log(request, operacao="UPDATE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF atualizada: {nome}")
            messages.success(request, "Calendário de avaliações atualizado!")
        else:
            messages.error(request, "Erro ao atualizar avaliação.")
        
        return redirect("home:admin_avaliacoes_list")

    return render(request, "admin/avaliacoes_form.html", {"avaliacao": avaliacao, 'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para apagar o pdf das avaliacoes
@admin_required
def admin_avaliacoes_delete(request, id):
    # SQL: Obtém a avaliação antes de deletar
    avaliacao = PostgreSQLConsultas.get_avaliacao_pdf_by_id(id)
    
    if not avaliacao:
        messages.error(request, "Avaliação não encontrada.")
        return redirect("home:admin_avaliacoes_list")
    
    nome = avaliacao['nome']
    ficheiro_ref = avaliacao['ficheiro']
    
    try:
        # Verifica se o ficheiro está no MongoDB
        if ficheiro_ref and ficheiro_ref.startswith("mongodb_gridfs:"):
            # Extrai o ID do ficheiro
            file_id_mongodb = ficheiro_ref.replace("mongodb_gridfs:", "")
            # Remove do MongoDB
            eliminar_pdf(file_id_mongodb, tipo_pdf="avaliacao")
        
        # SQL: Remove o registo da BD
        success = PostgreSQLConsultas.delete_avaliacao_pdf(id)
        
        if success:
            registar_log(request, operacao="DELETE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF apagada: {nome}")
            messages.success(request, "Calendário de avaliações apagado!")
        else:
            messages.error(request, "Erro ao apagar avaliação.")
        
    except Exception as e:
        messages.error(request, f"Erro ao apagar avaliação: {str(e)}")
    
    return redirect("home:admin_avaliacoes_list")

#view para listar os docentes no admin
def admin_users_docentes(request):
    # Redireciona para a lista geral de utilizadores
    # A filtragem é feita no cliente via JavaScript
    users_sorted = PostgreSQLConsultas.usuarios_combinado()
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    
    # Passar um flag para o template indicar que deve filtrar por "Docente"
    context = {
        "users": users_sorted,
        "cursos": cursos,
        "anos": anos,
        "filter_tipo": "Docente"
    }
    return render(request, "admin/users_list.html", context)

#view para listar os alunos no admin
def admin_users_alunos(request):
    # Redireciona para a lista geral de utilizadores
    # A filtragem é feita no cliente via JavaScript
    users_sorted = PostgreSQLConsultas.usuarios_combinado()
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    
    # Passar um flag para o template indicar que deve filtrar por "Aluno"
    context = {
        "users": users_sorted,
        "cursos": cursos,
        "anos": anos,
        "filter_tipo": "Aluno"
    }
    return render(request, "admin/users_list.html", context)

def testar_mongo(request):
    # Adicionar um log no MongoDB
    adicionar_log("teste_ligacao", {"user": "teste_django"})

    # Ler todos os logs existentes
    logs = listar_logs()

    return JsonResponse({"estado": "ok", "logs": logs})

#view para apagar o pdf dos horarios
def admin_horarios_delete(request, id):
    if PostgreSQLPDF.delete_pdf(id, 'horario'):
        messages.success(request, "Horário apagado!")
    else:
        messages.error(request, "Erro ao apagar horário")
    return redirect("home:admin_horarios_list")

# NOVA VIEW PARA TESTAR MONGO
def testar_mongo(request):
    adicionar_log("teste_ligacao", {"user": "teste_django"})
    logs = listar_logs()
    return JsonResponse({"estado": "ok", "logs": logs})

#view pagina inicial DI
def index_di(request):
    return render(request, "di/index_di.html", { "area": "di" })

#view recursos DI
def recursos_di(request):
    return render(request, "di/recursos.html", { "area": "di" })

#view sobre DI
def sobre_di(request):
    return render(request, "di/sobre.html", { "area": "di" })

#view contactos DI
def contacto_di(request):
    docentes = PostgreSQLConsultas.docentes()
    return render(request, "di/contactos.html", { "area": "di", "docentes": docentes })

#view pagina inicial EI
def index_ei(request):
    return render(request, "ei/index.html", { "area": "ei" })

#view pagina inicial TDM
def index_tdm(request):
    return render(request, "tdm/index_tdm.html", { "area": "tdm" })

#view ingressos TDM
def ingresso_tdm(request):
    return render(request, "tdm/ingresso_tdm.html", { "area": "tdm" })

#view plano curricular TDM
def plano_tdm(request):
    unidades = PostgreSQLConsultas.ucs_por_curso(2)

    plano = {}
    for uc in unidades:
        ano = uc.get('id_anocurricular')
        semestre = uc.get('semestre')
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "tdm/plano_tdm.html", {"plano": plano, "area": "tdm"})

#view para mostrar os horarios TDM
def horarios_tdm(request):
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "horarios", {"curso": "TDM"})
    
    horarios_por_ano = _listar_pdfs_por_ano('core_horariopdf', course_id=2)
    
    pode_inscrever = False
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        aluno_row = PostgreSQLTurnos.get_aluno(request.session["user_id"])
        if aluno_row and aluno_row.get("id_curso") == 2:
            pode_inscrever = True

    return render(request, "tdm/horarios_tdm.html", {
        "horarios_por_ano": horarios_por_ano, 
        "area": "tdm",
        "pode_inscrever": pode_inscrever
    })

#view contactos TDM
def contactos_tdm(request):
    docentes = PostgreSQLConsultas.docentes()
    return render(request, "tdm/contactos_tdm.html", { "area": "tdm", "docentes": docentes })

#view saidas profissionais TDM
def saidas_tdm(request):
    return render(request, "tdm/saidas.html", { "area": "tdm" })

#view avaliacoes TDM
def avaliacoes_tdm(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano('core_avaliacaopdf', course_id=2)
    return render(request, "tdm/avaliacoes_tdm.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "tdm"})

#view moodle TDM
def moodle(request):
    return render(request, "tdm/moodle.html", { "area": "tdm" })

#view para inscricao nos turnos TDM
@aluno_required
def inscricao_turno_tdm(request):
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    n_meca = request.session["user_id"]
    aluno_row = PostgreSQLTurnos.get_aluno(n_meca)
    if not aluno_row:
        messages.error(request, "Aluno não encontrado.")
        return redirect("home:login")

    if aluno_row.get("id_curso") != 2:
        messages.error(request, "Esta página é apenas para alunos de Tecnologia e Design Multimédia.")
        if aluno_row.get("id_curso") == 1:
            return redirect("home:inscricao_turno")
        return redirect("home:index")

    inscricoes_existentes = PostgreSQLTurnos.inscricoes_turno_por_aluno(n_meca)
    turno_escolhido = None
    if inscricoes_existentes:
        primeiro = inscricoes_existentes[0]
        turno_escolhido = primeiro.get("turno_numero")

    inscricoes_uc = PostgreSQLTurnos.ucs_inscritas_por_aluno(n_meca)

    turnos_info = {
        1: {"nome": "Turno 1", "ucs": []},
        2: {"nome": "Turno 2", "ucs": []}
    }

    def _dia_semana(hora_inicio):
        try:
            h_int = hora_inicio.hour
            if 8 <= h_int < 10:
                return "Segunda"
            if 10 <= h_int < 12:
                return "Terça"
            if 12 <= h_int < 14:
                return "Quarta"
            if 14 <= h_int < 16:
                return "Quinta"
            return "Sexta"
        except Exception:
            return "?"

    for uc_row in inscricoes_uc:
        if uc_row.get("id_curso") != 2:
            continue
        uc_id = uc_row.get("id_unidadecurricular")
        turnos_uc = PostgreSQLTurnos.turno_uc_por_uc(uc_id)

        for tu in turnos_uc:
            n_turno = tu.get("n_turno")
            if n_turno not in [1, 2]:
                continue

            turno_id = tu.get("id_turno")
            ocupados = PostgreSQLTurnos.count_inscritos(turno_id, uc_id)
            capacidade = tu.get("capacidade") or 0
            vagas = capacidade - ocupados
            if vagas < 0:
                vagas = 0

            hora_inicio = tu.get("hora_inicio")
            hora_fim = tu.get("hora_fim")
            hora_inicio_str = hora_inicio.strftime("%H:%M") if hora_inicio else "?"
            hora_fim_str = hora_fim.strftime("%H:%M") if hora_fim else "?"
            dia_semana = _dia_semana(hora_inicio) if hora_inicio else "?"

            turnos_info[n_turno]["ucs"].append({
                "nome": uc_row.get("nome"),
                "horario": f"{dia_semana} {hora_inicio_str}-{hora_fim_str}",
                "vagas": vagas,
                "capacidade": capacidade
            })

    return render(request, "tdm/inscricao_turno_tdm.html", {"turnos_info": turnos_info, "turno_escolhido": turno_escolhido, "area": "tdm"})

#view para inscrevr no turno TDM
@aluno_required
def inscrever_turno_tdm(request, n_turno):
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "Apenas alunos podem inscrever-se em turnos.")
        return redirect("home:login")
    
    inicio_tempo = time.time()
    n_meca = request.session["user_id"]
    aluno_row = PostgreSQLTurnos.get_aluno(n_meca)

    if not aluno_row:
        messages.error(request, "Aluno não encontrado.")
        return redirect("home:login")

    if aluno_row.get("id_curso") != 2:
        messages.error(request, "Esta funcionalidade é apenas para alunos de TDM.")
        return redirect("home:index")

    try:
        inscricoes_existentes = PostgreSQLTurnos.inscricoes_turno_por_aluno(n_meca)
        if inscricoes_existentes:
            messages.warning(request, "Já tens um turno escolhido. Para mudar, contacta a coordenação.")
            return redirect("home:inscricao_turno_tdm")

        inscricoes_uc = PostgreSQLTurnos.ucs_inscritas_por_aluno(n_meca)

        inscricoes_realizadas = 0
        erros = []

        for uc_row in inscricoes_uc:
            if uc_row.get("id_curso") != 2:
                continue
            uc_id = uc_row.get("id_unidadecurricular")

            try:
                turnos_uc = PostgreSQLTurnos.turno_uc_por_uc(uc_id)
                turno_alvo = None
                for tu in turnos_uc:
                    if tu.get("n_turno") == n_turno:
                        turno_alvo = tu
                        break

                if not turno_alvo:
                    erros.append(f"{uc_row.get('nome')}: Turno {n_turno} não disponível")
                    continue

                turno_id = turno_alvo.get("id_turno")
                capacidade = turno_alvo.get("capacidade") or 0
                ocupados = PostgreSQLTurnos.count_inscritos(turno_id, uc_id)

                if ocupados >= capacidade:
                    erros.append(f"{uc_row.get('nome')}: Turno {n_turno} cheio")
                    continue

                criado = PostgreSQLTurnos.create_inscricao_turno(n_meca, turno_id, uc_id)
                tempo_ms = int((time.time() - inicio_tempo) * 1000)

                if not criado:
                    erros.append(f"{uc_row.get('nome')}: erro ao criar inscrição")
                    continue

                registar_auditoria_inscricao(n_meca, turno_id, uc_id, uc_row.get("nome", ""), 'sucesso', f'Inscrição TDM - Turno {n_turno}', tempo_ms)
                inscricoes_realizadas += 1

            except Exception as e:
                erros.append(f"{uc_row.get('nome')}: {str(e)}")

        if inscricoes_realizadas > 0:
            messages.success(request, f"✓ Inscrito no Turno {n_turno} em {inscricoes_realizadas} UC(s)!")
            adicionar_log("inscricao_turno_tdm_sucesso", {"aluno": aluno_row.get("nome"), "turno": n_turno, "ucs_inscritas": inscricoes_realizadas}, request)

        if erros:
            for erro in erros:
                messages.warning(request, f"⚠ {erro}")

        return redirect("home:inscricao_turno_tdm")

    except Exception as e:
        messages.error(request, f"Erro ao processar inscrição: {str(e)}")
        registar_erro("inscrever_turno_tdm", str(e), {"aluno": n_meca, "turno": n_turno})
        return redirect("home:inscricao_turno_tdm")

#view para pagina inicial RSI
def index_rsi(request):
    return render(request, "rsi/index_rsi.html", { "area": "rsi" })

#view ingresso RSI
def ingresso_rsi(request):
    return render(request, "rsi/ingresso_rsi.html", { "area": "rsi" })

#view o plano curricular RSI
def plano_curric_rsi(request):
    unidades = PostgreSQLConsultas.ucs_por_curso(3)

    plano = {}
    for uc in unidades:
        ano = uc.get('id_anocurricular')
        semestre = uc.get('semestre')
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "rsi/plano_curric_rsi.html", {"plano": plano, "area": "rsi"})

#view estagio RSI
def estagio_rsi(request):
    return render(request, "rsi/estagio_rsi.html", { "area": "rsi" })

#view contactos RSI
def contactos_rsi(request):
    docentes = PostgreSQLConsultas.docentes()
    return render(request, "rsi/contactos_rsi.html", { "area": "rsi", "docentes": docentes })

#view avaliaçoes RSI
def avaliacoes_rsi(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano('core_avaliacaopdf', course_id=3)
    return render(request, "rsi/avaliacoes_rsi.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "rsi"})

#view para saidas profissionais RSI
def saidas_rsi(request):
    return render(request, "rsi/saidas_rsi.html", { "area": "rsi" })

#view horarios RSI
def horarios_rsi(request):
    horarios_por_ano = _listar_pdfs_por_ano('core_horariopdf', course_id=3)
    return render(request, "rsi/horarios_rsi.html", {"horarios_por_ano": horarios_por_ano, "area": "rsi"})

#view para pagina inicial DWDM
def index_dwdm(request):
    return render(request, "dwdm/index_dwdm.html", { "area": "dwdm" })

#view ingresso DWDM
def ingresso_dwdm(request):
    return render(request, "dwdm/ingresso_dwdm.html", { "area": "dwdm" })

#view para plano curricular DWDM
def plano_dwdm(request):
    unidades = PostgreSQLConsultas.ucs_por_curso(4)

    plano = {}
    for uc in unidades:
        ano = uc.get('id_anocurricular')
        semestre = uc.get('semestre')
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "dwdm/plano_dwdm.html", {"plano": plano, "area": "dwdm"})

#view para horarios DWDM
def horarios_dwdm(request):
    horarios_por_ano = _listar_pdfs_por_ano('core_horariopdf', course_id=4)
    return render(request, "dwdm/horarios_dwdm.html", {"horarios_por_ano": horarios_por_ano, "area": "dwdm"})

#view para avaliacoes DWDM
def avaliacoes_dwdm(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano('core_avaliacaopdf', course_id=4)
    return render(request, "dwdm/avaliacoes_dwdm.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "dwdm"})

#view para contactos DWDM
def contactos_dwdm(request):
    # SQL: Lista todos os docentes
    docentes = PostgreSQLConsultas.docentes()
    return render(request, "dwdm/contactos_dwdm.html", { "area": "dwdm", "docentes": docentes })

#view para etagio DWDM
def estagio_dwdm(request):
    return render(request, "dwdm/estagio_dwdm.html", { "area": "dwdm" })

#view para saidas profissionais DWDM
def saidas_dwdm(request):
    return render(request, "dwdm/saidas_dwdm.html", { "area": "dwdm" })

#view para programa brightstart DWDM
def brightstart(request):
    return render(request, "dwdm/brightstart.html", { "area": "dwdm" })

#view para pagina inicial do mestrado
def index_mestrado(request):
    return render(request, "eisi/index_mestrado.html", { "area": "eisi" })

#view para testemunhos do mestrado
def testemunho_mestrado(request):
    return render(request, "eisi/testemunho_mestrado.html", { "area": "eisi" })

#view para pagina de ingresso do mestrado
def ingresso_mestrado(request):
    return render(request, "eisi/ingresso_mestrado.html", { "area": "eisi" })

#view para pagina dos destinatarios do mestrado
def destinatarios_mestrado(request):
    return render(request, "eisi/destinatarios_mestrado.html", { "area": "eisi" })

#view plano curricular mestrado
def plano_curric_mestrado(request):
    # SQL: Lista UCs do curso 5 (Mestrado)
    unidades = PostgreSQLConsultas.ucs_por_curso(5)

    plano = {}
    for uc in unidades:
        ano = uc.get('id_anocurricular')
        semestre = uc.get('semestre')
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "eisi/plano_curric_mestrado.html", {"plano": plano, "area": "eisi"})

#view horarios do mestrado
def horarios_mestrado(request):
    horarios_por_ano = _listar_pdfs_por_ano("horario_pdf", course_id=5)
    return render(request, "eisi/horarios_mestrado.html", {"horarios_por_ano": horarios_por_ano, "area": "eisi"})

#view avaliacoes do mestrado
def avaliacoes_mestrado(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano("avaliacao_pdf", course_id=5)
    return render(request, "eisi/avaliacoes_mestrado.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "eisi"})

#view contactos do mestrado
def contactos_mestrado(request):
    # SQL: Lista todos os docentes
    docentes = PostgreSQLConsultas.docentes()
    return render(request, "eisi/contactos_mestrado.html", { "area": "eisi", "docentes": docentes })

#view para listar UCs no admin
def admin_uc_list(request):
    # SQL: Lista todas as UCs
    ucs = PostgreSQLConsultas.list_all_ucs()
    
    # Filtros
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    curso = request.GET.get('curso')
    
    # Aplicar filtros
    if ano:
        ucs = [u for u in ucs if str(u.get('id_anocurricular')) == str(ano)]
    if semestre:
        ucs = [u for u in ucs if str(u.get('id_semestre')) == str(semestre)]
    if curso:
        ucs = [u for u in ucs if str(u.get('id_curso')) == str(curso)]
    
    # SQL: Carrega listas para filtros
    anos = PostgreSQLConsultas.anos_curriculares()
    semestres = PostgreSQLConsultas.get_semestres()
    cursos = PostgreSQLConsultas.cursos_list()
    
    return render(request, "admin/uc_list.html", {
        "ucs": ucs,
        "anos": anos,
        "semestres": semestres,
        "cursos": cursos,
        "ano_selected": ano,
        "semestre_selected": semestre,
        "curso_selected": curso,
    })

#view para criar UC
def admin_uc_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        ects = request.POST.get("ects")
        id_curso = request.POST.get("curso")
        id_ano = request.POST.get("ano")
        id_semestre = request.POST.get("semestre")

        # SQL: Cria UC
        uc_id = PostgreSQLConsultas.create_uc(
            nome=nome,
            id_curso=int(id_curso),
            id_anocurricular=int(id_ano),
            id_semestre=int(id_semestre),
            ects=float(ects) if ects else 0.0
        )

        if uc_id:
            registar_log(request, operacao="CREATE", entidade="unidade_curricular", chave=str(uc_id), detalhes=f"UC criada: {nome}")
            messages.success(request, "Unidade Curricular criada com sucesso!")
        else:
            messages.error(request, "Erro ao criar Unidade Curricular.")

        return redirect("home:admin_uc_list")

    # SQL: Passa listas para o form
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    semestres = PostgreSQLConsultas.get_semestres()

    return render(request, "admin/uc_form.html", {
        "uc": None,
        "turnos_uc": [],
        "turnos_count": 0,
        "cursos": cursos,
        "anos": anos,
        "semestres": semestres,
    })

#view para editar UC
def admin_uc_edit(request, id):
    # SQL: Obtém a UC
    uc = PostgreSQLConsultas.get_uc_by_id(id)
    
    if not uc:
        messages.error(request, "UC não encontrada.")
        return redirect("home:admin_uc_list")

    # SQL: Obtém turnos associados à UC
    turnos_uc = PostgreSQLConsultas.get_turnos_uc_by_uc_id(id)
    turnos_count = len(turnos_uc)

    if request.method == "POST":
        action = request.POST.get("action") or "update_uc"

        # Atualizar apenas nome e ects
        if action == "update_uc":
            nome = request.POST.get("nome")
            ects = request.POST.get("ects")
            curso = request.POST.get("curso")
            ano = request.POST.get("ano")
            semestre = request.POST.get("semestre")
            
            # SQL: Atualiza UC
            success = PostgreSQLConsultas.update_uc(
                id, nome, int(curso), int(ano), int(semestre), float(ects) if ects else 0.0
            )
            
            if success:
                registar_log(request, operacao="UPDATE", entidade="unidade_curricular", chave=str(id), detalhes=f"UC atualizada: {nome}")
                messages.success(request, "Unidade Curricular atualizada!")
            else:
                messages.error(request, "Erro ao atualizar UC.")
            
            return redirect("home:admin_uc_list")

        # Adicionar um turno à UC
        if action == "add_turno":
            n_turno = request.POST.get("n_turno")
            tipo = request.POST.get("tipo")
            capacidade = request.POST.get("capacidade")
            hora_inicio = request.POST.get("hora_inicio")
            hora_fim = request.POST.get("hora_fim")
            
            # SQL: Cria turno
            novo_turno_id = PostgreSQLConsultas.create_turno(n_turno or "0", int(capacidade) if capacidade else 0, tipo or "")
            
            if novo_turno_id:
                # SQL: Associa turno à UC
                success = PostgreSQLConsultas.create_turno_uc(novo_turno_id, id, hora_inicio or "", hora_fim or "")
                
                if success:
                    registar_log(request, operacao="CREATE", entidade="turno", chave=str(novo_turno_id), detalhes=f"Turno criado para UC {uc['nome']}")
                    messages.success(request, "Turno adicionado à UC!")
                else:
                    messages.error(request, "Erro ao associar turno à UC.")
            else:
                messages.error(request, "Erro ao criar turno.")
            
            return redirect("home:admin_uc_edit", id=id)

        # Atualizar um turno da UC
        if action == "update_turno":
            turno_id = request.POST.get("turno_id")
            n_turno = request.POST.get("n_turno")
            tipo = request.POST.get("tipo")
            capacidade = request.POST.get("capacidade")
            hora_inicio = request.POST.get("hora_inicio")
            hora_fim = request.POST.get("hora_fim")
            
            # SQL: Atualiza turno
            success = PostgreSQLConsultas.update_turno(int(turno_id), n_turno or "0", int(capacidade) if capacidade else 0, tipo or "")
            
            if success:
                registar_log(request, operacao="UPDATE", entidade="turno", chave=str(turno_id), detalhes=f"Turno atualizado para UC {uc['nome']}")
                messages.success(request, "Turno atualizado!")
            else:
                messages.error(request, "Erro ao atualizar turno.")
            
            return redirect("home:admin_uc_edit", id=id)

        # Apagar turno associado a UC
        if action == "delete_turno":
            turno_id = request.POST.get("turno_id")
            
            # SQL: Deleta turno_uc e turno
            success = PostgreSQLConsultas.delete_turno(int(turno_id))
            
            if success:
                registar_log(request, operacao="DELETE", entidade="turno", chave=str(turno_id), detalhes=f"Turno removido da UC {uc['nome']}")
                messages.success(request, "Turno removido!")
            else:
                messages.error(request, "Erro ao remover turno.")
            
            return redirect("home:admin_uc_edit", id=id)

    # SQL: Passa listas para os selects
    cursos = PostgreSQLConsultas.cursos_list()
    anos = PostgreSQLConsultas.anos_curriculares()
    semestres = PostgreSQLConsultas.get_semestres()

    return render(request, "admin/uc_form.html", {
        "uc": uc,
        "turnos_uc": turnos_uc,
        "turnos_count": turnos_count,
        "cursos": cursos,
        "anos": anos,
        "semestres": semestres,
    })

#view para apagar UC
def admin_uc_delete(request, id):
    # SQL: Obtém UC
    uc = PostgreSQLConsultas.get_uc_by_id(id)
    
    if not uc:
        messages.error(request, "UC não encontrada.")
        return redirect("home:admin_uc_list")

    # SQL: Deleta turnos_uc e turnos associados
    count_t = PostgreSQLConsultas.delete_turnos_uc_by_uc_id(id)
    
    # SQL: Deleta UC
    success = PostgreSQLConsultas.delete_uc(id)
    
    if success:
        registar_log(request, operacao="DELETE", entidade="unidade_curricular", chave=str(id), detalhes=f"UC apagada: {uc['nome']} (e {count_t} turnos associados)")
        messages.success(request, f"Unidade Curricular apagada! ({count_t} turnos removidos)")
    else:
        messages.error(request, "Erro ao apagar UC.")
    
    return redirect("home:admin_uc_list")

#view para listar logs unificados entre SQL e MOJGO
def admin_logs_list(request):
    operacao_filter = (request.GET.get('operacao') or '').strip()
    entidade_filter = (request.GET.get('entidade') or '').strip()
    limite = int(request.GET.get('limite', 500) or 500)
    limite = 1000 if limite > 1000 else (100 if limite < 1 else limite)

    #auxiliar para converter valores em string/JSON
    def _to_str(val):
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        try:
            return json.dumps(val, ensure_ascii=False)
        except Exception:
            return str(val)

    #query nos logs sql usando SQL puro
    sql_logs_raw = PostgreSQLLogs.list_logs(operacao_filter=operacao_filter, entidade_filter=entidade_filter, limite=limite)

    #converte logs SQL para uma lista de dicionários
    sql_logs = [
        {
            "id": log.get('id_log'),
            "fonte": "SQL",
            "data": log.get('data_hora'),
            "data_display": log.get('data_hora').strftime("%Y-%m-%d %H:%M:%S") if log.get('data_hora') else "",
            "operacao": log.get('operacao'),
            "entidade": log.get('entidade'),
            "chave": log.get('chave_primaria'),
            "utilizador": log.get('utilizador_db'),
            "ip": "",
            "user_agent": "",
            "detalhes": _to_str(log.get('detalhes')),
        }
        for log in sql_logs_raw
    ]

    #obtem os logs em Mongo utilizando os mesmos filtros e limite
    mongo_logs = listar_eventos_mongo(filtro_acao=operacao_filter or None, filtro_entidade=entidade_filter or None, limite=limite,)

    #junta os logs do sql com os do mongo e ordena por data
    logs_unificados = sql_logs + mongo_logs
    logs_unificados = sorted(logs_unificados, key=lambda l: l.get("data") or datetime.min, reverse=True)[:limite]

    #carrega mais logs para construir listas de filtros
    mongo_all_for_filters = listar_eventos_mongo(limite=1000)
    operacoes = set(PostgreSQLLogs.get_distinct_operacoes() + [l.get("operacao", "") for l in mongo_all_for_filters])
    entidades = set(PostgreSQLLogs.get_distinct_entidades() + [l.get("entidade", "") for l in mongo_all_for_filters])

    return render(request, "admin/logs_list.html", {
        "logs": logs_unificados,
        "operacoes": sorted([op for op in operacoes if op]),
        "entidades": sorted([ent for ent in entidades if ent]),
        "operacao_filter": operacao_filter,
        "entidade_filter": entidade_filter,
        "limite": limite,
    })

#VIEW PARA ALGUMA COISA
def forum(request):
    return render(request, "forum/index_forum.html")

#view pagina inicial DAPE
def dape(request):
    # Busca todas as propostas de estágio via PostgreSQL
    propostas = PostgreSQLDAPE.listar_propostas()
    
    # Define proposta_id e conta disponíveis
    propostas_disponiveis = 0
    for proposta in propostas:
        proposta["proposta_id"] = str(proposta.get("id_proposta", ""))
        proposta["is_minha_proposta"] = False
        if not proposta.get("aluno_atribuido"):
            propostas_disponiveis += 1
    
    # Se o usuário for aluno, marca favoritos e a sua proposta (se atribuída)
    if request.session.get("user_tipo") == "aluno":
        aluno_id = request.session.get("user_id")
        proposta_atribuida = None
        outras_propostas = []
        
        for proposta in propostas:
            is_fav = PostgreSQLDAPE.verificar_favorito(aluno_id, proposta.get("id_proposta"))
            proposta["is_favorito"] = is_fav
            
            if proposta.get("aluno_atribuido") and str(proposta.get("aluno_atribuido")) == str(aluno_id):
                proposta["is_minha_proposta"] = True
                proposta_atribuida = proposta
            else:
                outras_propostas.append(proposta)
        
        propostas = [proposta_atribuida] + outras_propostas if proposta_atribuida else outras_propostas
    
    # Regista a consulta para analytics
    adicionar_log(
        "visualizar_propostas_estagio",
        {"total_propostas": len(propostas)},
        request
    )
    
    return render(request, "dape/dape.html", {
        "propostas": propostas,
        "propostas_disponiveis": propostas_disponiveis,
        "area": "dape"
    })

# View para contactos DAPE
def contactos_dape(request):
    return render(request, "dape/contactos.html", {
        "area": "dape"
    })

# View para documentos DAPE
def documentos_dape(request):
    return render(request, "dape/documentos.html", {
        "area": "dape"
    })


# ==========================================
# VIEW PARA SERVIR PDFs DO MongoDB (GridFS)
# ==========================================
def servir_pdf_mongodb(request, file_id, tipo_pdf):
    """
    Serve PDFs armazenados no MongoDB via GridFS
    
    Esta view é chamada quando o Django tenta aceder a um PDF que está no MongoDB.
    Em vez de procurar no filesystem, vai buscar ao GridFS.
    
    Args:
        file_id: ID único do ficheiro no MongoDB
        tipo_pdf: Tipo do PDF ("horario" ou "avaliacao")
    
    Returns:
        FileResponse com o PDF ou erro 404
    """
    try:
        # ==========================================
        # BUSCAR PDF DO MongoDB
        # ==========================================
        # Usa a função download_pdf do gridfs_service
        # Retorna o conteúdo do PDF e os metadados
        pdf_bytes, metadata = download_pdf(file_id, tipo_pdf=tipo_pdf)
        
        # ==========================================
        # PREPARAR RESPOSTA HTTP
        # ==========================================
        # FileResponse é a resposta do Django para ficheiros
        # Define o tipo de conteúdo como PDF
        response = FileResponse(
            pdf_bytes,
            content_type='application/pdf'
        )
        
        # Define o nome do ficheiro para download
        # Usa o nome original dos metadados se existir
        nome_ficheiro = metadata.get("nome_ficheiro_original", f"{metadata.get('nome', 'documento')}.pdf")
        response['Content-Disposition'] = f'inline; filename="{nome_ficheiro}"'
        
        # Regista o acesso ao PDF (analytics)
        adicionar_log(
            "download_pdf",
            {
                "file_id": file_id,
                "tipo": tipo_pdf,
                "nome": metadata.get("nome"),
                "tamanho": metadata.get("tamanho")
            },
            request
        )
        
        return response
    
    except Exception as e:
        # Se algo correr mal, retorna erro 404
        from django.http import Http404
        raise Http404(f"PDF não encontrado no MongoDB: {str(e)}")

# ==========================================
# VIEWS PARA PROPOSTAS DE ESTÁGIO
# ==========================================

@user_required
def criar_proposta_estagio_view(request):
    """View para criar uma nova proposta de estágio"""
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descricao = request.POST.get("descricao")
        empresa = request.POST.get("empresa")
        orientador = request.POST.get("orientador")
        
        # Verifica se é aluno (baseado na sessão)
        if request.session.get("user_tipo") != "aluno":
            messages.error(request, "Apenas alunos podem criar propostas de estágio.")
            return redirect("home:index")
        
        aluno_id = request.session.get("user_id")
        aluno_nome = request.session.get("user_nome")
        # Cria a proposta no PostgreSQL
        novo_id = PostgreSQLDAPE.criar_proposta(
            aluno_id=aluno_id,
            titulo=titulo,
            entidade=empresa,
            descricao=descricao,
            requisitos=None,
            modelo=None,
            orientador_empresa=orientador,
            telefone=None,
            email=None,
            logo=None,
        )
        
        # Regista log da criação
        adicionar_log(
            "criar_proposta_estagio",
            {
                "aluno_id": aluno_id,
                "titulo": titulo,
                "empresa": empresa,
                "id_proposta": novo_id
            },
            request
        )
        if novo_id:
            messages.success(request, "Proposta de estágio criada com sucesso!")
        else:
            messages.error(request, "Erro ao criar proposta de estágio.")
        return redirect("home:listar_propostas_estagio")
    
    return render(request, "proposta_estagio/criar.html")

@user_required
def listar_propostas_estagio_view(request):
    """View para listar propostas de estágio do aluno"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem ver suas propostas de estágio.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    # Lista propostas do aluno via PostgreSQL
    propostas = PostgreSQLDAPE.listar_propostas({"aluno_id": aluno_id})
    
    # Regista consulta
    adicionar_log(
        "listar_propostas_estagio",
        {"aluno_id": aluno_id, "total_propostas": len(propostas)},
        request
    )
    
    return render(request, "dape/dape.html", {"propostas": propostas})

@user_required
def atualizar_proposta_estagio_view(request, titulo):
    """View para atualizar uma proposta de estágio"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem atualizar propostas de estágio.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    if request.method == "POST":
        updates = {}
        if request.POST.get("titulo"):
            updates["titulo"] = request.POST.get("titulo")
        if request.POST.get("descricao"):
            updates["descricao"] = request.POST.get("descricao")
        if request.POST.get("empresa"):
            updates["entidade"] = request.POST.get("empresa")
        if request.POST.get("orientador"):
            updates["orientador_empresa"] = request.POST.get("orientador")
        
        # Atualiza a proposta via PostgreSQL
        sucesso = PostgreSQLDAPE.atualizar_proposta(aluno_id, titulo, updates)
        
        if sucesso:
            # Regista log da atualização
            adicionar_log(
                "atualizar_proposta_estagio",
                {"aluno_id": aluno_id, "titulo_antigo": titulo, "updates": updates},
                request
            )
            messages.success(request, "Proposta de estágio atualizada com sucesso!")
        else:
            messages.error(request, "Erro ao atualizar proposta de estágio.")
        
        return redirect("home:listar_propostas_estagio")
    
    # Busca a proposta atual para preencher o formulário
    propostas = PostgreSQLDAPE.listar_propostas({"aluno_id": aluno_id, "titulo": titulo})
    if not propostas:
        messages.error(request, "Proposta não encontrada.")
        return redirect("home:listar_propostas_estagio")
    
    proposta = propostas[0]
    return render(request, "dape/dape.html", {"proposta": proposta})

@user_required
def deletar_proposta_estagio_view(request, titulo):
    """View para deletar uma proposta de estágio"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem deletar propostas de estágio.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    # Deleta a proposta via PostgreSQL
    sucesso = PostgreSQLDAPE.eliminar_proposta(aluno_id, titulo)
    
    if sucesso:
        # Regista log da deleção
        adicionar_log(
            "deletar_proposta_estagio",
            {"aluno_id": aluno_id, "titulo": titulo},
            request
        )
        messages.success(request, "Proposta de estágio deletada com sucesso!")
    else:
        messages.error(request, "Erro ao deletar proposta de estágio.")
    
    return redirect("home:listar_propostas_estagio")

# ==========================================
# VIEWS PARA FAVORITOS
# ==========================================

def favoritos_view(request):
    """View para mostrar as propostas favoritas do aluno"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem ver seus favoritos.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    # Busca propostas favoritas via PostgreSQL
    propostas_favoritas = PostgreSQLDAPE.listar_favoritos(aluno_id)
    
    # Adiciona proposta_id para cada proposta
    for proposta in propostas_favoritas:
        proposta["proposta_id"] = str(proposta.get("id_proposta", ""))
    
    # Regista consulta
    adicionar_log(
        "visualizar_favoritos",
        {"aluno_id": aluno_id, "total_favoritos": len(propostas_favoritas)},
        request
    )
    
    return render(request, "dape/favoritos.html", {
        "propostas": propostas_favoritas,
        "area": "dape"
    })

def toggle_favorito_view(request):
    """View para adicionar/remover favorito via AJAX"""
    print("toggle_favorito_view called")
    try:
        if request.method == "POST" and request.session.get("user_tipo") == "aluno":
            proposta_id = request.POST.get("proposta_id")
            aluno_id = request.session.get("user_id")
            print(f"proposta_id: {proposta_id}, aluno_id: {aluno_id}")
            
            if proposta_id and aluno_id:
                res = PostgreSQLDAPE.toggle_favorito(int(aluno_id), int(proposta_id))
                action = "added" if res.get("added") else "removed"
                adicionar_log(f"favorito_{action}", {"aluno_id": aluno_id, "proposta_id": proposta_id}, request)
                return JsonResponse({"success": True, "action": action})
        
        print("Invalid request")
        return JsonResponse({"success": False, "error": "Invalid request"})
    except Exception as e:
        print(f"Exception in toggle_favorito_view: {e}")
        return JsonResponse({"success": False, "error": str(e)})
    
from django.http import Http404

def proposta_detalhes(request, id_proposta):
    """
    View para mostrar os detalhes de uma proposta de estágio
    (dados vêm do PostgreSQL)
    """

    # Buscar proposta por ID
    proposta = PostgreSQLDAPE.obter_proposta_por_id(id_proposta)

    if not proposta:
        raise Http404("Proposta não encontrada")

    # Normalizar ID
    proposta["proposta_id"] = str(proposta.get("id_proposta", ""))

    # Verificar favorito (se aluno)
    if request.session.get("user_tipo") == "aluno":
        aluno_id = request.session.get("user_id")
        proposta["is_favorito"] = PostgreSQLDAPE.verificar_favorito(aluno_id, proposta["id_proposta"])

    # Obter aluno atribuído (se existir) - FUNCIONALIDADE AINDA NÃO IMPLEMENTADA
    aluno_atribuido = None  # obter_aluno_atribuido(proposta["proposta_id"])
    
    # Registar acesso
    adicionar_log(
        "visualizar_detalhes_proposta",
        {"proposta_id": proposta["proposta_id"]},
        request
    )

    return render(request, "dape/detalhes.html", {
        "proposta": proposta,
        "aluno_atribuido": aluno_atribuido,
        "area": "dape"
    })

def atribuir_aluno_view(request, id_proposta):
    """
    View para atribuir um aluno a uma proposta de estágio (apenas admin)
    FUNCIONALIDADE AINDA NÃO IMPLEMENTADA
    """
    messages.error(request, "Funcionalidade de atribuir aluno ainda não implementada.")
    return redirect("home:proposta_detalhes", id_proposta=id_proposta)
    
    # TODO: Descomentar quando implementar as funções de atribuição
    # Verificar se é admin
    # if request.session.get("user_tipo") != "admin":
    #     messages.error(request, "Apenas administradores podem atribuir alunos a propostas.")
    #     return redirect("home:proposta_detalhes", id_proposta=id_proposta)
    # 
    # if request.method == "POST":
    #     n_mecanografico = request.POST.get("n_mecanografico", "").strip()
    #     acao = request.POST.get("acao", "atribuir")
    #     
    #     if acao == "remover":
    #         # Remover atribuição
    #         sucesso = remover_atribuicao_proposta(id_proposta)
    #         if sucesso:
    #             adicionar_log(
    #                 "remover_atribuicao_proposta",
    #                 {"proposta_id": id_proposta},
    #                 request
    #             )
    #             messages.success(request, "Atribuição removida com sucesso!")
    #         else:
    #             messages.error(request, "Erro ao remover atribuição.")
    #     elif n_mecanografico:
    #         # Buscar nome do aluno
    #         try:
    #             aluno = Aluno.objects.get(n_mecanografico=n_mecanografico)
    #             aluno_nome = aluno.nome
    #         except Aluno.DoesNotExist:
    #             messages.error(request, f"Aluno com número mecanográfico {n_mecanografico} não encontrado.")
    #             return redirect("home:proposta_detalhes", id_proposta=id_proposta)
    #         
    #         # Verificar se o aluno já tem uma proposta atribuída
    #         proposta_existente = verificar_aluno_tem_proposta(n_mecanografico)
    #         if proposta_existente:
    #             messages.error(
    #                 request, 
    #                 f"O aluno {aluno_nome} já tem uma proposta atribuída: '{proposta_existente.get('titulo')}' ({proposta_existente.get('entidade')}). "
    #                 f"Remova essa atribuição primeiro antes de atribuir uma nova proposta."
    #             )
    #             return redirect("home:proposta_detalhes", id_proposta=id_proposta)
    #         
    #         # Atribuir aluno à proposta
    #         sucesso = atribuir_aluno_proposta(id_proposta, n_mecanografico, aluno_nome)
    #         if sucesso:
    #             adicionar_log(
    #                 "atribuir_aluno_proposta",
    #                 {
    #                     "proposta_id": id_proposta,
    #                     "aluno_n_mecanografico": n_mecanografico,
    #                     "aluno_nome": aluno_nome
    #                 },
    #                 request
    #             )
    #             messages.success(request, f"Aluno {aluno_nome} atribuído com sucesso!")
    #         else:
    #             messages.error(request, "Erro ao atribuir aluno à proposta.")
    #     else:
    #         messages.error(request, "Número mecanográfico é obrigatório.")
    # 
    # return redirect("home:proposta_detalhes", id_proposta=id_proposta)


# ==========================================
# VIEWS ADMIN - GESTÃO PROPOSTAS DAPE
# ==========================================

@admin_required
def admin_dape_list(request):
    """Lista todas as propostas DAPE para gestão"""
    propostas = PostgreSQLDAPE.listar_propostas()
    
    # Adiciona o ID formatado para cada proposta
    for proposta in propostas:
        proposta["proposta_id"] = str(proposta.get("id_proposta", ""))
    
    return render(request, "admin/dape_list.html", {
        "propostas": propostas,
        "total_propostas": len(propostas)
    })


@admin_required
def admin_dape_create(request):
    """Cria uma nova proposta DAPE"""
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        entidade = request.POST.get("entidade")
        descricao = request.POST.get("descricao")
        requisitos = request.POST.get("requisitos")
        modelo = request.POST.get("modelo")
        orientador_empresa = request.POST.get("orientador_empresa")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        logo = request.POST.get("logo")

        novo_id = PostgreSQLDAPE.criar_proposta(
            aluno_id=None,
            titulo=titulo,
            entidade=entidade,
            descricao=descricao,
            requisitos=requisitos,
            modelo=modelo,
            orientador_empresa=orientador_empresa,
            telefone=telefone,
            email=email,
            logo=logo,
        )

        if novo_id:
            adicionar_log(
                "admin_criar_proposta",
                {"titulo": titulo, "entidade": entidade, "id_proposta": novo_id},
                request
            )
            messages.success(request, f"Proposta '{titulo}' criada com sucesso!")
            return redirect("home:admin_dape_list")
        else:
            messages.error(request, "Erro ao criar proposta.")
    
    return render(request, "admin/dape_form.html", {"proposta": None})


@admin_required
def admin_dape_edit(request, id):
    """Edita uma proposta DAPE existente (admin)"""
    try:
        pid = int(id)
    except Exception:
        messages.error(request, "ID inválido.")
        return redirect("home:admin_dape_list")

    proposta = PostgreSQLDAPE.obter_proposta_por_id(pid)
    if not proposta:
        messages.error(request, "Proposta não encontrada.")
        return redirect("home:admin_dape_list")

    if request.method == "POST":
        updates = {
            "titulo": request.POST.get("titulo"),
            "entidade": request.POST.get("entidade"),
            "descricao": request.POST.get("descricao"),
            "requisitos": request.POST.get("requisitos"),
            "modelo": request.POST.get("modelo"),
            "orientador_empresa": request.POST.get("orientador_empresa"),
            "telefone": request.POST.get("telefone"),
            "email": request.POST.get("email"),
            "logo": request.POST.get("logo"),
        }

        sucesso = PostgreSQLDAPE.admin_atualizar_proposta(pid, updates)
        if sucesso:
            adicionar_log("admin_editar_proposta", {"id": pid, "updates": updates}, request)
            messages.success(request, f"Proposta '{updates.get('titulo') or proposta.get('titulo')}' atualizada com sucesso!")
            return redirect("home:admin_dape_list")
        else:
            messages.error(request, "Erro ao atualizar proposta.")

    return render(request, "admin/dape_form.html", {"proposta": proposta})


@admin_required
def admin_dape_delete(request, id):
    """Remover uma proposta DAPE (admin)"""
    try:
        pid = int(id)
    except Exception:
        messages.error(request, "ID inválido.")
        return redirect("home:admin_dape_list")

    proposta = PostgreSQLDAPE.obter_proposta_por_id(pid)
    if not proposta:
        messages.error(request, "Proposta não encontrada.")
        return redirect("home:admin_dape_list")

    titulo = proposta.get("titulo", "Desconhecido")
    sucesso = PostgreSQLDAPE.admin_eliminar_proposta(pid)
    if sucesso:
        adicionar_log("admin_deletar_proposta", {"id": pid, "titulo": titulo}, request)
        messages.success(request, f"Proposta '{titulo}' eliminada com sucesso!")
    else:
        messages.error(request, "Erro ao eliminar proposta.")

    return redirect("home:admin_dape_list")
