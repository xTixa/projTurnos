from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from huggingface_hub import logout
from .models import UnidadeCurricular, Docente, Curso, HorarioPDF, Aluno, TurnoUc, Turno, InscricaoTurno, InscritoUc
from .db_views import UCMais4Ects, CadeirasSemestre, AlunosMatriculadosPorDia, AlunosPorOrdemAlfabetica, Turnos, Cursos
from django.http import JsonResponse
from .models import VwTopDocenteUcAnoCorrente
from .models import VwAlunosInscricoes2025
from django.contrib.auth.models import User
from bd2_projeto.services.mongo_service import adicionar_log, listar_logs

def index(request):
    return render(request, "home/index.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # 1) Tentar autenticar ALUNO
        try:
            aluno = Aluno.objects.get(email=email)

            if aluno.password == password:
                request.session["user_tipo"] = "aluno"
                request.session["user_id"] = aluno.n_mecanografico
                request.session["user_nome"] = aluno.nome
                request.session["user_email"] = aluno.email
                return redirect("home:index")
            else:
                messages.error(request, "Password incorreta.")
                return redirect("home:login")

        except Aluno.DoesNotExist:
            pass

        # 2) Tentar autenticar DOCENTE
        try:
            docente = Docente.objects.get(email=email)

            if hasattr(docente, "password") and docente.password == password:
                request.session["user_tipo"] = "docente"
                request.session["user_id"] = docente.id_docente
                request.session["user_nome"] = docente.nome
                request.session["user_email"] = docente.email
                return redirect("home:index")

            else:
                messages.error(request, "Password incorreta.")
                return redirect("home:login")

        except Docente.DoesNotExist:
            pass

        # Se não encontrou em lado nenhum
        messages.error(request, "Utilizador não encontrado.")
        return redirect("home:login")

    return render(request, "auth/login.html")

def ingresso(request):
    return render(request, "home/ingresso.html")

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

    return render(request, "home/plano_curricular.html", {"plano": plano})

def horarios(request):
    horarios = {
        "1º Ano": [
            {"dia": "Segunda", "hora": "08:30 - 10:00", "uc": "Programação I", "sala": "Lab 1", "turno": "TP A"},
            {"dia": "Terça", "hora": "10:00 - 11:30", "uc": "Matemática Discreta", "sala": "A1.2", "turno": "T"},
            {"dia": "Quinta", "hora": "09:00 - 10:30", "uc": "Bases de Dados I", "sala": "A2.1", "turno": "T"},
        ],
        "2º Ano": [
            {"dia": "Segunda", "hora": "14:00 - 15:30", "uc": "Programação para Dispositivos Móveis", "sala": "Lab 2", "turno": "TP"},
            {"dia": "Quarta", "hora": "09:00 - 10:30", "uc": "Engenharia de Software", "sala": "A3.2", "turno": "T"},
        ],
        "3º Ano": [
            {"dia": "Terça", "hora": "08:30 - 10:00", "uc": "Sistemas Distribuídos", "sala": "Lab 5", "turno": "TP"},
            {"dia": "Sexta", "hora": "10:30 - 12:00", "uc": "Inteligência Artificial", "sala": "A4.1", "turno": "T"},
        ]
    }

    # Marcar conflitos dentro de cada ano
    for ano, lista in horarios.items():
        for i, h in enumerate(lista):
            h["conflito"] = any(
                i != j and h["dia"] == o["dia"] and h["hora"] == o["hora"]
                for j, o in enumerate(lista)
            )

    return render(request, "home/horarios.html", {"horarios_por_ano": horarios})


def avaliacoes(request):
    avaliacoes_docs = [
        {"ano": "1º Ano", "ficheiro": "avaliacoes_1ano.pdf"},
        {"ano": "2º Ano", "ficheiro": "avaliacoes_2ano.pdf"},
        {"ano": "3º Ano", "ficheiro": "avaliacoes_3ano.pdf"},
    ]
    return render(request, "home/avaliacoes.html", {"avaliacoes_docs": avaliacoes_docs})

def contactos(request):
    # Buscar todos os docentes
    docentes = Docente.objects.all().order_by('nome')

    # Buscar dados do curso principal (por exemplo Engenharia Informática)
    curso = Curso.objects.filter(nome__icontains="Engenharia Informática").first()

    contexto = {
        "curso": curso,
        "docentes": docentes
    }
    return render(request, "home/contactos.html", contexto)

def inscricao_turno(request):

    # --- 1) Obter aluno autenticado ---
    if "user_tipo" not in request.session or request.session["user_tipo"] != "aluno":
        messages.error(request, "É necessário iniciar sessão como aluno.")
        return redirect("home:login")

    n_meca = request.session["user_id"]
    aluno = Aluno.objects.get(n_mecanografico=n_meca)

    # --- 2) Buscar APENAS as UCs em que o aluno está inscrito ---
    inscricoes = InscritoUc.objects.filter(
        n_mecanografico=aluno,
        estado=True
    ).values('id_unidadecurricular')

    lista_uc = []

    for inscricao in inscricoes:
        uc_id = inscricao['id_unidadecurricular']
        uc = UnidadeCurricular.objects.get(id_unidadecurricular=uc_id)

        # --- 3) Buscar os turnos dessa UC ---
        relacoes = TurnoUc.objects.filter(id_unidadecurricular=uc)

        turnos = []
        for r in relacoes:
            turno = r.id_turno  # Turno real

            # 4) Calcular vagas ocupadas
            ocupados = InscricaoTurno.objects.filter(id_turno=r).count()
            vagas = turno.capacidade - ocupados
            if vagas < 0:
                vagas = 0

            turnos.append({
                "id": turno.id_turno,
                "nome": f"T{turno.n_turno}",
                "tipo": turno.tipo,
                "capacidade": turno.capacidade,
                "vagas": vagas,
                "horario": "A definir"
            })

        lista_uc.append({
            "id": uc.id_unidadecurricular,
            "nome": uc.nome,
            "turnos": turnos,
        })

    # --- Horário e dias ---
    horas = [
        "08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30",
        "12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30",
        "16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30",
        "20:00","20:30","21:00","21:30","22:00","22:30","23:00","23:30"
    ]

    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    return render(request, "home/inscricao_turno.html", {
        "unidades": lista_uc,
        "horas": horas,
        "dias": dias
    })

def informacoes(request):
    return render(request, "home/informacoes.html")

def perfil(request):
    return render(request, "profile/perfil.html")

def do_logout(request):
    auth_logout(request)                 # termina a sessão
    return redirect("home:index")        # redireciona para a home

@login_required
def inscrever_turno(request, turno_id):
    if request.method != "POST":
        messages.error(request, "Método inválido. Usa o botão para te inscreveres.")
        return redirect("home:perfil")

    # (futuro) lógica real de BD; por agora só feedback
    messages.success(request, f"Inscrição no turno #{turno_id} concluída com sucesso")
    return redirect("home:perfil")

#ficha 12
def uc_mais_4_ects(request):
    data = list(
        UCMais4Ects.objects
        .order_by('id_anocurricular', 'id_semestre', 'nome')
        .values('id_unidadecurricular', 'nome', 'ects', 'id_anocurricular', 'id_semestre')
    )
    return JsonResponse(data, safe=False)

def cadeiras_semestre(request):
    data = list(
        CadeirasSemestre.objects
        .order_by('semestre_id', 'nome')
        .values('id_unidadecurricular', 'nome', 'ects', 'semestre_id', 'semestre_nome')
    )
    return JsonResponse(data, safe=False)

def alunos_matriculados_por_dia(request):
    data = list(
        AlunosMatriculadosPorDia.objects
        .order_by('ano_matricula', 'dia_matricula', 'nome')
        .values('id_matricula', 'n_mecanografico', 'nome', 'email', 'estado', 'data_matricula', 'dia_matricula', 'ano_matricula')
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


def top_docente_uc_ano_corrente(request):
    data = list(
        VwTopDocenteUcAnoCorrente.objects
        .all()
        .values('id_docente', 'nome', 'email', 'total_ucs')
    )
    return JsonResponse(data, safe=False)

def alunos_inscricoes_2025(request):
    data = list(
        VwAlunosInscricoes2025.objects
        .all()
        .values(
            'id_inscricao',
            'data_inscricao',
            'n_mecanografico',
            'aluno_nome',
            'aluno_email',
            'id_unidadecurricular',
            'uc_nome',
            'id_turno'
        )
    )
    return JsonResponse(data, safe=False)


# Dashboard
def admin_dashboard(request):
    total_users = User.objects.count()
    total_turnos = Turnos.objects.count()
    total_ucs = UnidadeCurricular.objects.count()
    total_horarios = HorarioPDF.objects.count()

    return render(request, "admin/dashboard.html", {
        "total_users": total_users,
        "total_turnos": total_turnos,
        "total_ucs": total_ucs,
        "total_horarios": total_horarios,
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

        Turnos.objects.create(
            n_turno=n_turno,
            capacidade=capacidade,
            tipo=tipo,
        )
        messages.success(request, "Turno criado com sucesso!")
        return redirect("admin_turnos_list")

    return render(request, "admin/turnos_form.html")

def admin_turnos_edit(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)

    if request.method == "POST":
        turno.n_turno = request.POST.get("n_turno")
        turno.capacidade = request.POST.get("capacidade")
        turno.tipo = request.POST.get("tipo")
        turno.save()

        messages.success(request, "Turno atualizado!")
        return redirect("admin_turnos_list")

    return render(request, "admin/turnos_form.html", {"turno": turno})

def admin_turnos_delete(request, id):
    turno = get_object_or_404(Turnos, id_turno=id)
    turno.delete()
    messages.success(request, "Turno apagado!")
    return redirect("admin_turnos_list")

# ==========================
# ADMIN — HORÁRIOS CRUD
# ==========================

def admin_horarios_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        ficheiro = request.FILES.get("ficheiro")

        if not ficheiro:
            messages.error(request, "É necessário enviar um ficheiro PDF.")
            return redirect("home:admin_horarios_create")

        HorarioPDF.objects.create(
            nome=nome,
            ficheiro=ficheiro
        )

        messages.success(request, "Horário carregado com sucesso!")
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html")

def admin_horarios_edit(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)

    if request.method == "POST":
        horario.nome = request.POST.get("nome")

        if "ficheiro" in request.FILES:
            horario.ficheiro = request.FILES["ficheiro"]

        horario.save()
        messages.success(request, "Horário atualizado!")
        return redirect("home:admin_horarios_list")

    return render(request, "admin/horarios_form.html", {"horario": horario})

def admin_horarios_delete(request, id):
    horario = get_object_or_404(HorarioPDF, id=id)
    horario.delete()
    messages.success(request, "Horário apagado!")
    return redirect("home:admin_horarios_list")

def admin_horarios_list(request):
    horarios = HorarioPDF.objects.all().order_by("-atualizado_em")
    return render(request, "admin/horarios_list.html", {"horarios": horarios})

def horarios(request):
    pdf = HorarioPDF.objects.order_by("-atualizado_em").first()
    return render(request, "home/horarios.html", {"pdf": pdf})

def admin_users_docentes(request):
    docentes = User.objects.filter(tipo="docente")
    return render(request, "admin/users_filter.html", {
        "titulo": "Docentes",
        "users": docentes
    })

def admin_users_alunos(request):
    alunos = User.objects.filter(tipo="aluno")
    return render(request, "admin/users_filter.html", {
        "titulo": "Alunos",
        "users": alunos
    })

def admin_logout(request):
    logout(request)
    return redirect("home:admin_login")

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
