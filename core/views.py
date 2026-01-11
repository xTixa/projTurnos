from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from .models import AnoCurricular, UnidadeCurricular, Semestre, Docente, Curso, HorarioPDF, Aluno, TurnoUc, Turno, InscricaoTurno, InscritoUc, LogEvento
from .db_views import CadeirasSemestre, AlunosPorOrdemAlfabetica, Turnos, Cursos
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from bd2_projeto.services.mongo_service import adicionar_log, listar_logs
from core.utils import registar_log, admin_required


def index(request):
    return render(request, "di/index_di.html")

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # =========================
        # ADMIN (Django User)
        # =========================
        user = authenticate(
            request,
            username=username_or_email,
            password=password
        )

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
    # Busca todas as unidades, com joins automáticos
    unidades = UnidadeCurricular.objects.select_related('id_anocurricular', 'id_semestre').order_by(
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
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "Apenas alunos se podem inscrever em turnos.")
        return redirect("home:login")

    aluno = get_object_or_404(Aluno, n_mecanografico=request.session["user_id"])
    turno_uc = get_object_or_404(Turno, id_turno=turno_id)
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=uc_id)

    turno_uc_existe = TurnoUc.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).exists()
    if not turno_uc_existe:
        messages.error(request, "Este turno não pertence a esta UC.")
        return redirect("home:inscricao_turno")

    inscrito = InscritoUc.objects.filter(n_mecanografico=aluno, id_unidadecurricular=uc, estado=True).exists()
    if not inscrito:
        messages.error(request, "Não estás inscrito nesta UC.")
        return redirect("home:inscricao_turno")
    
    if InscricaoTurno.objects.filter(n_mecanografico=aluno, id_turno=turno_uc, id_unidadecurricular=uc).exists():
        messages.warning(request, "Já estás inscrito neste turno.")
        return redirect("home:inscricao_turno")

    ocupados = InscricaoTurno.objects.filter(id_turno=turno_uc, id_unidadecurricular=uc).count()
    if ocupados >= turno_uc.capacidade:
        messages.error(request, "Este turno já está cheio.")
        return redirect("home:inscricao_turno")

    InscricaoTurno.objects.create(n_mecanografico=aluno, id_turno=turno_uc, id_unidadecurricular=uc, data_inscricao=datetime.today().date())

    messages.success(request, "Inscrição no turno efetuada com sucesso!")
    return redirect("home:inscricao_turno")



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
        "chart_alunos_labels": chart_alunos_labels,
        "chart_alunos_values": chart_alunos_values,
        "vagas_ocupadas": vagas_ocupadas,
        "vagas_disponiveis": vagas_disponiveis,
    })

def admin_users_list(request):
    users = User.objects.all().order_by("id")
    return render(request, "admin/users_list.html", {"users": users})

def admin_users_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username e password são obrigatórios.")
            return redirect("admin_users_create")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Utilizador criado com sucesso!")
        return redirect("admin_users_list")

    return render(request, "admin/users_form.html")

def admin_users_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Utilizador atualizado!")
        return redirect("admin_users_list")

    return render(request, "admin/users_form.html", {"user": user})

def admin_users_delete(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.success(request, "Utilizador apagado!")
    return redirect("admin_users_list")

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
    return render(request, "di/contactos.html", { "area": "di" })


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
    return render(request, "tdm/plano_tdm.html", { "area": "tdm" })

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
    return render(request, "tdm/contactos_tdm.html", { "area": "tdm" })

def saidas_tdm(request):
    return render(request, "tdm/saidas.html", { "area": "tdm" })

def avaliacoes_tdm(request):
    return render(request, "tdm/avaliacoes_tdm.html", { "area": "tdm" })

def moodle(request):
    return render(request, "tdm/moodle.html", { "area": "tdm" })



#RSI
def index_rsi(request):
    return render(request, "rsi/index_rsi.html", { "area": "rsi" })

def ingresso_rsi(request):
    return render(request, "rsi/ingresso_rsi.html", { "area": "rsi" })

def plano_curric_rsi(request):
    return render(request, "rsi/plano_curric_rsi.html", { "area": "rsi" })

def estagio_rsi(request):
    return render(request, "rsi/estagio_rsi.html", { "area": "rsi" })

def contactos_rsi(request):
    return render(request, "rsi/contactos_rsi.html", { "area": "rsi" })

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
    return render(request, "dwdm/plano_dwdm.html", { "area": "dwdm" })

def horarios_dwdm(request):
    return render(request, "dwdm/horarios_dwdm.html", { "area": "dwdm" })

def avaliacoes_dwdm(request):
    return render(request, "dwdm/avaliacoes_dwdm.html", { "area": "dwdm" })

def contactos_dwdm(request):
    return render(request, "dwdm/contactos_dwdm.html", { "area": "dwdm" })

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
    return render(request, "eisi/plano_curric_mestrado.html", { "area": "eisi" })

def horarios_mestrado(request):
    return render(request, "eisi/horarios_mestrado.html", { "area": "eisi" })

def avaliacoes_mestrado(request):
    return render(request, "eisi/avaliacoes_mestrado.html", { "area": "eisi" })

def contactos_mestrado(request):
    return render(request, "eisi/contactos_mestrado.html")



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

    return render(request, "admin/uc_form.html")

def admin_uc_edit(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)

    if request.method == "POST":
        uc.nome = request.POST.get("nome")
        uc.ects = request.POST.get("ects")
        uc.save()

        registar_log( request, operacao="UPDATE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC atualizada: {uc.nome}")

        messages.success(request, "Unidade Curricular atualizada!")
        return redirect("home:admin_uc_list")

    return render(request, "admin/uc_form.html", {"uc": uc})

def admin_uc_delete(request, id):
    uc = get_object_or_404(UnidadeCurricular, id_unidadecurricular=id)
    uc.delete()

    registar_log( request, operacao="DELETE", entidade="unidade_curricular", chave=str(uc.id_unidadecurricular), detalhes=f"UC apagada: {uc.nome}")
    messages.success(request, "Unidade Curricular apagada!")
    return redirect("home:admin_uc_list")



def admin_logs_list(request):
    # Filtrar por operação
    operacao_filter = request.GET.get('operacao', '')
    entidade_filter = request.GET.get('entidade', '')
    
    logs = LogEvento.objects.all()
    
    if operacao_filter:
        logs = logs.filter(operacao__icontains=operacao_filter)
    
    if entidade_filter:
        logs = logs.filter(entidade__icontains=entidade_filter)
    
    logs = logs[:500]
    
    # Obter lista de operações para os filtros
    operacoes = LogEvento.objects.values_list('operacao', flat=True).distinct().order_by('operacao')
    entidades = LogEvento.objects.values_list('entidade', flat=True).distinct().order_by('entidade')

    return render(request, "admin/logs_list.html", {
        "logs": logs,
        "operacoes": operacoes,
        "entidades": entidades,
        "operacao_filter": operacao_filter,
        "entidade_filter": entidade_filter,
    })

# ==========================
# Forum
# ==========================

def forum(request):
    return render(request, "forum/index_forum.html")
