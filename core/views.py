from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from .models import AnoCurricular, UnidadeCurricular, Semestre, Docente, Curso, HorarioPDF, AvaliacaoPDF, Aluno, TurnoUc, Turno, InscricaoTurno, InscritoUc, LogEvento, AuditoriaInscricao
from .db_views import CadeirasSemestre, AlunosPorOrdemAlfabetica, Turnos, Cursos
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from bd2_projeto.services.mongo_service import (
    adicionar_log, listar_eventos_mongo, listar_logs, registar_auditoria_inscricao,
    validar_inscricao_disponivel, registar_consulta_aluno,
    registar_atividade_docente, registar_erro, registar_auditoria_user
)
from core.utils import registar_log, admin_required
import time


def index(request):
    return render(request, "di/index_di.html", {"area": "di"})

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # =========================
        # ADMIN (Django User)
        # =========================
        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("home:admin_dashboard")

            return redirect("home:index")

        # =========================
        #  ALUNO
        # =========================
        try:
            aluno = Aluno.objects.get(email=username_or_email)
            if aluno.password == password:
                request.session.flush()  # limpa tudo
                request.session["user_tipo"] = "aluno"
                request.session["user_id"] = aluno.n_mecanografico
                request.session["user_nome"] = aluno.nome
                request.session["user_email"] = aluno.email
                return redirect("home:index")
        except Aluno.DoesNotExist:
            pass

        # =========================
        # DOCENTE
        # =========================
        try:
            docente = Docente.objects.get(email=username_or_email)
            if docente.password == password:
                request.session.flush()
                request.session["user_tipo"] = "docente"
                request.session["user_id"] = docente.id_docente
                request.session["user_nome"] = docente.nome
                request.session["user_email"] = docente.email
                return redirect("home:index")
        except Docente.DoesNotExist:
            pass

        messages.error(request, "Utilizador ou palavra-passe incorretos.")
        return redirect("home:login")

    return render(request, "auth/login.html")


def do_logout(request):
    auth_logout(request)  # Logout do Django
    request.session.flush()  # Limpa as sessões personalizadas
    return redirect("home:login")  # Redireciona para a página de login


def ingresso(request):
    return render(request, "ei/ingresso.html", { "area": "ei" })


def plano_curricular(request):
    # ✅ Registar consulta em MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(
            request.session.get("user_id"),
            request.session.get("user_nome", "desconhecido"),
            "plano_curricular",
            {"curso": "EI"}
        )
    
    # Filtrar apenas UCs de Engenharia Informática (id_curso = 1)
    unidades = UnidadeCurricular.objects.filter(id_curso_id=1).select_related(
        'id_anocurricular', 'id_semestre'
    ).order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "ei/plano_curricular.html", {"plano": plano, "area": "ei"})

def horarios(request):
    # ✅ Registar consulta em MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(
            request.session.get("user_id"),
            request.session.get("user_nome", "desconhecido"),
            "horarios",
            {"curso": "EI"}
        )
    
    anos = AnoCurricular.objects.all().order_by("id_anocurricular")

    horarios_por_ano = []

    for ano in anos:
        pdf = (HorarioPDF.objects.filter(id_anocurricular=ano).order_by("-atualizado_em").first())

        horarios_por_ano.append({
            "ano": ano,
            "pdf": pdf
        })

    return render(request, "ei/horarios.html", {
        "horarios_por_ano": horarios_por_ano,
        "area": "ei"
    })

def avaliacoes(request):
    # ✅ Registar consulta em MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(
            request.session.get("user_id"),
            request.session.get("user_nome", "desconhecido"),
            "avaliacoes",
            {"curso": "EI"}
        )
    
    avaliacoes_docs = [
        {"ano": "1º Ano", "ficheiro": "avaliacoes_1ano.pdf"},
        {"ano": "2º Ano", "ficheiro": "avaliacoes_2ano.pdf"},
        {"ano": "3º Ano", "ficheiro": "avaliacoes_3ano.pdf"},
    ]
    return render(request, "ei/avaliacoes.html", {"avaliacoes_docs": avaliacoes_docs, "area": "ei"})

def contactos(request):
    # Buscar todos os docentes
    docentes = Docente.objects.all().order_by('nome')

    # Buscar dados do curso principal (por exemplo Engenharia Informática)
    curso = Curso.objects.filter(nome__icontains="Engenharia Informática").first()

    contexto = {
        "curso": curso,
        "docentes": docentes
    }
    return render(request, "ei/contactos.html", {"curso": curso, "docentes": docentes, "area": "ei"})


def inscricao_turno(request):
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)

    # Verificar se o aluno é de EI (id_curso = 1)
    if aluno.id_curso_id != 1:
        messages.error(request, "Esta página é apenas para alunos de Engenharia Informática.")
        if aluno.id_curso_id == 2:  # Se for TDM, redirecionar para a página correta
            return redirect("home:inscricao_turno_tdm")
        return redirect("home:index")

    inscricoes_turno = InscricaoTurno.objects.filter(n_mecanografico=aluno).values_list('id_turno_id', flat=True)
    turnos_inscritos = set(inscricoes_turno)

    inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True).values('id_unidadecurricular')

    lista_uc = []
    turnos_no_horario = []  # NOVA LISTA para o horário

    for inscricao in inscricoes:
        uc_id = inscricao['id_unidadecurricular']
        uc = UnidadeCurricular.objects.get(id_unidadecurricular=uc_id)

        relacoes = TurnoUc.objects.filter(id_unidadecurricular=uc)

        turnos = []
        for r in relacoes:
            turno = r.id_turno

            ocupados = InscricaoTurno.objects.filter(id_turno=turno).count()
            vagas = turno.capacidade - ocupados
            if vagas < 0:
                vagas = 0

            ja_inscrito = turno.id_turno in turnos_inscritos

            hora_inicio_str = r.hora_inicio.strftime("%H:%M")
            hora_fim_str = r.hora_fim.strftime("%H:%M")

            # Mapear dia da semana
            h_int = int(hora_inicio_str.split(":")[0])
            if 8 <= h_int < 10:
                dia_semana = "Segunda"
            elif 10 <= h_int < 12:
                dia_semana = "Terça"
            elif 12 <= h_int < 14:
                dia_semana = "Quarta"
            elif 14 <= h_int < 16:
                dia_semana = "Quinta"
            else:
                dia_semana = "Sexta"

            turno_info = {
                "id": turno.id_turno,
                "nome": f"T{turno.n_turno}",
                "tipo": turno.tipo,
                "capacidade": turno.capacidade,
                "vagas": vagas,
                "horario": f"{dia_semana} {hora_inicio_str}-{hora_fim_str}",
                "ja_inscrito": ja_inscrito,
                "dia": dia_semana,
                "hora_inicio": hora_inicio_str,
                "hora_fim": hora_fim_str,
            }
            
            turnos.append(turno_info)
            
            # Se o aluno está inscrito, adiciona à lista do horário
            if ja_inscrito:
                turnos_no_horario.append({
                    "uc_nome": uc.nome,
                    "turno_nome": f"T{turno.n_turno}",
                    "tipo": turno.tipo,
                    "dia": dia_semana,
                    "hora_inicio": hora_inicio_str,
                    "hora_fim": hora_fim_str,
                })

        lista_uc.append({
            "id": uc.id_unidadecurricular,
            "nome": uc.nome,
            "turnos": turnos,
        })

    horas = [
        "08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30",
        "12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30",
        "16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30",
        "20:00","20:30","21:00","21:30","22:00","22:30","23:00","23:30"
    ]

    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    return render(request, "ei/inscricao_turno.html", {
        "unidades": lista_uc,
        "horas": horas,
        "dias": dias,
        "turnos_horario": turnos_no_horario,  # PASSA OS TURNOS INSCRITOS
        "area": "ei"
    })

def informacoes(request):
    return render(request, "ei/informacoes.html", { "area": "ei" })

def perfil(request):
    user_tipo = request.session.get("user_tipo")
    user_id = request.session.get("user_id")
    
    context = {}

    if user_tipo == "aluno":
        aluno = get_object_or_404(Aluno, n_mecanografico=user_id)
        context["user_obj"] = aluno
        context["tipo"] = "Aluno"
        
        # Turnos inscritos
        inscricoes = InscricaoTurno.objects.filter(n_mecanografico=aluno).select_related('id_turno', 'id_unidadecurricular')
        
        turnos_info = []
        for inscricao in inscricoes:
            turno = inscricao.id_turno
            uc = inscricao.id_unidadecurricular
            
            # Tenta pegar info extra de horário (TurnoUc)
            # Usamos filter().first() porque a tabela pode ter múltiplas entradas para o mesmo id_turno (modelo incorreto?)
            # e porque queremos o horário deste turno NESTA disciplina específica.
            turno_uc = TurnoUc.objects.filter(id_turno=turno, id_unidadecurricular=uc).first()
            
            if turno_uc:
                hora_inicio = turno_uc.hora_inicio.strftime("%H:%M")
                hora_fim = turno_uc.hora_fim.strftime("%H:%M")
                
                # Lógica de dia da semana
                try:
                    h_int = int(hora_inicio.split(":")[0])
                    if 8 <= h_int < 10:
                        dia_semana = "Segunda"
                    elif 10 <= h_int < 12:
                        dia_semana = "Terça"
                    elif 12 <= h_int < 14:
                        dia_semana = "Quarta"
                    elif 14 <= h_int < 16:
                        dia_semana = "Quinta"
                    else:
                        dia_semana = "Sexta"
                except:
                    dia_semana = "?"
            else:
                hora_inicio = "?"
                hora_fim = "?"
                dia_semana = "?"
            
            turnos_info.append({
                "uc": uc.nome,
                "turno": f"T{turno.n_turno}",
                "tipo": turno.tipo,
                "horario": f"{dia_semana}, {hora_inicio} - {hora_fim}"
            })
            
        context["turnos"] = turnos_info

    elif user_tipo == "docente":
        docente = get_object_or_404(Docente, id_docente=user_id)
        context["user_obj"] = docente
        context["tipo"] = "Docente"

    return render(request, "profile/perfil.html", context)

def inscrever_turno(request, turno_id, uc_id):
    """
    Inscreve aluno em turno com auditoria em PostgreSQL e MongoDB
    """
    inicio_tempo = time.time()
    resultado = None
    motivo = None
    
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        mensagem_erro = "Apenas alunos se podem inscrever em turnos."
        messages.error(request, mensagem_erro)
        registar_erro("inscrever_turno", mensagem_erro)
        return redirect("home:login")

    try:
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        
        # Verificar se o aluno é de EI (id_curso = 1)
        if aluno.id_curso_id != 1:
            messages.error(request, "Esta funcionalidade é apenas para alunos de Engenharia Informática.")
            return redirect("home:index")
        
        turno_uc = get_object_or_404(Turno, id_turno=turno_id)
        uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=uc_id)

        # ✅ Validar se turno pertence à UC
        turno_uc_existe = TurnoUc.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).exists()
        if not turno_uc_existe:
            resultado = "nao_autorizado"
            motivo = "Este turno não pertence a esta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(
                aluno.n_mecanografico, turno_id, uc_id, uc.nome, 
                resultado, motivo, tempo_ms
            )
            return redirect("home:inscricao_turno")

        # ✅ Validar se está inscrito na UC
        inscrito = InscritoUc.objects.filter(n_mecanografico=aluno, id_unidadecurricular=uc, estado=True).exists()
        if not inscrito:
            resultado = "nao_autorizado"
            motivo = "Não estás inscrito nesta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(
                aluno.n_mecanografico, turno_id, uc_id, uc.nome, 
                resultado, motivo, tempo_ms
            )
            return redirect("home:inscricao_turno")
        
        # ✅ Validar se já está inscrito neste turno (em MongoDB)
        pode_inscrever, msg_validacao = validar_inscricao_disponivel(
            aluno.n_mecanografico, turno_id
        )
        if not pode_inscrever:
            resultado = "uc_duplicada"
            motivo = msg_validacao
            messages.warning(request, "Já estás inscrito neste turno.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(
                aluno.n_mecanografico, turno_id, uc_id, uc.nome, 
                resultado, motivo, tempo_ms
            )
            return redirect("home:inscricao_turno")

        # ✅ Validar capacidade do turno
        ocupados = InscricaoTurno.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).count()
        if ocupados >= turno_uc.capacidade:
            resultado = "turno_cheio"
            motivo = f"Turno cheio (capacidade: {turno_uc.capacidade}, ocupado: {ocupados})"
            messages.error(request, "Este turno já está cheio.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(
                aluno.n_mecanografico, turno_id, uc_id, uc.nome, 
                resultado, motivo, tempo_ms
            )
            return redirect("home:inscricao_turno")

        # ✅ INSCRIÇÃO BEM-SUCEDIDA
        inscricao = InscricaoTurno.objects.create(
            n_mecanografico=aluno, 
            id_turno=turno_uc, 
            id_unidadecurricular=uc, 
            data_inscricao=datetime.today().date()
        )

        # ✅ REGISTAR AUDITORIA (PostgreSQL)
        tempo_ms = int((time.time() - inicio_tempo) * 1000)
        auditoria_pg = AuditoriaInscricao.objects.create(
            n_mecanografico=aluno,
            id_turno=turno_uc,
            id_unidadecurricular=uc,
            resultado='sucesso',
            tempo_processamento_ms=tempo_ms
        )

        # ✅ REGISTAR AUDITORIA (MongoDB)
        registar_auditoria_inscricao(
            aluno.n_mecanografico, turno_id, uc_id, uc.nome, 
            'sucesso', None, tempo_ms
        )

        # ✅ REGISTAR LOG COM CONTEXTO
        adicionar_log(
            "inscricao_turno_sucesso",
            {
                "aluno": aluno.nome,
                "uc": uc.nome,
                "turno": turno_id,
                "tempo_ms": tempo_ms
            },
            request
        )

        messages.success(request, "Inscrição no turno efetuada com sucesso!")
        return redirect("home:inscricao_turno")
        
    except Exception as e:
        resultado = "erro_sistema"
        motivo = str(e)
        tempo_ms = int((time.time() - inicio_tempo) * 1000)
        registar_erro("inscrever_turno", str(e), {"turno_id": turno_id, "uc_id": uc_id})
        registar_auditoria_inscricao(
            request.session.get("user_id"), turno_id, uc_id, "desconhecido", 
            resultado, motivo, tempo_ms
        )
        messages.error(request, "Erro ao processar inscrição. Tente novamente.")
        return redirect("home:inscricao_turno")


def desinscrever_turno(request, turno_id, uc_id):
    """
    Remove aluno de inscrição em turno
    """
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        return JsonResponse({"erro": "Acesso não autorizado"}, status=403)

    try:
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        turno_uc = get_object_or_404(Turno, id_turno=turno_id)
        uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=uc_id)

        # Remover inscrição (tenta com UC e, se não encontrar, remove apenas pelo turno)
        qs = InscricaoTurno.objects.filter(
            n_mecanografico=aluno,
            id_turno=turno_uc,
            id_unidadecurricular=uc
        )

        removidas = qs.delete()[0]

        # Fallback: caso algum registo tenha ficado sem UC associada (dados antigos)
        if removidas == 0:
            removidas = InscricaoTurno.objects.filter(
                n_mecanografico=aluno,
                id_turno=turno_uc
            ).delete()[0]

        if removidas > 0:
            registar_auditoria_inscricao(
                aluno.n_mecanografico, turno_id, uc_id, uc.nome,
                'desinscrever', None, 0
            )
            # Logar quantidade removida para diagnóstico
            adicionar_log(
                "desinscrever_turno",
                {
                    "aluno": aluno.n_mecanografico,
                    "turno": turno_id,
                    "uc": uc_id,
                    "registos_removidos": removidas,
                },
                request
            )
            messages.success(request, f"Desinscrição em {uc.nome} — {turno_uc.tipo} efetuada!")
        else:
            messages.warning(request, "Inscrição não encontrada.")

        return redirect("home:inscricao_turno")

    except Exception as e:
        registar_erro("desinscrever_turno", str(e), {"turno_id": turno_id, "uc_id": uc_id})
        messages.error(request, "Erro ao remover inscrição.")
        return redirect("home:inscricao_turno")


def api_verificar_conflitos(request, turno_id):
    """
    API para verificar conflitos de horário antes de inscrever
    Retorna lista de UCs com conflito se houver
    """
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        return JsonResponse({"erro": "Não autorizado"}, status=403)

    try:
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        turno_novo = get_object_or_404(Turno, id_turno=turno_id)

        # Pegar os horários do turno novo (pode haver múltiplas associações com UCs diferentes)
        turnos_uc_novo = TurnoUc.objects.filter(id_turno=turno_novo)
        if not turnos_uc_novo.exists():
            return JsonResponse({"conflitos": []})

        # Pegar todas as inscrições do aluno com os horários associados
        inscricoes = InscricaoTurno.objects.filter(
            n_mecanografico=aluno
        ).select_related('id_turno', 'id_unidadecurricular')

        conflitos = []
        
        # Para cada turno novo que será inscrito
        for turno_uc_novo in turnos_uc_novo:
            hora_inicio_novo = turno_uc_novo.hora_inicio
            hora_fim_novo = turno_uc_novo.hora_fim
            dia_novo = getattr(turno_uc_novo, "dia", None)

            # Verificar com todas as inscrições existentes
            for insc in inscricoes:
                turno_uc_existente = TurnoUc.objects.filter(
                    id_turno=insc.id_turno
                ).first()

                if turno_uc_existente:
                    hora_inicio_existente = turno_uc_existente.hora_inicio
                    hora_fim_existente = turno_uc_existente.hora_fim
                    dia_existente = getattr(turno_uc_existente, "dia", None)

                    # Se ambos têm dia e são diferentes, não há conflito
                    if dia_novo and dia_existente and dia_novo != dia_existente:
                        continue

                    # Verificar sobreposição temporal
                    if (hora_inicio_novo < hora_fim_existente and hora_fim_novo > hora_inicio_existente):
                        conflitos.append({
                            "uc": insc.id_unidadecurricular.nome,
                            "turno": insc.id_turno.tipo,
                            "horario": f"{hora_inicio_existente.strftime('%H:%M')} - {hora_fim_existente.strftime('%H:%M')}"
                        })

        # Remover duplicatas mantendo ordem
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


def cadeiras_semestre(request):
    data = list(
        CadeirasSemestre.objects
        .order_by('semestre_id', 'nome')
        .values('id_unidadecurricular', 'nome', 'ects', 'semestre_id', 'semestre_nome')
    )
    return JsonResponse(data, safe=False)

def alunos_por_ordem_alfabetica(request):
    data = list(
        AlunosPorOrdemAlfabetica.objects
        .order_by('nome')
        .values('n_mecanografico', 'nome', 'email', 'id_anocurricular')
    )
    return JsonResponse(data, safe=False)

def turnos_list(request):
    data = list(
        Turnos.objects
        .order_by('id_turno')
        .values('id_turno', 'n_turno', 'capacidade', 'tipo')
    )
    return JsonResponse(data, safe=False)

def cursos_list(request):
    data = list(
        Cursos.objects
        .order_by('id_curso')
        .values('id_curso', 'nome', 'grau')
    )
    return JsonResponse(data, safe=False)

# Dashboard
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_turnos = Turnos.objects.count()
    total_ucs = UnidadeCurricular.objects.count()
    total_cursos = Curso.objects.count()
    total_horarios = HorarioPDF.objects.count()
    total_avaliacoes = AvaliacaoPDF.objects.count()

    # Dados para o gráfico de alunos por UC
    from django.db.models import Count
    alunos_por_uc = InscritoUc.objects.values(
        'id_unidadecurricular__nome'
    ).annotate(
        total=Count('n_mecanografico')
    ).order_by('-total')[:10]  # Top 10 UCs
    
    chart_alunos_labels = json.dumps([item['id_unidadecurricular__nome'] for item in alunos_por_uc])
    chart_alunos_values = json.dumps([item['total'] for item in alunos_por_uc])

    # Dados para o gráfico de turnos disponíveis vs ocupados
    total_vagas = Turno.objects.aggregate(total=models.Sum('capacidade'))['total'] or 0
    vagas_ocupadas = InscricaoTurno.objects.count()
    vagas_disponiveis = total_vagas - vagas_ocupadas

    return render(request, "admin/dashboard.html", {
        "total_users": total_users,
        "total_turnos": total_turnos,
        "total_ucs": total_ucs,
        "total_cursos": total_cursos,
        "total_horarios": total_horarios,
        "total_avaliacoes": total_avaliacoes,
        "chart_alunos_labels": chart_alunos_labels,
        "chart_alunos_values": chart_alunos_values,
        "vagas_ocupadas": vagas_ocupadas,
        "vagas_disponiveis": vagas_disponiveis,
    })

def admin_users_list(request):
    # Combinar todos os tipos de utilizadores
    django_users = User.objects.all().values('id', 'username', 'email', 'date_joined', 'is_active', 'is_staff').annotate(tipo=models.Value('Admin', output_field=models.CharField()))
    alunos = Aluno.objects.all().values('n_mecanografico', 'nome', 'email').annotate(
        id=models.F('n_mecanografico'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Aluno', output_field=models.CharField())
    )
    docentes = Docente.objects.all().values('id_docente', 'nome', 'email').annotate(
        id=models.F('id_docente'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Docente', output_field=models.CharField())
    )
    
    users = list(django_users) + list(alunos) + list(docentes)
    users_sorted = sorted(users, key=lambda x: x.get('id', 0))
    
    return render(request, "admin/users_list.html", {"users": users_sorted})

def admin_users_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username e password são obrigatórios.")
            django_users = User.objects.all().values('id', 'username', 'email', 'date_joined', 'is_active', 'is_staff').annotate(tipo=models.Value('Admin', output_field=models.CharField()))
            alunos = Aluno.objects.all().values('n_mecanografico', 'nome', 'email').annotate(
                id=models.F('n_mecanografico'),
                username=models.F('nome'),
                date_joined=models.Value(None, output_field=models.DateTimeField()),
                is_active=models.Value(True, output_field=models.BooleanField()),
                is_staff=models.Value(False, output_field=models.BooleanField()),
                tipo=models.Value('Aluno', output_field=models.CharField())
            )
            docentes = Docente.objects.all().values('id_docente', 'nome', 'email').annotate(
                id=models.F('id_docente'),
                username=models.F('nome'),
                date_joined=models.Value(None, output_field=models.DateTimeField()),
                is_active=models.Value(True, output_field=models.BooleanField()),
                is_staff=models.Value(False, output_field=models.BooleanField()),
                tipo=models.Value('Docente', output_field=models.CharField())
            )
            users = list(django_users) + list(alunos) + list(docentes)
            users_sorted = sorted(users, key=lambda x: x.get('id', 0))
            return render(request, "admin/users_form.html", {"users": users_sorted})

        User.objects.create_user(username=username, email=email, password=password)
        
        # Obter o user criado para registar o ID
        novo_user = User.objects.get(username=username)
        
        # Registar em PostgreSQL
        registar_log(
            request, 
            operacao="CREATE", 
            entidade="user_admin", 
            chave=str(novo_user.id), 
            detalhes=f"Novo utilizador criado: {username} ({email})"
        )
        
        # Registar em MongoDB
        registar_auditoria_user(
            "CREATE", 
            novo_user.id, 
            "Admin",
            {"username": username, "email": email},
            request
        )
        
        messages.success(request, "Utilizador criado com sucesso!")
        return redirect("home:admin_users_list")

    django_users = User.objects.all().values('id', 'username', 'email', 'date_joined', 'is_active', 'is_staff').annotate(tipo=models.Value('Admin', output_field=models.CharField()))
    alunos = Aluno.objects.all().values('n_mecanografico', 'nome', 'email').annotate(
        id=models.F('n_mecanografico'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Aluno', output_field=models.CharField())
    )
    docentes = Docente.objects.all().values('id_docente', 'nome', 'email').annotate(
        id=models.F('id_docente'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Docente', output_field=models.CharField())
    )
    users = list(django_users) + list(alunos) + list(docentes)
    users_sorted = sorted(users, key=lambda x: x.get('id', 0))
    return render(request, "admin/users_form.html", {"users": users_sorted})

def admin_users_edit(request, id):
    # Tentar encontrar em Django User
    user = None
    user_type = None
    
    try:
        user = User.objects.get(id=id)
        user_type = "Admin"
    except User.DoesNotExist:
        pass
    
    # Tentar encontrar em Aluno
    if not user:
        try:
            user = Aluno.objects.get(n_mecanografico=id)
            user_type = "Aluno"
        except Aluno.DoesNotExist:
            pass
    
    # Tentar encontrar em Docente
    if not user:
        try:
            user = Docente.objects.get(id_docente=id)
            user_type = "Docente"
        except Docente.DoesNotExist:
            pass
    
    if not user:
        return redirect("admin_users_list")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        
        # Guardar dados antigos para auditoria
        old_data = {
            'username': user.username if user_type == "Admin" else user.nome,
            'email': user.email
        }
        
        if user_type == "Admin":
            user.username = username
            user.email = email
            user.save()
        elif user_type == "Aluno":
            user.nome = username
            user.email = email
            user.save()
        elif user_type == "Docente":
            user.nome = username
            user.email = email
            user.save()
        
        # Registar mudanças em PostgreSQL
        registar_log(
            request, 
            operacao="UPDATE", 
            entidade=f"user_{user_type.lower()}", 
            chave=str(id), 
            detalhes=f"Campos alterados: username={username}, email={email}"
        )
        
        # Registar em MongoDB
        registar_auditoria_user(
            "UPDATE", 
            id, 
            user_type,
            {
                "username": username,
                "email": email,
                "alterado_de": old_data
            },
            request
        )
        
        messages.success(request, "Utilizador atualizado com sucesso!")
        return redirect("home:admin_users_list")

    # Preparar dados para o template
    user_data = {
        'id': user.id if user_type == "Admin" else (user.n_mecanografico if user_type == "Aluno" else user.id_docente),
        'username': user.username if user_type == "Admin" else user.nome,
        'email': user.email,
        'tipo': user_type
    }
    
    django_users = User.objects.all().values('id', 'username', 'email', 'date_joined', 'is_active', 'is_staff').annotate(tipo=models.Value('Admin', output_field=models.CharField()))
    alunos = Aluno.objects.all().values('n_mecanografico', 'nome', 'email').annotate(
        id=models.F('n_mecanografico'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Aluno', output_field=models.CharField())
    )
    docentes = Docente.objects.all().values('id_docente', 'nome', 'email').annotate(
        id=models.F('id_docente'),
        username=models.F('nome'),
        date_joined=models.Value(None, output_field=models.DateTimeField()),
        is_active=models.Value(True, output_field=models.BooleanField()),
        is_staff=models.Value(False, output_field=models.BooleanField()),
        tipo=models.Value('Docente', output_field=models.CharField())
    )
    users = list(django_users) + list(alunos) + list(docentes)
    users_sorted = sorted(users, key=lambda x: x.get('id', 0))
    
    return render(request, "admin/users_form.html", {"user": user_data, "users": users_sorted})

def admin_users_delete(request, id):
    # Tentar encontrar em Django User
    user = None
    user_type = None
    username = None
    
    try:
        user = User.objects.get(id=id)
        user_type = "Admin"
        username = user.username
    except User.DoesNotExist:
        pass
    
    # Tentar encontrar em Aluno
    if not user:
        try:
            user = Aluno.objects.get(n_mecanografico=id)
            user_type = "Aluno"
            username = user.nome
            
            # Limpar matrículas (foreign key constraint)
            from .models import Matricula
            matriculas = Matricula.objects.filter(n_mecanografico=user)
            total_matriculas = matriculas.count()
            matriculas.delete()
            
            # Limpar inscrições em turnos (libera vagas)
            inscricoes_turno = InscricaoTurno.objects.filter(n_mecanografico=user)
            total_inscricoes = inscricoes_turno.count()
            inscricoes_turno.delete()
            
            # Limpar inscrições em UCs
            inscricoes_uc = InscritoUc.objects.filter(n_mecanografico=user)
            total_ucs = inscricoes_uc.count()
            inscricoes_uc.delete()
            
            # Limpar auditorias relacionadas (opcional - para não perder histórico, comentar estas linhas)
            # AuditoriaInscricao.objects.filter(n_mecanografico=user).delete()
            
            messages.info(request, f"Removidas {total_matriculas} matrículas, {total_inscricoes} inscrições em turnos e {total_ucs} inscrições em UCs.")
            
        except Aluno.DoesNotExist:
            pass
    
    # Tentar encontrar em Docente
    if not user:
        try:
            user = Docente.objects.get(id_docente=id)
            user_type = "Docente"
            username = user.nome
            
            # Limpar associações de docente com UCs
            from .models import LecionaUc
            leciona = LecionaUc.objects.filter(id_docente=user)
            total_ucs = leciona.count()
            leciona.delete()
            
            messages.info(request, f"Removidas {total_ucs} associações com UCs.")
            
        except Docente.DoesNotExist:
            pass
    
    if not user:
        messages.error(request, "Utilizador não encontrado.")
        return redirect("home:admin_users_list")
    
    # Registar antes de apagar em PostgreSQL
    registar_log(
        request, 
        operacao="DELETE", 
        entidade=f"user_{user_type.lower()}", 
        chave=str(id), 
        detalhes=f"Utilizador apagado: {username} (Tipo: {user_type})"
    )
    
    # Registar em MongoDB
    registar_auditoria_user(
        "DELETE", 
        id, 
        user_type,
        {
            "username": username, 
            "email": user.email,
            "tipo": user_type
        },
        request
    )
    
    # Apagar o utilizador
    user.delete()
    
    messages.success(request, f"{user_type} '{username}' apagado com sucesso!")
    return redirect("home:admin_users_list")

# ==========================
# ADMIN — TURNOS CRUD
# ==========================

def admin_turnos_list(request):
    turnos = Turnos.objects.all().order_by("id_turno")
    return render(request, "admin/turnos_list.html", {"turnos": turnos})

def admin_turnos_create(request):
    if request.method == "POST":
        n_turno = request.POST.get("n_turno")
        capacidade = request.POST.get("capacidade")
        tipo = request.POST.get("tipo")

        turno = Turnos.objects.create(
            n_turno=n_turno,
            capacidade=capacidade,
            tipo=tipo,
        )

        registar_log(request, operacao="CREATE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno criado: {turno.tipo} (nº {turno.n_turno})")
        messages.success(request, "Turno criado com sucesso!")
        return redirect("home:admin_turnos_list")

    return render(request, "admin/turnos_form.html")

def admin_turnos_edit(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)

    if request.method == "POST":
        turno.n_turno = request.POST.get("n_turno")
        turno.capacidade = request.POST.get("capacidade")
        turno.tipo = request.POST.get("tipo")
        turno.save()

        registar_log(request, operacao="UPDATE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno atualizado: {turno.tipo} (nº {turno.n_turno})")

        messages.success(request, "Turno atualizado!")
        return redirect("admin_turnos_list")

    return render(request, "admin/turnos_form.html", {"turno": turno})

def admin_turnos_delete(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)
    turno.delete()
    registar_log(request, operacao="DELETE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno apagado: {turno.tipo} (nº {turno.n_turno})")
    messages.success(request, "Turno apagado!")
    return redirect("admin_turnos_list")

# ==========================
# ADMIN — HORÁRIOS CRUD
# ==========================

def admin_horarios_create(request):
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        ficheiro = request.FILES.get("ficheiro")
        curso_id = request.POST.get("id_curso")
        ano_id = request.POST.get("id_anocurricular")

        if not ficheiro:
            messages.error(request, "É necessário enviar um ficheiro PDF.")
            return redirect("home:admin_horarios_create")
        
        if not curso_id or not ano_id:
            messages.error(request, "É necessário selecionar o curso e o ano curricular.")
            return redirect("home:admin_horarios_create")

        HorarioPDF.objects.create(
            nome=nome,
            ficheiro=ficheiro,
            id_anocurricular_id=ano_id
        )

        messages.success(request, "Horário carregado com sucesso!")
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html", {
        'cursos': cursos,
        'anos_curriculares': anos_curriculares
    })

def admin_horarios_edit(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')

    if request.method == "POST":
        horario.nome = request.POST.get("nome")
        curso_id = request.POST.get("id_curso")
        ano_id = request.POST.get("id_anocurricular")
        
        if ano_id:
            horario.id_anocurricular_id = ano_id

        if "ficheiro" in request.FILES:
            horario.ficheiro = request.FILES["ficheiro"]

        horario.save()
        messages.success(request, "Horário atualizado!")
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html", {
        "horario": horario,
        'cursos': cursos,
        'anos_curriculares': anos_curriculares
    })

def admin_horarios_delete(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)
    horario.delete()
    messages.success(request, "Horário apagado!")
    return redirect("home:admin_horarios_list")

def admin_horarios_list(request):
    horarios = HorarioPDF.objects.all().order_by("-atualizado_em")
    return render(request, "admin/horarios_list.html", {"horarios": horarios})

def horarios_admin(request):
    pdf = HorarioPDF.objects.order_by("-atualizado_em").first()
    return render(request, "home/horarios.html", {"pdf": pdf})


# ==========================
# AVALIACOES ADMIN (GESTÃO DE PDFs)
# ==========================

@admin_required
def admin_avaliacoes_list(request):
    avaliacoes = AvaliacaoPDF.objects.all().order_by("-atualizado_em")
    return render(request, "admin/avaliacoes_list.html", {"avaliacoes": avaliacoes})

@admin_required
def admin_avaliacoes_create(request):
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')

    if request.method == "POST":
        nome = request.POST.get("nome")
        ficheiro = request.FILES.get("ficheiro")
        ano_id = request.POST.get("id_anocurricular")

        if not ficheiro:
            messages.error(request, "É necessário enviar um ficheiro PDF.")
            return redirect("home:admin_avaliacoes_create")
        
        if not ano_id:
            messages.error(request, "É necessário selecionar o ano curricular.")
            return redirect("home:admin_avaliacoes_create")

        AvaliacaoPDF.objects.create(
            nome=nome,
            ficheiro=ficheiro,
            id_anocurricular_id=ano_id
        )

        registar_log(request, operacao="CREATE", entidade="avaliacao_pdf", chave="novo", detalhes=f"Avaliação PDF criada: {nome}")
        messages.success(request, "Calendário de avaliações carregado com sucesso!")
        return redirect("home:admin_avaliacoes_list")

    return render(request, "admin/avaliacoes_form.html", {
        'cursos': cursos,
        'anos_curriculares': anos_curriculares
    })

@admin_required
def admin_avaliacoes_edit(request, id):
    avaliacao = get_object_or_404(AvaliacaoPDF, id=id)
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')

    if request.method == "POST":
        avaliacao.nome = request.POST.get("nome")
        ano_id = request.POST.get("id_anocurricular")
        
        if ano_id:
            avaliacao.id_anocurricular_id = ano_id

        if "ficheiro" in request.FILES:
            avaliacao.ficheiro = request.FILES["ficheiro"]

        avaliacao.save()
        registar_log(request, operacao="UPDATE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF atualizada: {avaliacao.nome}")
        messages.success(request, "Calendário de avaliações atualizado!")
        return redirect("home:admin_avaliacoes_list")

    return render(request, "admin/avaliacoes_form.html", {
        "avaliacao": avaliacao,
        'cursos': cursos,
        'anos_curriculares': anos_curriculares
    })

@admin_required
def admin_avaliacoes_delete(request, id):
    avaliacao = get_object_or_404(AvaliacaoPDF, id=id)
    nome = avaliacao.nome
    avaliacao.delete()
    registar_log(request, operacao="DELETE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF apagada: {nome}")
    messages.success(request, "Calendário de avaliações apagado!")
    return redirect("home:admin_avaliacoes_list")


def admin_users_docentes(request):
    docentes = Docente.objects.all().order_by("id_docente")
    return render(request, "admin/users_filter.html", {
        "titulo": "Docentes",
        "users": docentes
    })

def admin_users_alunos(request):
    alunos = Aluno.objects.all().order_by("n_mecanografico")
    return render(request, "admin/users_filter.html", {
        "titulo": "Alunos",
        "users": alunos
    })

def testar_mongo(request):
    # Adicionar um log no MongoDB
    adicionar_log("teste_ligacao", {"user": "teste_django"})

    # Ler todos os logs existentes
    logs = listar_logs()

    return JsonResponse({"estado": "ok", "logs": logs})

def admin_horarios_delete(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)
    horario.delete()
    messages.success(request, "Horário apagado!")
    return redirect("home:admin_horarios_list")

# NOVA VIEW PARA TESTAR MONGO
def testar_mongo(request):
    adicionar_log("teste_ligacao", {"user": "teste_django"})
    logs = listar_logs()
    return JsonResponse({"estado": "ok", "logs": logs})


#DEPARTAMENTO INFORMATICA
def index_di(request):
    return render(request, "di/index_di.html", { "area": "di" })

def recursos_di(request):
    return render(request, "di/recursos.html", { "area": "di" })

def sobre_di(request):
    return render(request, "di/sobre.html", { "area": "di" })

def contacto_di(request):
    # Listar docentes para a página do Departamento
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "di/contactos.html", { "area": "di", "docentes": docentes })


#ENG INFORMATICA
def index_ei(request):
    return render(request, "ei/index.html", { "area": "ei" })

# ADMIN – ENGENHARIA INFORMÁTICA
def admin_ei_ingresso(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Ingresso"})

def admin_ei_saidas(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Saídas"})

def admin_ei_plano(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Plano Curricular"})

def admin_ei_horarios(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Horários"})

def admin_ei_avaliacoes(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Avaliações"})

def admin_ei_contactos(request):
    return render(request, "admin/placeholder.html", {"titulo": "EI — Contactos"})




#TDM
def index_tdm(request):
    return render(request, "tdm/index_tdm.html", { "area": "tdm" })

def ingresso_tdm(request):
    return render(request, "tdm/ingresso_tdm.html", { "area": "tdm" })

def plano_tdm(request):
    # Filtrar apenas UCs de Tecnologia e Design Multimedia (id_curso = 2)
    unidades = UnidadeCurricular.objects.filter(id_curso_id=2).select_related(
        'id_anocurricular', 'id_semestre'
    ).order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "tdm/plano_tdm.html", {"plano": plano, "area": "tdm"})

def horarios_tdm(request):
    anos = AnoCurricular.objects.all().order_by("id_anocurricular")

    horarios_por_ano = []

    for ano in anos:
        pdf = (HorarioPDF.objects.filter(id_anocurricular=ano).order_by("-atualizado_em").first())

        horarios_por_ano.append({
            "ano": ano,
            "pdf": pdf
        })

    return render(request, "tdm/horarios_tdm.html", {
        "horarios_por_ano": horarios_por_ano,
        "area": "tdm"
    })

def contactos_tdm(request):
    # Reutiliza a lista de docentes (igual a EI)
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "tdm/contactos_tdm.html", { "area": "tdm", "docentes": docentes })

def saidas_tdm(request):
    return render(request, "tdm/saidas.html", { "area": "tdm" })

def avaliacoes_tdm(request):
    return render(request, "tdm/avaliacoes_tdm.html", { "area": "tdm" })

def moodle(request):
    return render(request, "tdm/moodle.html", { "area": "tdm" })

def inscricao_turno_tdm(request):
    """
    Sistema de inscrição específico para TDM:
    Alunos escolhem APENAS Turno 1 ou Turno 2, aplicando a TODAS as UCs do semestre
    """
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)
    
    # Verificar se o aluno é de TDM (id_curso = 2)
    if aluno.id_curso_id != 2:
        messages.error(request, "Esta página é apenas para alunos de Tecnologia e Design Multimédia.")
        if aluno.id_curso_id == 1:  # Se for EI, redirecionar para a página correta
            return redirect("home:inscricao_turno")
        return redirect("home:index")
    
    # Verificar se o aluno já escolheu um turno
    inscricoes_existentes = InscricaoTurno.objects.filter(n_mecanografico=aluno)
    turno_escolhido = None
    
    if inscricoes_existentes.exists():
        # Pega o primeiro turno inscrito para saber qual foi a escolha (T1 ou T2)
        primeira_inscricao = inscricoes_existentes.first()
        turno_escolhido = primeira_inscricao.id_turno.n_turno if primeira_inscricao.id_turno else None
    
    # Buscar as UCs em que o aluno está inscrito
    inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True).select_related('id_unidadecurricular')
    ucs_inscritas = [i.id_unidadecurricular for i in inscricoes]
    
    # Buscar informações dos turnos disponíveis (T1 e T2)
    turnos_info = {
        1: {"nome": "Turno 1", "ucs": []},
        2: {"nome": "Turno 2", "ucs": []}
    }
    
    for uc in ucs_inscritas:
        # Buscar turnos T1 e T2 desta UC
        turnos_uc = TurnoUc.objects.filter(
            id_unidadecurricular=uc
        ).select_related('id_turno')
        
        for turno_rel in turnos_uc:
            turno = turno_rel.id_turno
            n_turno = turno.n_turno
            
            if n_turno in [1, 2]:
                # Calcular vagas
                ocupados = InscricaoTurno.objects.filter(
                    id_turno=turno,
                    id_unidadecurricular=uc
                ).count()
                vagas = turno.capacidade - ocupados
                if vagas < 0:
                    vagas = 0
                
                # Mapear dia da semana baseado na hora
                hora_inicio_str = turno_rel.hora_inicio.strftime("%H:%M")
                h_int = int(hora_inicio_str.split(":")[0])
                
                if 8 <= h_int < 10:
                    dia_semana = "Segunda"
                elif 10 <= h_int < 12:
                    dia_semana = "Terça"
                elif 12 <= h_int < 14:
                    dia_semana = "Quarta"
                elif 14 <= h_int < 16:
                    dia_semana = "Quinta"
                else:
                    dia_semana = "Sexta"
                
                turnos_info[n_turno]["ucs"].append({
                    "nome": uc.nome,
                    "horario": f"{dia_semana} {turno_rel.hora_inicio.strftime('%H:%M')}-{turno_rel.hora_fim.strftime('%H:%M')}",
                    "vagas": vagas,
                    "capacidade": turno.capacidade
                })
    
    return render(request, "tdm/inscricao_turno_tdm.html", {
        "turnos_info": turnos_info,
        "turno_escolhido": turno_escolhido,
        "area": "tdm"
    })

def inscrever_turno_tdm(request, n_turno):
    """
    Inscreve aluno TDM em TODAS as UCs do semestre no turno escolhido (1 ou 2)
    """
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "Apenas alunos podem inscrever-se em turnos.")
        return redirect("home:login")
    
    inicio_tempo = time.time()
    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)
    
    # Verificar se o aluno é de TDM (id_curso = 2)
    if aluno.id_curso_id != 2:
        messages.error(request, "Esta funcionalidade é apenas para alunos de TDM.")
        return redirect("home:index")
    
    try:
        # Verificar se já tem inscrições
        inscricoes_existentes = InscricaoTurno.objects.filter(n_mecanografico=aluno)
        if inscricoes_existentes.exists():
            messages.warning(request, "Já tens um turno escolhido. Para mudar, contacta a coordenação.")
            return redirect("home:inscricao_turno_tdm")
        
        # Buscar todas as UCs em que o aluno está inscrito
        inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True)
        
        inscricoes_realizadas = 0
        erros = []
        
        for inscricao in inscricoes:
            uc = inscricao.id_unidadecurricular
            
            # Buscar o turno específico (T1 ou T2) para esta UC
            try:
                turno_uc_rel = TurnoUc.objects.filter(
                    id_unidadecurricular=uc,
                    id_turno__n_turno=n_turno
                ).select_related('id_turno').first()
                
                if not turno_uc_rel:
                    erros.append(f"{uc.nome}: Turno {n_turno} não disponível")
                    continue
                
                turno = turno_uc_rel.id_turno
                
                # Verificar capacidade
                ocupados = InscricaoTurno.objects.filter(
                    id_turno=turno,
                    id_unidadecurricular=uc
                ).count()
                
                if ocupados >= turno.capacidade:
                    erros.append(f"{uc.nome}: Turno {n_turno} cheio")
                    continue
                
                # Criar inscrição
                InscricaoTurno.objects.create(
                    n_mecanografico=aluno,
                    id_turno=turno,
                    id_unidadecurricular=uc,
                    data_inscricao=datetime.today().date()
                )
                
                # Registar auditoria
                tempo_ms = int((time.time() - inicio_tempo) * 1000)
                registar_auditoria_inscricao(
                    aluno.n_mecanografico,
                    turno.id_turno,
                    uc.id_unidadecurricular,
                    uc.nome,
                    'sucesso',
                    f'Inscrição TDM - Turno {n_turno}',
                    tempo_ms
                )
                
                inscricoes_realizadas += 1
                
            except Exception as e:
                erros.append(f"{uc.nome}: {str(e)}")
        
        # Mensagens de feedback
        if inscricoes_realizadas > 0:
            messages.success(request, f"✓ Inscrito no Turno {n_turno} em {inscricoes_realizadas} UC(s)!")
            
            # Registar log
            adicionar_log(
                "inscricao_turno_tdm_sucesso",
                {
                    "aluno": aluno.nome,
                    "turno": n_turno,
                    "ucs_inscritas": inscricoes_realizadas
                },
                request
            )
        
        if erros:
            for erro in erros:
                messages.warning(request, f"⚠ {erro}")
        
        return redirect("home:inscricao_turno_tdm")
        
    except Exception as e:
        messages.error(request, f"Erro ao processar inscrição: {str(e)}")
        registar_erro("inscrever_turno_tdm", str(e), {"aluno": n_meca, "turno": n_turno})
        return redirect("home:inscricao_turno_tdm")



#RSI
def index_rsi(request):
    return render(request, "rsi/index_rsi.html", { "area": "rsi" })

def ingresso_rsi(request):
    return render(request, "rsi/ingresso_rsi.html", { "area": "rsi" })

def plano_curric_rsi(request):
    # Filtrar apenas UCs de Redes e Sistemas Informaticos (id_curso = 3)
    unidades = UnidadeCurricular.objects.filter(id_curso_id=3).select_related(
        'id_anocurricular', 'id_semestre'
    ).order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "rsi/plano_curric_rsi.html", {"plano": plano, "area": "rsi"})

def estagio_rsi(request):
    return render(request, "rsi/estagio_rsi.html", { "area": "rsi" })

def contactos_rsi(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "rsi/contactos_rsi.html", { "area": "rsi", "docentes": docentes })

def avaliacoes_rsi(request):
    return render(request, "rsi/avaliacoes_rsi.html", { "area": "rsi" })

def saidas_rsi(request):
    return render(request, "rsi/saidas_rsi.html", { "area": "rsi" })

def horarios_rsi(request):
    return render(request, "rsi/horarios_rsi.html", { "area": "rsi" })


#DWDM
def index_dwdm(request):
    return render(request, "dwdm/index_dwdm.html", { "area": "dwdm" })

def ingresso_dwdm(request):
    return render(request, "dwdm/ingresso_dwdm.html", { "area": "dwdm" })

def plano_dwdm(request):
    # Filtrar apenas UCs de Desenvolvimento Web e Dispositivos Móveis (id_curso = 4)
    unidades = UnidadeCurricular.objects.filter(id_curso_id=4).select_related(
        'id_anocurricular', 'id_semestre'
    ).order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "dwdm/plano_dwdm.html", {"plano": plano, "area": "dwdm"})

def horarios_dwdm(request):
    return render(request, "dwdm/horarios_dwdm.html", { "area": "dwdm" })

def avaliacoes_dwdm(request):
    return render(request, "dwdm/avaliacoes_dwdm.html", { "area": "dwdm" })

def contactos_dwdm(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "dwdm/contactos_dwdm.html", { "area": "dwdm", "docentes": docentes })

def estagio_dwdm(request):
    return render(request, "dwdm/estagio_dwdm.html", { "area": "dwdm" })

def saidas_dwdm(request):
    return render(request, "dwdm/saidas_dwdm.html", { "area": "dwdm" })

def brightstart(request):
    return render(request, "dwdm/brightstart.html", { "area": "dwdm" })


#MESTRADO
def index_mestrado(request):
    return render(request, "eisi/index_mestrado.html", { "area": "eisi" })

def testemunho_mestrado(request):
    return render(request, "eisi/testemunho_mestrado.html", { "area": "eisi" })

def ingresso_mestrado(request):
    return render(request, "eisi/ingresso_mestrado.html", { "area": "eisi" })

def destinatarios_mestrado(request):
    return render(request, "eisi/destinatarios_mestrado.html", { "area": "eisi" })

def plano_curric_mestrado(request):
    # Filtrar apenas UCs de Engenharia Informática – Sistemas de Informação (id_curso = 5)
    unidades = UnidadeCurricular.objects.filter(id_curso_id=5).select_related(
        'id_anocurricular', 'id_semestre'
    ).order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre'
    )

    # Organiza por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    return render(request, "eisi/plano_curric_mestrado.html", {"plano": plano, "area": "eisi"})

def horarios_mestrado(request):
    return render(request, "eisi/horarios_mestrado.html", { "area": "eisi" })

def avaliacoes_mestrado(request):
    return render(request, "eisi/avaliacoes_mestrado.html", { "area": "eisi" })

def contactos_mestrado(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "eisi/contactos_mestrado.html", { "area": "eisi", "docentes": docentes })



#==========================
# ADMIN — UNIDADE CURRICULAR CRUD
def admin_uc_list(request):
    ucs = UnidadeCurricular.objects.all().order_by("id_unidadecurricular")

    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    curso = request.GET.get('curso')

    if ano:
        ucs = ucs.filter(id_anocurricular_id=ano)

    if semestre:
        ucs = ucs.filter(id_semestre_id=semestre)

    if curso:
        ucs = ucs.filter(id_curso_id=curso)

    anos = AnoCurricular.objects.all()
    semestres = Semestre.objects.all()
    cursos = Curso.objects.all()

    return render(request, "admin/uc_list.html", {
        "ucs": ucs,
        "anos": anos,
        "semestres": semestres,
        "cursos": cursos,
        "ano_selected": ano,
        "semestre_selected": semestre,
        "curso_selected": curso,
    })



def admin_uc_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        ects = request.POST.get("ects")

        uc = UnidadeCurricular.objects.create(
            nome=nome,
            ects=ects,
        )

        registar_log( request, operacao="CREATE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC criada: {uc.nome}")

        messages.success(request, "Unidade Curricular criada com sucesso!")
        return redirect("home:admin_uc_list")

    return render(
        request,
        "admin/uc_form.html",
        {
            "uc": None,
            "turnos_uc": [],
            "turnos_count": 0,
        },
    )

def admin_uc_edit(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)
    turnos_uc = (
        TurnoUc.objects.filter(id_unidadecurricular=uc)
        .select_related("id_turno")
        .order_by("id_turno__n_turno")
    )
    turnos_count = turnos_uc.count()

    if request.method == "POST":
        action = request.POST.get("action") or "update_uc"

        # Atualizar dados da UC
        if action == "update_uc":
            uc.nome = request.POST.get("nome")
            uc.ects = request.POST.get("ects")
            uc.save()

            registar_log(
                request,
                operacao="UPDATE",
                entidade="unidade_curricular",
                chave=str(uc.id_unidadecurricular),
                detalhes=f"UC atualizada: {uc.nome}",
            )

            messages.success(request, "Unidade Curricular atualizada!")
            return redirect("home:admin_uc_list")

        # Adicionar novo turno para esta UC
        if action == "add_turno":
            n_turno = request.POST.get("n_turno")
            tipo = request.POST.get("tipo")
            capacidade = request.POST.get("capacidade")
            hora_inicio = request.POST.get("hora_inicio")
            hora_fim = request.POST.get("hora_fim")

            novo_turno = Turno.objects.create(
                n_turno=n_turno or 0,
                tipo=tipo or "",
                capacidade=capacidade or 0,
            )

            TurnoUc.objects.create(
                id_turno=novo_turno,
                id_unidadecurricular=uc,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
            )

            registar_log(
                request,
                operacao="CREATE",
                entidade="turno",
                chave=str(novo_turno.id_turno),
                detalhes=f"Turno criado para UC {uc.nome}",
            )

            messages.success(request, "Turno adicionado à UC!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

        # Atualizar um turno existente
        if action == "update_turno":
            turno_id = request.POST.get("turno_id")
            turno = get_object_or_404(Turno, id_turno=turno_id)
            turno_uc = get_object_or_404(TurnoUc, id_turno=turno)

            turno.n_turno = request.POST.get("n_turno")
            turno.tipo = request.POST.get("tipo")
            turno.capacidade = request.POST.get("capacidade")
            turno.save()

            turno_uc.hora_inicio = request.POST.get("hora_inicio")
            turno_uc.hora_fim = request.POST.get("hora_fim")
            turno_uc.save()

            registar_log(
                request,
                operacao="UPDATE",
                entidade="turno",
                chave=str(turno.id_turno),
                detalhes=f"Turno atualizado para UC {uc.nome}",
            )

            messages.success(request, "Turno atualizado!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

        # Remover turno de uma UC
        if action == "delete_turno":
            turno_id = request.POST.get("turno_id")
            turno = get_object_or_404(Turno, id_turno=turno_id)

            # Remover relação Turno-UC e o próprio turno
            TurnoUc.objects.filter(id_turno=turno).delete()
            turno.delete()

            registar_log(
                request,
                operacao="DELETE",
                entidade="turno",
                chave=str(turno_id),
                detalhes=f"Turno removido da UC {uc.nome}",
            )

            messages.success(request, "Turno removido!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

    return render(
        request,
        "admin/uc_form.html",
        {
            "uc": uc,
            "turnos_uc": turnos_uc,
            "turnos_count": turnos_count,
        },
    )

def admin_uc_delete(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)
    uc.delete()

    registar_log( request, operacao="DELETE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC apagada: {uc.nome}")
    messages.success(request, "Unidade Curricular apagada!")
    return redirect("home:admin_uc_list")



def admin_logs_list(request):
    # Filtros
    operacao_filter = (request.GET.get('operacao') or '').strip()
    entidade_filter = (request.GET.get('entidade') or '').strip()
    limite = int(request.GET.get('limite', 500) or 500)
    limite = 1000 if limite > 1000 else (100 if limite < 1 else limite)

    def _to_str(val):
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        try:
            return json.dumps(val, ensure_ascii=False)
        except Exception:
            return str(val)

    # Fonte SQL
    sql_qs = LogEvento.objects.all()
    if operacao_filter:
        sql_qs = sql_qs.filter(operacao__icontains=operacao_filter)
    if entidade_filter:
        sql_qs = sql_qs.filter(entidade__icontains=entidade_filter)
    sql_qs = sql_qs.order_by('-data_hora')[:limite]

    sql_logs = [
        {
            "id": log.id_log,
            "fonte": "SQL",
            "data": log.data_hora,
            "data_display": log.data_hora.strftime("%Y-%m-%d %H:%M:%S") if log.data_hora else "",
            "operacao": log.operacao,
            "entidade": log.entidade,
            "chave": log.chave_primaria,
            "utilizador": log.utilizador_db,
            "ip": "",
            "user_agent": "",
            "detalhes": _to_str(log.detalhes),
        }
        for log in sql_qs
    ]

    # Fonte Mongo (todas as coleções relevantes)
    mongo_logs = listar_eventos_mongo(
        filtro_acao=operacao_filter or None,
        filtro_entidade=entidade_filter or None,
        limite=limite,
    )

    # Unificar e ordenar
    logs_unificados = sql_logs + mongo_logs
    logs_unificados = sorted(
        logs_unificados,
        key=lambda l: l.get("data") or datetime.min,
        reverse=True
    )[:limite]

    # Opções para filtros combinados
    mongo_all_for_filters = listar_eventos_mongo(limite=1000)
    operacoes = set(
        list(LogEvento.objects.values_list('operacao', flat=True).distinct()) +
        [l.get("operacao", "") for l in mongo_all_for_filters]
    )
    entidades = set(
        list(LogEvento.objects.values_list('entidade', flat=True).distinct()) +
        [l.get("entidade", "") for l in mongo_all_for_filters]
    )

    return render(request, "admin/logs_list.html", {
        "logs": logs_unificados,
        "operacoes": sorted([op for op in operacoes if op]),
        "entidades": sorted([ent for ent in entidades if ent]),
        "operacao_filter": operacao_filter,
        "entidade_filter": entidade_filter,
        "limite": limite,
    })

# ==========================
# Forum
# ==========================

def forum(request):
    return render(request, "forum/index_forum.html")



# ==========================

def dape(request):
    return render(request, "dape/dape.html")