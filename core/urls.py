from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("ingresso/", views.ingresso, name="ingresso"),
    path("plano/", views.plano_curricular, name="plano"),
    path("horarios/", views.horarios, name="horarios"),
    path("avaliacoes/", views.avaliacoes, name="avaliacoes"),
    path("contactos/", views.contactos, name="contactos"),
    path("informacoes/", views.informacoes, name="informacoes"),
    path("perfil/", views.perfil, name="perfil"),
    path("login/",  auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", views.do_logout, name="logout"),

    path("inscricao_turno/", views.inscricao_turno, name="inscricao_turno"),
    path("turnos/inscrever/<int:turno_id>/", views.inscrever_turno, name="inscrever_turno"),



    #ficha 12
    path("4etcs/", views.uc_mais_4_ects, name="uc_mais_4_ects"),
    path("cadeiras_semestre/", views.cadeiras_semestre, name="cadeiras_semestre"),
    path("vw_alunos_matriculas_por_dia/", views.alunos_matriculados_por_dia, name="vw_alunos_matriculados_por_dia"),
    path("vw_alunos_por_ordem_alfabetica/", views.alunos_por_ordem_alfabetica, name="vw_alunos_por_ordem_alfabetica"),
    path("turnos_list/", views.turnos_list, name="turnos_list"),
    path("cursos_list/", views.cursos_list, name="cursos_list"),
    path("top_docente_uc_ano_corrente/", views.top_docente_uc_ano_corrente, name="top_docente_uc_ano_corrente"),
    path("alunos_inscricoes_2025/", views.alunos_inscricoes_2025, name="alunos_inscricoes_2025"),

]
