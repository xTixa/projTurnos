from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from .models import AnoCurricular, UnidadeCurricular, Semestre, Docente, Curso, HorarioPDF, AvaliacaoPDF, Aluno, TurnoUc, Turno, InscricaoTurno, InscritoUc, LogEvento, AuditoriaInscricao, Matricula, LecionaUc
from .db_views import CadeirasSemestre, AlunosPorOrdemAlfabetica, Turnos, Cursos
from django.http import JsonResponse, FileResponse
import json
from django.contrib.auth.models import User
from bd2_projeto.services.mongo_service import (
    adicionar_log, listar_eventos_mongo, listar_logs, registar_auditoria_inscricao,
    validar_inscricao_disponivel, registar_consulta_aluno,
    registar_atividade_docente, registar_erro, registar_auditoria_user,
    criar_proposta_estagio, listar_propostas_estagio, atualizar_proposta_estagio, deletar_proposta_estagio
)
# ==========================================
# IMPORT DO SERVIÇO GridFS PARA PDFs
# ==========================================
# Importa as funções de armazenamento de PDFs no MongoDB
from bd2_projeto.services.gridfs_service import (
    upload_pdf_horario, upload_pdf_avaliacao,
    download_pdf, deletar_pdf, listar_pdfs_horarios, listar_pdfs_avaliacoes
)
from core.utils import registar_log, admin_required, aluno_required, user_required, docente_required
import time
from django.db.models import Count


def _listar_pdfs_por_ano(model_cls, course_id):
    """Obtém o PDF mais recente por ano curricular, priorizando o curso indicado."""
    anos = AnoCurricular.objects.all().order_by("id_anocurricular")
    documentos = []

    for ano in anos:
        base_qs = model_cls.objects.filter(id_anocurricular=ano)

        pdf = base_qs.filter(id_curso_id=course_id).order_by("-atualizado_em").first()
        if not pdf:
            pdf = base_qs.filter(id_curso__isnull=True).order_by("-atualizado_em").first()

        documentos.append({"ano": ano, "pdf": pdf})

    return documentos

#view pagina inicial DI
def index(request):
    return render(request, "di/index_di.html", {"area": "di"})

#view para login
def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username") # le o valor introduzido no username, pode ser username ou email
        password = request.POST.get("password") # le o valor introduzido na password

        #tenta fazer login de um user do django
        user = authenticate(request, username=username_or_email, password=password)

        #se o user for encontrado no django, faz login, senao redireciona para a pagina inicial
        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("home:admin_dashboard")

            return redirect("home:index")

        #procura na tabela de alunos algum registo com estes dados
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

        #procura na tabela de docentes algum registo com estes dados
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
        
        #caso nao exista ninguem com os dados fornecidos, da msg de erro
        messages.error(request, "Utilizador ou palavra-passe incorretos.")
        return redirect("home:login")

    return render(request, "auth/login.html")

#view para logout
def do_logout(request):
    auth_logout(request)  #faz o logout do Django
    request.session.flush()  # limpa toda a sessão
    return redirect("home:login")  # redireciona para a página de login novamente

#view para ingresso em EI
def ingresso(request):
    return render(request, "ei/ingresso.html", { "area": "ei" })

#view para plano curricular de EI
def plano_curricular(request):
    #se o utilizador for aluno, regista a consulta na coleçao do MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "plano_curricular", {"curso": "EI"})
    
    #obtem as UCs do curso com id_curso = 1 (Engenharia Informática)
    #o select_related evita que haja queries desnecessarias
    unidades = UnidadeCurricular.objects.filter(id_curso_id=1).select_related('id_anocurricular', 'id_semestre').order_by(
        'id_anocurricular__id_anocurricular', 'id_semestre__id_semestre')

    #cria uma struct para guardar o plano curricular organizado por ano e semestre
    plano = {}
    for uc in unidades:
        ano = uc.id_anocurricular.ano_curricular
        semestre = uc.id_semestre.semestre
        if ano not in plano:
            plano[ano] = {}
        if semestre not in plano[ano]:
            plano[ano][semestre] = []
        plano[ano][semestre].append(uc)

    #plano é um dicionario com as UCs organizadas por ano e semestre
    #area é o identificador do curso para o template
    return render(request, "ei/plano_curricular.html", {"plano": plano, "area": "ei"})

#view para horarios de EI
def horarios(request):
    #se o utilizador for aluno, regista a consulta na coleçao do MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "horarios", {"curso": "EI"})

    horarios_por_ano = _listar_pdfs_por_ano(HorarioPDF, course_id=1)
    
    # Verificar se o aluno pertence ao curso de EI (id_curso = 1)
    pode_inscrever = False
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        try:
            aluno = Aluno.objects.get(n_mecanografico=request.session["user_id"])
            pode_inscrever = (aluno.id_curso_id == 1)  # Apenas alunos de EI
        except Aluno.DoesNotExist:
            pass

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

    avaliacoes_por_ano = _listar_pdfs_por_ano(AvaliacaoPDF, course_id=1)

    return render(request, "ei/avaliacoes.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "ei"})

#view para contactos de EI
def contactos(request):
    #procura todos os docentes e ordena pelo nome
    docentes = Docente.objects.all().order_by('nome')

    #procura dados do curso principal neste caso EI
    curso = Curso.objects.filter(nome__icontains="Engenharia Informática").first()

    return render(request, "ei/contactos.html", {"curso": curso, "docentes": docentes, "area": "ei"})

#view para inscricao em turnos de EI (pagina apenas)
def inscricao_turno(request):
    #verifica se o user é aluno, caso nao seja redireciona para a login page
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    #recolhe o nMecanografico do aluno e vai buscar o aluno em questao
    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)

    #verifica se o aluno é de EI ou de TDM, caso nao seja, redireciona para a pagina inicial
    if aluno.id_curso_id != 1:
        messages.error(request, "Esta página é apenas para alunos de Engenharia Informática.")
        if aluno.id_curso_id == 2:
            return redirect("home:inscricao_turno_tdm")
        return redirect("home:index")

    #obtem os ids dos turnos em que o aluno ja está inscrito
    inscricoes_turno = InscricaoTurno.objects.filter(n_mecanografico=aluno).values_list('id_turno_id', flat=True)
    turnos_inscritos = set(inscricoes_turno)

    #obtem as UCs em que o aluno está inscrito
    inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True).values('id_unidadecurricular')

    #lista com as UCs e os turnos disponiveis
    lista_uc = []

    #lista de turnos em que o aluno esta inscrito
    turnos_no_horario = []

    #para cada inscricao do aluno
    for inscricao in inscricoes:
        uc_id = inscricao['id_unidadecurricular']
        uc = UnidadeCurricular.objects.get(id_unidadecurricular=uc_id)

        #obtem quais os turnos que existem nesta uc
        relacoes = TurnoUc.objects.filter(id_unidadecurricular=uc)

        #lista de turnos para esta UC
        turnos = []
        for r in relacoes:
            turno = r.id_turno

            #ve quantos estao inscritos no turno e calcula as vagss
            ocupados = InscricaoTurno.objects.filter(id_turno=turno).count()
            vagas = turno.capacidade - ocupados
            if vagas < 0:
                vagas = 0

            #ve se o aluno ja esta inscrito no turbo
            ja_inscrito = turno.id_turno in turnos_inscritos

            #converte as horas do datetime para uma string
            hora_inicio_str = r.hora_inicio.strftime("%H:%M")
            hora_fim_str = r.hora_fim.strftime("%H:%M")

            #mapear o dia da semana
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

            #dicionario com a info do turno da uc
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
            
            #se o aluno está inscrito, adiciona o mesmo na lista do horário
            if ja_inscrito:
                turnos_no_horario.append({
                    "uc_nome": uc.nome,
                    "turno_nome": f"T{turno.n_turno}",
                    "tipo": turno.tipo,
                    "dia": dia_semana,
                    "hora_inicio": hora_inicio_str,
                    "hora_fim": hora_fim_str,
                })

        #adiciona a UC na lista com os seus turnos
        lista_uc.append({
            "id": uc.id_unidadecurricular,
            "nome": uc.nome,
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
        aluno = get_object_or_404(Aluno, n_mecanografico=user_id)
        context["user_obj"] = aluno
        context["tipo"] = "Aluno"
        
        # Turnos inscritos
        inscricoes = InscricaoTurno.objects.filter(n_mecanografico=aluno).select_related('id_turno', 'id_unidadecurricular')
        
        #lista com a info dos turnos do aluno
        turnos_info = []
        for inscricao in inscricoes:
            turno = inscricao.id_turno
            uc = inscricao.id_unidadecurricular
            
            # Tenta ter info extra de horário (TurnoUc)
            # Usamos filter().first() porque a tabela pode ter múltiplas entradas para o mesmo id_turno (modelo incorreto?)
            # e porque queremos o horário deste turno NESTA disciplina específica.
            turno_uc = TurnoUc.objects.filter(id_turno=turno, id_unidadecurricular=uc).first()
            
            if turno_uc:
                hora_inicio = turno_uc.hora_inicio.strftime("%H:%M")
                hora_fim = turno_uc.hora_fim.strftime("%H:%M")
                
                #determina o de dia da semana
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
            
            #adiciona a lista um dicionario com a info de cada turno do alino
            turnos_info.append({
                "uc": uc.nome,
                "turno": f"T{turno.n_turno}",
                "tipo": turno.tipo,
                "horario": f"{dia_semana}, {hora_inicio} - {hora_fim}"
            })
        
        #coloca a lista no contexto para ser apresentado no template
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
    
    #verifica se o user é aluno, senao for, nao dá para inscrevr
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        mensagem_erro = "Apenas alunos se podem inscrever em turnos."
        messages.error(request, mensagem_erro)
        registar_erro("inscrever_turno", mensagem_erro)
        return redirect("home:login")

    try:
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        
        #verifica se o aluno pertence a EI
        if aluno.id_curso_id != 1:
            messages.error(request, "Esta funcionalidade é apenas para alunos de Engenharia Informática.")
            return redirect("home:index")
        
        #vai buscar o turno e a uc com base no id recebido
        turno_uc = get_object_or_404(Turno, id_turno=turno_id)
        uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=uc_id)

        #verifica se turno pertence à UC
        turno_uc_existe = TurnoUc.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).exists()
        if not turno_uc_existe:
            resultado = "nao_autorizado"
            motivo = "Este turno não pertence a esta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        #verifica se o aluno está inscrito na UC
        inscrito = InscritoUc.objects.filter(n_mecanografico=aluno, id_unidadecurricular=uc, estado=True).exists()
        if not inscrito:
            resultado = "nao_autorizado"
            motivo = "Não estás inscrito nesta UC"
            messages.error(request, motivo)
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")
        
        #verifica se já está inscrito no turno
        pode_inscrever, msg_validacao = validar_inscricao_disponivel(aluno.n_mecanografico, turno_id)
        if not pode_inscrever:
            resultado = "uc_duplicada"
            motivo = msg_validacao
            messages.warning(request, "Já estás inscrito neste turno.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        #verifica a capacidade restante do turno
        ocupados = InscricaoTurno.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).count()
        if ocupados >= turno_uc.capacidade:
            resultado = "turno_cheio"
            motivo = f"Turno cheio (capacidade: {turno_uc.capacidade}, ocupado: {ocupados})"
            messages.error(request, "Este turno já está cheio.")
            tempo_ms = int((time.time() - inicio_tempo) * 1000)
            registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, resultado, motivo, tempo_ms)
            return redirect("home:inscricao_turno")

        #cria a inscricao
        inscricao = InscricaoTurno.objects.create(n_mecanografico=aluno, id_turno=turno_uc, id_unidadecurricular=uc, data_inscricao=datetime.today().date())

        #calcula o tempo de processamento e regista nos logs
        tempo_ms = int((time.time() - inicio_tempo) * 1000)
        auditoria_pg = AuditoriaInscricao.objects.create(n_mecanografico=aluno, id_turno=turno_uc, id_unidadecurricular=uc, resultado='sucesso',tempo_processamento_ms=tempo_ms)

        registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, 'sucesso', None, tempo_ms)
        adicionar_log("inscricao_turno_sucesso", {"aluno": aluno.nome, "uc": uc.nome, "turno": turno_id, "tempo_ms": tempo_ms}, request)
        messages.success(request, "Inscrição no turno efetuada com sucesso!")
        return redirect("home:inscricao_turno")
    
    #caso exista erro, este tambem fica registado nos logs
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
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        return JsonResponse({"erro": "Acesso não autorizado"}, status=403)

    try:
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        turno_uc = get_object_or_404(Turno, id_turno=turno_id)
        uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=uc_id)

        #query para encontrar a inscriçao do aluno no turno
        qs = InscricaoTurno.objects.filter(n_mecanografico=aluno, id_turno=turno_uc, id_unidadecurricular=uc)

        #apaga os registos encontrados e devolve as linhas eliminadas
        removidas = qs.delete()[0]

        #senão removeu nada, tenta apagar as inscrições do aluno no turno
        if removidas == 0:
            removidas = InscricaoTurno.objects.filter(n_mecanografico=aluno, id_turno=turno_uc).delete()[0]

        #caso tenha removido, regista nos logs
        if removidas > 0:
            registar_auditoria_inscricao(aluno.n_mecanografico, turno_id, uc_id, uc.nome, 'desinscrever', None, 0)
            adicionar_log("desinscrever_turno", {"aluno": aluno.n_mecanografico, "turno": turno_id, "uc": uc_id, "registos_removidos": removidas, }, request)
            messages.success(request, f"Desinscrição em {uc.nome} — {turno_uc.tipo} efetuada!")
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
        aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
        turno_novo = get_object_or_404(Turno, id_turno=turno_id)

        #procura os registos associados ao turno
        turnos_uc_novo = TurnoUc.objects.filter(id_turno=turno_novo)
        if not turnos_uc_novo.exists():
            return JsonResponse({"conflitos": []})

        #obtem as inscriçoes atuais do aluno
        inscricoes = InscricaoTurno.objects.filter(n_mecanografico=aluno).select_related('id_turno', 'id_unidadecurricular')

        #lista onde vao ser guardados os conflitos que forem encontrados
        conflitos = []
        
        #para cada espaço no horario do turno novo
        for turno_uc_novo in turnos_uc_novo:
            hora_inicio_novo = turno_uc_novo.hora_inicio
            hora_fim_novo = turno_uc_novo.hora_fim
            dia_novo = getattr(turno_uc_novo, "dia", None)

            #compara com os turnos em que o aluno ja está inscrito
            for insc in inscricoes:
                turno_uc_existente = TurnoUc.objects.filter(id_turno=insc.id_turno).first()

                if turno_uc_existente:
                    hora_inicio_existente = turno_uc_existente.hora_inicio
                    hora_fim_existente = turno_uc_existente.hora_fim
                    dia_existente = getattr(turno_uc_existente, "dia", None)

                    #se os dias forem diferentes, nao ha conflito
                    if dia_novo and dia_existente and dia_novo != dia_existente:
                        continue
                    
                    #verifica se ha sobreposiçao de horarios
                    if (hora_inicio_novo < hora_fim_existente and hora_fim_novo > hora_inicio_existente):
                        conflitos.append({
                            "uc": insc.id_unidadecurricular.nome,
                            "turno": insc.id_turno.tipo,
                            "horario": f"{hora_inicio_existente.strftime('%H:%M')} - {hora_fim_existente.strftime('%H:%M')}"
                        })

        #remove conflitos duplicados
        conflitos_unicos = []
        chaves_vistas = set()
        for c in conflitos:
            chave = (c['uc'], c['turno'], c['horario'])
            if chave not in chaves_vistas:
                chaves_vistas.add(chave)
                conflitos_unicos.append(c)

        #devolve a lista de conflitos
        return JsonResponse({"conflitos": conflitos_unicos})

    except Exception as e:
        import traceback
        registar_erro("api_verificar_conflitos", str(e), {"turno_id": turno_id, "traceback": traceback.format_exc()})
        return JsonResponse({"erro": str(e), "debug": traceback.format_exc()}, status=500)

#view para obter as ucs por semestre
def cadeiras_semestre(request):
    data = list(CadeirasSemestre.objects.order_by('semestre_id', 'nome').values('id_unidadecurricular', 'nome', 'ects', 'semestre_id', 'semestre_nome'))
    return JsonResponse(data, safe=False)

#view para obter os launos alfabeticamente
def alunos_por_ordem_alfabetica(request):
    data = list(AlunosPorOrdemAlfabetica.objects.order_by('nome').values('n_mecanografico', 'nome', 'email', 'id_anocurricular'))
    return JsonResponse(data, safe=False)

#view para obter os turnos
def turnos_list(request):
    data = list(Turnos.objects.order_by('id_turno').values('id_turno', 'n_turno', 'capacidade', 'tipo'))
    return JsonResponse(data, safe=False)

#view para obter os cursos
def cursos_list(request):
    data = list(Cursos.objects.order_by('id_curso').values('id_curso', 'nome', 'grau'))
    return JsonResponse(data, safe=False)

#view para o dashboard do admin
@admin_required
def admin_dashboard(request):
    #recolhe os dados principais para apresentar no dashboard
    total_users = User.objects.count()
    total_turnos = Turnos.objects.count()
    total_ucs = UnidadeCurricular.objects.count()
    total_cursos = Curso.objects.count()
    total_horarios = HorarioPDF.objects.count()
    total_avaliacoes = AvaliacaoPDF.objects.count()

    #calcula os dados para o grafico de alunos por UC
    alunos_por_uc = InscritoUc.objects.values('id_unidadecurricular__nome').annotate(total=Count('n_mecanografico')).order_by('-total')[:10]  # Top 10 UCs
    
    #prepara os dados em formato JSON para o template
    chart_alunos_labels = json.dumps([item['id_unidadecurricular__nome'] for item in alunos_por_uc])
    chart_alunos_values = json.dumps([item['total'] for item in alunos_por_uc])

    #calcula as vagas disponiveis e ocupadas
    total_vagas = Turnos.objects.aggregate(total=models.Sum('capacidade'))['total'] or 0
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

#view para listar os utilizadores admin, alunos e docentes
def admin_users_list(request):
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
    
    #agrupa as 3 listas de users e ordena pelo id
    users = list(django_users) + list(alunos) + list(docentes)
    users_sorted = sorted(users, key=lambda x: x.get('id', 0))
    
    return render(request, "admin/users_list.html", {"users": users_sorted})

#view para criar um user e listar os restantes
def admin_users_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        #obriga a inserir um nome e uma pass e depois reconstroi a lista
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

            #volta a mostrar o formulario
            return render(request, "admin/users_form.html", {"users": users_sorted})

        #cria um user djang com pass encriptada
        User.objects.create_user(username=username, email=email, password=password)
        
        #vai buscar o user acabado de criar
        novo_user = User.objects.get(username=username)
        
        #faz o registo nos logs
        registar_log(request, operacao="CREATE", entidade="user_admin", chave=str(novo_user.id), detalhes=f"Novo utilizador criado: {username} ({email})")
        registar_auditoria_user("CREATE", novo_user.id, "Admin", {"username": username, "email": email}, request)
        messages.success(request, "Utilizador criado com sucesso!")
        return redirect("home:admin_users_list")

    #se nao houve pedido por POST, entao os dados apenas saoa preparados para o forms
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

#view para editar os dados de um user
def admin_users_edit(request, id):
    user = None
    user_type = None
    
    #tenta encontrar o user como Admin
    try:
        user = User.objects.get(id=id)
        user_type = "Admin"
    except User.DoesNotExist:
        pass
    
    #senao encontrar, vai tentar como ALuno
    if not user:
        try:
            user = Aluno.objects.get(n_mecanografico=id)
            user_type = "Aluno"
        except Aluno.DoesNotExist:
            pass
    
    #senao encontrar nem aluno nem admin, tenta como docente
    if not user:
        try:
            user = Docente.objects.get(id_docente=id)
            user_type = "Docente"
        except Docente.DoesNotExist:
            pass
    
    #senao encontrar nenhum, volta apenas apra a ista de users
    if not user:
        return redirect("admin_users_list")

    #pedido post para editar os dados
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        
        #guarda os dados antigos para colocar nos logs
        old_data = {'username': user.username if user_type == "Admin" else user.nome, 'email': user.email}
        
        #atualiza os campos conforme o user
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
        
        #regista nos logs a alteraçao feita
        registar_log(request, operacao="UPDATE", entidade=f"user_{user_type.lower()}", chave=str(id), detalhes=f"Campos alterados: username={username}, email={email}")
        registar_auditoria_user("UPDATE", id, user_type,{"username": username, "email": email, "alterado_de": old_data}, request)
        messages.success(request, "Utilizador atualizado com sucesso!")
        return redirect("home:admin_users_list")

    #para o get, prepara os dados do user para preencher o forms
    user_data = {
        'id': user.id if user_type == "Admin" else (user.n_mecanografico if user_type == "Aluno" else user.id_docente),
        'username': user.username if user_type == "Admin" else user.nome,
        'email': user.email,
        'tipo': user_type
    }
    
    #recria a lista de users totais
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

#view para apagar um user
def admin_users_delete(request, id):
    user = None
    user_type = None
    username = None
    
    #tenta encontrar o user como Admin
    try:
        user = User.objects.get(id=id)
        user_type = "Admin"
        username = user.username
    except User.DoesNotExist:
        pass
    
    #senao encontrar, tenta commo Aluno
    if not user:
        try:
            user = Aluno.objects.get(n_mecanografico=id)
            user_type = "Aluno"
            username = user.nome
            
            #remove as matriculas do aluno
            matriculas = Matricula.objects.filter(n_mecanografico=user)
            total_matriculas = matriculas.count()
            matriculas.delete()
            
            #remove as inscriçoes nos turnos em que o aluno esta inscrito
            inscricoes_turno = InscricaoTurno.objects.filter(n_mecanografico=user)
            total_inscricoes = inscricoes_turno.count()
            inscricoes_turno.delete()
            
            #remove as inscriçoes nas ucs em que o aluno esta inscrito
            inscricoes_uc = InscritoUc.objects.filter(n_mecanografico=user)
            total_ucs = inscricoes_uc.count()
            inscricoes_uc.delete()
            
            messages.info(request, f"Removidas {total_matriculas} matrículas, {total_inscricoes} inscrições em turnos e {total_ucs} inscrições em UCs.")
            
        except Aluno.DoesNotExist:
            pass
    
    #senao for Admin nem Aluno, tenta como Docente
    if not user:
        try:
            user = Docente.objects.get(id_docente=id)
            user_type = "Docente"
            username = user.nome
            
            #remove a UC do docente
            leciona = LecionaUc.objects.filter(id_docente=user)
            total_ucs = leciona.count()
            leciona.delete()
            
            messages.info(request, f"Removidas {total_ucs} associações com UCs.")
            
        except Docente.DoesNotExist:
            pass
    
    #caso nao seja nenhum dos anteriores, apresenta erro
    if not user:
        messages.error(request, "Utilizador não encontrado.")
        return redirect("home:admin_users_list")
    
    registar_log(request, operacao="DELETE", entidade=f"user_{user_type.lower()}", chave=str(id), detalhes=f"Utilizador apagado: {username} (Tipo: {user_type})")
    registar_auditoria_user("DELETE", id, user_type, {"username": username, "email": user.email, "tipo": user_type}, request)
    user.delete()
    messages.success(request, f"{user_type} '{username}' apagado com sucesso!")
    return redirect("home:admin_users_list")

#view para listar todos os turnos no admin
def admin_turnos_list(request):
    turnos = Turnos.objects.all().order_by("id_turno")
    return render(request, "admin/turnos_list.html", {"turnos": turnos})

#view para criar um novo turno
def admin_turnos_create(request):
    if request.method == "POST":
        n_turno = request.POST.get("n_turno")
        capacidade = request.POST.get("capacidade")
        tipo = request.POST.get("tipo")

        #cria o turno na base de dados
        turno = Turnos.objects.create(n_turno=n_turno, capacidade=capacidade, tipo=tipo,)

        registar_log(request, operacao="CREATE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno criado: {turno.tipo} (nº {turno.n_turno})")
        messages.success(request, "Turno criado com sucesso!")
        return redirect("home:admin_turnos_list")

    return render(request, "admin/turnos_form.html")

#view paraa editar turno
def admin_turnos_edit(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)

    #se for post atualiza os campos dos turnos
    if request.method == "POST":
        turno.n_turno = request.POST.get("n_turno")
        turno.capacidade = request.POST.get("capacidade")
        turno.tipo = request.POST.get("tipo")
        turno.save()

        registar_log(request, operacao="UPDATE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno atualizado: {turno.tipo} (nº {turno.n_turno})")

        messages.success(request, "Turno atualizado!")
        return redirect("admin_turnos_list")

    #se for get, apenas mostra o form preenchido
    return render(request, "admin/turnos_form.html", {"turno": turno})

#view para eliminar turno
def admin_turnos_delete(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)
    turno.delete()
    registar_log(request, operacao="DELETE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno apagado: {turno.tipo} (nº {turno.n_turno})")
    messages.success(request, "Turno apagado!")
    return redirect("admin_turnos_list")

#view para upload pdf com o horario
def admin_horarios_create(request):
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')
    
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
            # GUARDAR REFERÊNCIA NA BD (Django/PostgreSQL)
            # ==========================================
            # Em vez de guardar o ficheiro no filesystem,
            # guardamos apenas o ID do GridFS como referência
            HorarioPDF.objects.create(
                nome=nome,
                ficheiro=f"mongodb_gridfs:{file_id_mongodb}",  # Formato especial para indicar que está no MongoDB
                id_anocurricular_id=ano_id,
                id_curso_id=curso_id,
            )
            
            # Regista a operação no log
            registar_log(request, operacao="CREATE", entidade="horario_pdf", chave=file_id_mongodb, detalhes=f"Horário PDF criado no MongoDB: {nome}")
            
            messages.success(request, "Horário carregado com sucesso no MongoDB!")
            return redirect("home:admin_horarios_list")
        
        except Exception as e:
            # Se algo correr mal, mostra a mensagem de erro
            messages.error(request, f"Erro ao carregar horário: {str(e)}")
            return redirect("home:admin_horarios_create")

    return render(request, "admin/horarios_form.html", {'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para editar o pdf com o horario
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

        if curso_id:
            horario.id_curso_id = curso_id

        #se foi efetuado o upload de um pdf, este substitui o pdf atual
        if "ficheiro" in request.FILES:
            horario.ficheiro = request.FILES["ficheiro"]

        horario.save()
        messages.success(request, "Horário atualizado!")
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html", {"horario": horario, 'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para eliminar o pdf do horario
def admin_horarios_delete(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)
    horario.delete()
    messages.success(request, "Horário apagado!")
    return redirect("home:admin_horarios_list")

#view para listar os horarios
def admin_horarios_list(request):
    horarios = HorarioPDF.objects.all().order_by("-atualizado_em")
    return render(request, "admin/horarios_list.html", {"horarios": horarios})

#view para mostrar na web o mais recente
def horarios_admin(request):
    pdf = HorarioPDF.objects.order_by("-atualizado_em").first()
    return render(request, "home/horarios.html", {"pdf": pdf})

#view para listar os pdf das avaliacoes
@admin_required
def admin_avaliacoes_list(request):
    avaliacoes = AvaliacaoPDF.objects.all().order_by("-atualizado_em")
    return render(request, "admin/avaliacoes_list.html", {"avaliacoes": avaliacoes})

#view para upload pdf para avaliacoes
@admin_required
def admin_avaliacoes_create(request):
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')

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
            # GUARDAR REFERÊNCIA NA BD (Django/PostgreSQL)
            # ==========================================
            # Guardamos apenas o ID do GridFS como referência
            AvaliacaoPDF.objects.create(
                nome=nome,
                ficheiro=f"mongodb_gridfs:{file_id_mongodb}",  # Indica que está no MongoDB
                id_anocurricular_id=ano_id,
                id_curso_id=curso_id,
            )

            registar_log(request, operacao="CREATE", entidade="avaliacao_pdf", chave=file_id_mongodb, detalhes=f"Avaliação PDF criada no MongoDB: {nome}")
            messages.success(request, "Calendário de avaliações carregado com sucesso no MongoDB!")
            return redirect("home:admin_avaliacoes_list")
        
        except Exception as e:
            messages.error(request, f"Erro ao carregar avaliação: {str(e)}")
            return redirect("home:admin_avaliacoes_create")

    return render(request, "admin/avaliacoes_form.html", {'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view editar um pdf de avaliacoes
@admin_required
def admin_avaliacoes_edit(request, id):
    avaliacao = get_object_or_404(AvaliacaoPDF, id=id)
    cursos = Curso.objects.all().order_by('nome')
    anos_curriculares = AnoCurricular.objects.all().order_by('id_anocurricular')

    if request.method == "POST":
        avaliacao.nome = request.POST.get("nome")
        ano_id = request.POST.get("id_anocurricular")
        curso_id = request.POST.get("id_curso")
        
        #atualiza o ano curricular se tiver selecionado
        if ano_id:
            avaliacao.id_anocurricular_id = ano_id

        if curso_id:
            avaliacao.id_curso_id = curso_id

        #substitui o pdf atual pelo novo
        if "ficheiro" in request.FILES:
            avaliacao.ficheiro = request.FILES["ficheiro"]

        avaliacao.save()
        registar_log(request, operacao="UPDATE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF atualizada: {avaliacao.nome}")
        messages.success(request, "Calendário de avaliações atualizado!")
        return redirect("home:admin_avaliacoes_list")

    return render(request, "admin/avaliacoes_form.html", {"avaliacao": avaliacao, 'cursos': cursos, 'anos_curriculares': anos_curriculares})

#view para apagar o pdf das avaliacoes
@admin_required
def admin_avaliacoes_delete(request, id):
    avaliacao = get_object_or_404(AvaliacaoPDF, id=id)
    nome = avaliacao.nome
    
    try:
        # ==========================================
        # EXTRAIR ID DO MongoDB (GridFS)
        # ==========================================
        # Verifica se o ficheiro está no MongoDB
        # O formato é "mongodb_gridfs:ID_DO_FICHEIRO"
        if avaliacao.ficheiro.startswith("mongodb_gridfs:"):
            # Extrai o ID do ficheiro
            file_id_mongodb = avaliacao.ficheiro.replace("mongodb_gridfs:", "")
            
            # ==========================================
            # DELETAR DO MongoDB (GridFS)
            # ==========================================
            # Remove o ficheiro do MongoDB
            deletar_pdf(file_id_mongodb, tipo_pdf="avaliacao")
        
        # Remove o registo da BD
        avaliacao.delete()
        registar_log(request, operacao="DELETE", entidade="avaliacao_pdf", chave=str(id), detalhes=f"Avaliação PDF apagada do MongoDB: {nome}")
        messages.success(request, "Calendário de avaliações apagado!")
        
    except Exception as e:
        messages.error(request, f"Erro ao apagar avaliação: {str(e)}")
    
    return redirect("home:admin_avaliacoes_list")

#view para listar os docentes no admin
def admin_users_docentes(request):
    docentes = Docente.objects.all().order_by("id_docente")
    return render(request, "admin/users_filter.html", {"titulo": "Docentes", "users": docentes})

#view para listar os alunos no admin
def admin_users_alunos(request):
    alunos = Aluno.objects.all().order_by("n_mecanografico")
    return render(request, "admin/users_filter.html", {"titulo": "Alunos", "users": alunos})

def testar_mongo(request):
    # Adicionar um log no MongoDB
    adicionar_log("teste_ligacao", {"user": "teste_django"})

    # Ler todos os logs existentes
    logs = listar_logs()

    return JsonResponse({"estado": "ok", "logs": logs})

#view para apagar o pdf dos horarios
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
    docentes = Docente.objects.all().order_by('nome')
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
    unidades = UnidadeCurricular.objects.filter(id_curso_id=2).select_related('id_anocurricular', 'id_semestre').order_by('id_anocurricular__id_anocurricular', 'id_semestre__id_semestre')

    #constroi um dicionario para o plano
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

#view para mostrar os horarios TDM
def horarios_tdm(request):
    #se o utilizador for aluno, regista a consulta na coleçao do MongoDB
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        registar_consulta_aluno(request.session.get("user_id"), request.session.get("user_nome", "desconhecido"), "horarios", {"curso": "TDM"})
    
    horarios_por_ano = _listar_pdfs_por_ano(HorarioPDF, course_id=2)
    
    # Verificar se o aluno pertence ao curso de TDM (id_curso = 2)
    pode_inscrever = False
    if "user_tipo" in request.session and request.session["user_tipo"] == "aluno":
        try:
            aluno = Aluno.objects.get(n_mecanografico=request.session["user_id"])
            pode_inscrever = (aluno.id_curso_id == 2)  # Apenas alunos de TDM
        except Aluno.DoesNotExist:
            pass

    return render(request, "tdm/horarios_tdm.html", {
        "horarios_por_ano": horarios_por_ano, 
        "area": "tdm",
        "pode_inscrever": pode_inscrever
    })

#view contactos TDM
def contactos_tdm(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "tdm/contactos_tdm.html", { "area": "tdm", "docentes": docentes })

#view saidas profissionais TDM
def saidas_tdm(request):
    return render(request, "tdm/saidas.html", { "area": "tdm" })

#view avaliacoes TDM
def avaliacoes_tdm(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano(AvaliacaoPDF, course_id=2)
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

    #obtem nMecanografico do aluno
    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)
    
    #verifica se o aluno pertence a TDM
    if aluno.id_curso_id != 2:
        messages.error(request, "Esta página é apenas para alunos de Tecnologia e Design Multimédia.")
        if aluno.id_curso_id == 1:
            return redirect("home:inscricao_turno")
        return redirect("home:index")
    
    #verifica se já tem inscrições em algum turno
    inscricoes_existentes = InscricaoTurno.objects.filter(n_mecanografico=aluno)
    turno_escolhido = None
    
    #se houver uma inscriçao, obtem numero do turno
    if inscricoes_existentes.exists():
        primeira_inscricao = inscricoes_existentes.first()
        turno_escolhido = primeira_inscricao.id_turno.n_turno if primeira_inscricao.id_turno else None
    
    #UCs em que está inscrito
    inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True).select_related('id_unidadecurricular')
    ucs_inscritas = [i.id_unidadecurricular for i in inscricoes]
    
    #struct para os turnos e lista de UCs
    turnos_info = {
        1: {"nome": "Turno 1", "ucs": []},
        2: {"nome": "Turno 2", "ucs": []}
    }
    
    #para cada UC que esta inscrito, procura registos TurnoUC
    for uc in ucs_inscritas:
        turnos_uc = TurnoUc.objects.filter(id_unidadecurricular=uc).select_related('id_turno')
        
        for turno_rel in turnos_uc:
            turno = turno_rel.id_turno
            n_turno = turno.n_turno
            
            #calcula quantoas estao inscritos e as vags disponiveis
            if n_turno in [1, 2]:
                ocupados = InscricaoTurno.objects.filter(id_turno=turno,id_unidadecurricular=uc).count()
                vagas = turno.capacidade - ocupados
                if vagas < 0:
                    vagas = 0
                
                #converte a hora para string e extrai para mapear o dia da semana
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
                
                #adiciona esta UC à lisra de UCs do turno escolhido
                turnos_info[n_turno]["ucs"].append({
                    "nome": uc.nome,
                    "horario": f"{dia_semana} {turno_rel.hora_inicio.strftime('%H:%M')}-{turno_rel.hora_fim.strftime('%H:%M')}",
                    "vagas": vagas,
                    "capacidade": turno.capacidade
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
    aluno = Aluno.objects.get(n_mecanografico=n_meca)
    
    if aluno.id_curso_id != 2:
        messages.error(request, "Esta funcionalidade é apenas para alunos de TDM.")
        return redirect("home:index")
    
    #se ja existe inscriçao, nao deixa inscrever
    try:
        inscricoes_existentes = InscricaoTurno.objects.filter(n_mecanografico=aluno)
        if inscricoes_existentes.exists():
            messages.warning(request, "Já tens um turno escolhido. Para mudar, contacta a coordenação.")
            return redirect("home:inscricao_turno_tdm")
        
        #UCs onde está inscrito
        inscricoes = InscritoUc.objects.filter(n_mecanografico=aluno, estado=True)
        
        inscricoes_realizadas = 0
        erros = []
        
        for inscricao in inscricoes:
            uc = inscricao.id_unidadecurricular
            
            try:
                turno_uc_rel = TurnoUc.objects.filter(id_unidadecurricular=uc, id_turno__n_turno=n_turno).select_related('id_turno').first()
                
                if not turno_uc_rel:
                    erros.append(f"{uc.nome}: Turno {n_turno} não disponível")
                    continue
                
                turno = turno_uc_rel.id_turno
                
                #verifica capacidade do turno
                ocupados = InscricaoTurno.objects.filter(id_turno=turno, id_unidadecurricular=uc).count()
                
                if ocupados >= turno.capacidade:
                    erros.append(f"{uc.nome}: Turno {n_turno} cheio")
                    continue
                
                #criacao da inscricao no turno
                InscricaoTurno.objects.create(n_mecanografico=aluno, id_turno=turno, id_unidadecurricular=uc, data_inscricao=datetime.today().date())
                
                tempo_ms = int((time.time() - inicio_tempo) * 1000)
                registar_auditoria_inscricao(aluno.n_mecanografico, turno.id_turno, uc.id_unidadecurricular, uc.nome, 'sucesso', f'Inscrição TDM - Turno {n_turno}', tempo_ms)
                inscricoes_realizadas += 1
                
            except Exception as e:
                erros.append(f"{uc.nome}: {str(e)}")
        
        if inscricoes_realizadas > 0:
            messages.success(request, f"✓ Inscrito no Turno {n_turno} em {inscricoes_realizadas} UC(s)!")
            adicionar_log("inscricao_turno_tdm_sucesso", {"aluno": aluno.nome, "turno": n_turno, "ucs_inscritas": inscricoes_realizadas}, request)
        
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
    unidades = UnidadeCurricular.objects.filter(id_curso_id=3).select_related('id_anocurricular', 'id_semestre').order_by('id_anocurricular__id_anocurricular', 'id_semestre__id_semestre')

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

#view estagio RSI
def estagio_rsi(request):
    return render(request, "rsi/estagio_rsi.html", { "area": "rsi" })

#view contactos RSI
def contactos_rsi(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "rsi/contactos_rsi.html", { "area": "rsi", "docentes": docentes })

#view avaliaçoes RSI
def avaliacoes_rsi(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano(AvaliacaoPDF, course_id=3)
    return render(request, "rsi/avaliacoes_rsi.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "rsi"})

#view para saidas profissionais RSI
def saidas_rsi(request):
    return render(request, "rsi/saidas_rsi.html", { "area": "rsi" })

#view horarios RSI
def horarios_rsi(request):
    horarios_por_ano = _listar_pdfs_por_ano(HorarioPDF, course_id=3)
    return render(request, "rsi/horarios_rsi.html", {"horarios_por_ano": horarios_por_ano, "area": "rsi"})

#view para pagina inicial DWDM
def index_dwdm(request):
    return render(request, "dwdm/index_dwdm.html", { "area": "dwdm" })

#view ingresso DWDM
def ingresso_dwdm(request):
    return render(request, "dwdm/ingresso_dwdm.html", { "area": "dwdm" })

#view para plano curricular DWDM
def plano_dwdm(request):
    unidades = UnidadeCurricular.objects.filter(id_curso_id=4).select_related('id_anocurricular', 'id_semestre').order_by('id_anocurricular__id_anocurricular', 'id_semestre__id_semestre')

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

#view para horarios DWDM
def horarios_dwdm(request):
    horarios_por_ano = _listar_pdfs_por_ano(HorarioPDF, course_id=4)
    return render(request, "dwdm/horarios_dwdm.html", {"horarios_por_ano": horarios_por_ano, "area": "dwdm"})

#view para avaliacoes DWDM
def avaliacoes_dwdm(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano(AvaliacaoPDF, course_id=4)
    return render(request, "dwdm/avaliacoes_dwdm.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "dwdm"})

#view para contactos DWDM
def contactos_dwdm(request):
    docentes = Docente.objects.all().order_by('nome')
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
    unidades = UnidadeCurricular.objects.filter(id_curso_id=5).select_related('id_anocurricular', 'id_semestre').order_by('id_anocurricular__id_anocurricular', 'id_semestre__id_semestre')

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

#view horarios do mestrado
def horarios_mestrado(request):
    horarios_por_ano = _listar_pdfs_por_ano(HorarioPDF, course_id=5)
    return render(request, "eisi/horarios_mestrado.html", {"horarios_por_ano": horarios_por_ano, "area": "eisi"})

#view avaliacoes do mestrado
def avaliacoes_mestrado(request):
    avaliacoes_por_ano = _listar_pdfs_por_ano(AvaliacaoPDF, course_id=5)
    return render(request, "eisi/avaliacoes_mestrado.html", {"avaliacoes_por_ano": avaliacoes_por_ano, "area": "eisi"})

#view contactos do mestrado
def contactos_mestrado(request):
    docentes = Docente.objects.all().order_by('nome')
    return render(request, "eisi/contactos_mestrado.html", { "area": "eisi", "docentes": docentes })

#view para listar UCs no admin
def admin_uc_list(request):
    ucs = UnidadeCurricular.objects.all().order_by("id_unidadecurricular")

    #filtro
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    curso = request.GET.get('curso')

    if ano:
        ucs = ucs.filter(id_anocurricular_id=ano)

    if semestre:
        ucs = ucs.filter(id_semestre_id=semestre)

    if curso:
        ucs = ucs.filter(id_curso_id=curso)

    #carrega as listas para agrupar por filtros
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

#view para criar UC
def admin_uc_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        ects = request.POST.get("ects")

        #cria UC com nome e ects
        uc = UnidadeCurricular.objects.create(nome=nome, ects=ects,)

        registar_log( request, operacao="CREATE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC criada: {uc.nome}")
        messages.success(request, "Unidade Curricular criada com sucesso!")
        return redirect("home:admin_uc_list")

    return render(request, "admin/uc_form.html", {"uc": None, "turnos_uc": [], "turnos_count": 0,},)

#view para editar UC
def admin_uc_edit(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)

    #obtem turnos associados a UC
    turnos_uc = (TurnoUc.objects.filter(id_unidadecurricular=uc).select_related("id_turno").order_by("id_turno__n_turno"))
    turnos_count = turnos_uc.count()

    if request.method == "POST":
        action = request.POST.get("action") or "update_uc"

        #atualizar apenas nome e ects
        if action == "update_uc":
            uc.nome = request.POST.get("nome")
            uc.ects = request.POST.get("ects")
            uc.save()

            registar_log(request, operacao="UPDATE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC atualizada: {uc.nome}",)
            messages.success(request, "Unidade Curricular atualizada!")
            return redirect("home:admin_uc_list")

        #adciionar um turno à UC
        if action == "add_turno":
            n_turno = request.POST.get("n_turno")
            tipo = request.POST.get("tipo")
            capacidade = request.POST.get("capacidade")
            hora_inicio = request.POST.get("hora_inicio")
            hora_fim = request.POST.get("hora_fim")
            
            #cria um turno ainda sem a conexao a UC
            novo_turno = Turno.objects.create(n_turno=n_turno or 0, tipo=tipo or "", capacidade=capacidade or 0,)

            #cria a relacao com os horarios
            TurnoUc.objects.create(id_turno=novo_turno, id_unidadecurricular=uc, hora_inicio=hora_inicio, hora_fim=hora_fim,)

            registar_log(request, operacao="CREATE", entidade="turno", chave=str(novo_turno.id_turno), detalhes=f"Turno criado para UC {uc.nome}",)
            messages.success(request, "Turno adicionado à UC!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

        #atualizar um turno da UC
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

            registar_log(request, operacao="UPDATE", entidade="turno", chave=str(turno.id_turno), detalhes=f"Turno atualizado para UC {uc.nome}",)
            messages.success(request, "Turno atualizado!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

        #apagar turno associado a UC
        if action == "delete_turno":
            turno_id = request.POST.get("turno_id")
            turno = get_object_or_404(Turno, id_turno=turno_id)

            TurnoUc.objects.filter(id_turno=turno).delete()
            turno.delete()

            registar_log(request, operacao="DELETE", entidade="turno", chave=str(turno_id), detalhes=f"Turno removido da UC {uc.nome}",)
            messages.success(request, "Turno removido!")
            return redirect("home:admin_uc_edit", id=uc.id_unidadecurricular)

    return render(request, "admin/uc_form.html", {"uc": uc, "turnos_uc": turnos_uc, "turnos_count": turnos_count,},)

#view para apagar UC
def admin_uc_delete(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)
    uc.delete()

    registar_log( request, operacao="DELETE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC apagada: {uc.nome}")
    messages.success(request, "Unidade Curricular apagada!")
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

    #query nos logs sql
    sql_qs = LogEvento.objects.all()
    if operacao_filter:
        sql_qs = sql_qs.filter(operacao__icontains=operacao_filter)
    if entidade_filter:
        sql_qs = sql_qs.filter(entidade__icontains=entidade_filter)
    sql_qs = sql_qs.order_by('-data_hora')[:limite]

    #converte logs SQL para uma lista de dicionários
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

    #obtem os logs em Mongo utiliazndo os mesmos filtros e limite
    mongo_logs = listar_eventos_mongo(filtro_acao=operacao_filter or None, filtro_entidade=entidade_filter or None, limite=limite,)

    #junta os logs do sql com os do mongo e oredena por data
    logs_unificados = sql_logs + mongo_logs
    logs_unificados = sorted(logs_unificados, key=lambda l: l.get("data") or datetime.min, reverse=True)[:limite]

    #carrega mais logs para construir listas de filtros
    mongo_all_for_filters = listar_eventos_mongo(limite=1000)
    operacoes = set(list(LogEvento.objects.values_list('operacao', flat=True).distinct()) + [l.get("operacao", "") for l in mongo_all_for_filters])
    entidades = set(list(LogEvento.objects.values_list('entidade', flat=True).distinct()) + [l.get("entidade", "") for l in mongo_all_for_filters])

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
    # Busca todas as propostas de estágio do MongoDB
    propostas = listar_propostas_estagio()
    
    # Regista a consulta para analytics
    adicionar_log(
        "visualizar_propostas_estagio",
        {"total_propostas": len(propostas)},
        request
    )
    
    return render(request, "dape/dape.html", {"propostas": propostas})


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

@login_required
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
        
        # Cria a proposta no MongoDB
        proposta = criar_proposta_estagio(
            aluno_id=aluno_id,
            aluno_nome=aluno_nome,
            titulo=titulo,
            descricao=descricao,
            empresa=empresa,
            orientador=orientador
        )
        
        # Regista log da criação
        adicionar_log(
            "criar_proposta_estagio",
            {
                "aluno_id": aluno_id,
                "titulo": titulo,
                "empresa": empresa
            },
            request
        )
        
        messages.success(request, "Proposta de estágio criada com sucesso!")
        return redirect("home:listar_propostas_estagio")
    
    return render(request, "proposta_estagio/criar.html")

@login_required
def listar_propostas_estagio_view(request):
    """View para listar propostas de estágio do aluno"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem ver suas propostas de estágio.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    # Lista propostas do aluno
    propostas = listar_propostas_estagio({"aluno_id": aluno_id})
    
    # Regista consulta
    adicionar_log(
        "listar_propostas_estagio",
        {"aluno_id": aluno_id, "total_propostas": len(propostas)},
        request
    )
    
    return render(request, "dape/dape.html", {"propostas": propostas})

@login_required
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
            updates["empresa"] = request.POST.get("empresa")
        if request.POST.get("orientador"):
            updates["orientador"] = request.POST.get("orientador")
        
        # Atualiza a proposta
        sucesso = atualizar_proposta_estagio(aluno_id, titulo, updates)
        
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
    propostas = listar_propostas_estagio({"aluno_id": aluno_id, "titulo": titulo})
    if not propostas:
        messages.error(request, "Proposta não encontrada.")
        return redirect("home:listar_propostas_estagio")
    
    proposta = propostas[0]
    return render(request, "dape/dape.html", {"proposta": proposta})

@login_required
def deletar_proposta_estagio_view(request, titulo):
    """View para deletar uma proposta de estágio"""
    if request.session.get("user_tipo") != "aluno":
        messages.error(request, "Apenas alunos podem deletar propostas de estágio.")
        return redirect("home:index")
    
    aluno_id = request.session.get("user_id")
    
    # Deleta a proposta
    sucesso = deletar_proposta_estagio(aluno_id, titulo)
    
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
