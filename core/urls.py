from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from core.views import testar_mongo

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
   # path("login/",  auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
   path("login/", views.login_view, name="login"),
    path("logout/", views.do_logout, name="logout"),

    path("ei/inscricao_turno/", views.inscricao_turno, name="inscricao_turno"),
    path("turnos/inscrever/<int:turno_id>/", views.inscrever_turno, name="inscrever_turno"),

    # Painel Admin
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/logout/", views.admin_logout, name="admin_logout"),
    # ADMIN – ENGENHARIA INFORMÁTICA
    path("admin-panel/ei/ingresso/", views.admin_ei_ingresso, name="admin_ei_ingresso"),
    path("admin-panel/ei/saidas/", views.admin_ei_saidas, name="admin_ei_saidas"),
    path("admin-panel/ei/plano/", views.admin_ei_plano, name="admin_ei_plano"),
    path("admin-panel/ei/horarios/", views.admin_ei_horarios, name="admin_ei_horarios"),
    path("admin-panel/ei/avaliacoes/", views.admin_ei_avaliacoes, name="admin_ei_avaliacoes"),
    path("admin-panel/ei/contactos/", views.admin_ei_contactos, name="admin_ei_contactos"),

    # --------------------------
    # ADMIN — CURSOS (HOME)
    # --------------------------
    #path("admin-panel/cursos/", views.admin_cursos_home, name="admin_cursos_home"),

    # --------------------------
    # ADMIN — CURSOS INDIVIDUAIS
    # --------------------------
    #path("admin-panel/cursos/ei/", views.admin_ei_home, name="admin_ei_home"),
    #path("admin-panel/cursos/tdm/", views.admin_tdm_home, name="admin_tdm_home"),
    #path("admin-panel/cursos/rsi/", views.admin_rsi_home, name="admin_rsi_home"),
    #path("admin-panel/cursos/eisi/", views.admin_eisi_home, name="admin_eisi_home"),
    #path("admin-panel/cursos/dwdm/", views.admin_dwdm_home, name="admin_dwdm_home"),

    # --------------------
    # ADMIN — EISI (MESTRADO)
    # --------------------
    #path("admin-panel/cursos/eisi/", views.admin_eisi_home, name="admin_eisi_home"),

    #path("admin-panel/cursos/eisi/ingresso/", views.admin_eisi_ingresso, name="admin_eisi_ingresso"),
    #path("admin-panel/cursos/eisi/destinatarios/", views.admin_eisi_destinatarios, name="admin_eisi_destinatarios"),
    #path("admin-panel/cursos/eisi/plano/", views.admin_eisi_plano, name="admin_eisi_plano"),
    #path("admin-panel/cursos/eisi/horarios/", views.admin_eisi_horarios, name="admin_eisi_horarios"),
    #path("admin-panel/cursos/eisi/avaliacoes/", views.admin_eisi_avaliacoes, name="admin_eisi_avaliacoes"),
    #path("admin-panel/cursos/eisi/testemunhos/", views.admin_eisi_testemunhos, name="admin_eisi_testemunhos"),
    #path("admin-panel/cursos/eisi/contactos/", views.admin_eisi_contactos, name="admin_eisi_contactos"),



    # Users
    #path("admin-panel/users/", views.admin_users_list, name="admin_users_list"),
    #path("admin-panel/users/create/", views.admin_users_create, name="admin_users_create"),
    #path("admin-panel/users/<int:id>/edit/", views.admin_users_edit, name="admin_users_edit"),
    #path("admin-panel/users/<int:id>/delete/", views.admin_users_delete, name="admin_users_delete"),
    #path("admin-panel/users/docentes/", views.admin_users_docentes, name="admin_users_docentes"),
    #path("admin-panel/users/alunos/", views.admin_users_alunos, name="admin_users_alunos"),

    # Turnos
    #path("admin-panel/turnos/", views.admin_turnos_list, name="admin_turnos_list"),
    #path("admin-panel/turnos/create/", views.admin_turnos_create, name="admin_turnos_create"),
    #path("admin-panel/turnos/<int:id>/edit/", views.admin_turnos_edit, name="admin_turnos_edit"),
    #path("admin-panel/turnos/<int:id>/delete/", views.admin_turnos_delete, name="admin_turnos_delete"),

    # HORARIOS ADMIN (AJUSTADO)
    #path("admin-panel/horarios/", views.admin_horarios_list, name="admin_horarios_list"),
    #path("admin-panel/horarios/novo/", views.admin_horarios_create, name="admin_horarios_create"),
    #path("admin-panel/horarios/<int:id>/editar/", views.admin_horarios_edit, name="admin_horarios_edit"),
    #path("admin-panel/horarios/<int:id>/apagar/", views.admin_horarios_delete, name="admin_horarios_delete"),

    #ficha 12
    path("4etcs/", views.uc_mais_4_ects, name="uc_mais_4_ects"),
    path("cadeiras_semestre/", views.cadeiras_semestre, name="cadeiras_semestre"),
    path("vw_alunos_matriculas_por_dia/", views.alunos_matriculados_por_dia, name="vw_alunos_matriculados_por_dia"),
    path("vw_alunos_por_ordem_alfabetica/", views.alunos_por_ordem_alfabetica, name="vw_alunos_por_ordem_alfabetica"),
    path("turnos_list/", views.turnos_list, name="turnos_list"),
    path("cursos_list/", views.cursos_list, name="cursos_list"),
    path("top_docente_uc_ano_corrente/", views.top_docente_uc_ano_corrente, name="top_docente_uc_ano_corrente"),
    path("alunos_inscricoes_2025/", views.alunos_inscricoes_2025, name="alunos_inscricoes_2025"),

    # MONGO TESTE
    path("testar-mongo/", testar_mongo, name="testar_mongo"),


    #DI
    path("di/", views.index_di, name="index_di"),
    path("di/recursos/", views.recursos_di, name="recursos_di"),
    path("di/sobre/", views.sobre_di, name="sobre_di"),
    path("di/contactos/", views.contacto_di, name="contacto_di"),

    #EI
    path("ei/", views.index_ei, name="index"),

    #TDM
    path("tdm/", views.index_tdm, name="index_tdm"),
    path("tdm/ingresso/", views.ingresso_tdm, name="ingresso_tdm"),
    path("tdm/plano/", views.plano_tdm, name="plano_tdm"),
    path("tdm/horarios/", views.horarios_tdm, name="horarios_tdm"),
    path("tdm/contactos/", views.contactos_tdm, name="contactos_tdm"),
    path("tdm/avaliacoes/", views.avaliacoes_tdm, name="avaliacoes_tdm"),
    path("tdm/saidas/", views.saidas_tdm, name="saidas"),
    path("tdm/moodle/", views.moodle, name="moodle"),

    #RSI
    path("rsi/", views.index_rsi, name="index_rsi"),
    path("rsi/estagio/", views.estagio_rsi, name="estagio_rsi"),
    path("rsi/contactos/", views.contactos_rsi, name="contactos_rsi"),
    path("rsi/ingresso/", views.ingresso_rsi, name="ingresso_rsi"),
    path("rsi/plano/", views.plano_curric_rsi, name="plano_curric_rsi"),
    path("rsi/horarios/", views.horarios_rsi, name="horarios_rsi"),
    path("rsi/avaliacoes/", views.avaliacoes_rsi, name="avaliacoes_rsi"),
    path("rsi/saidas/", views.saidas_rsi, name="saidas_rsi"),

    #DWDM
    path("dwdm/", views.index_dwdm, name="index_dwdm"),
    path("dwdm/ingresso/", views.ingresso_dwdm, name="ingresso_dwdm"),
    path("dwdm/plano/", views.plano_dwdm, name="plano_dwdm"),
    path("dwdm/horarios/", views.horarios_dwdm, name="horarios_dwdm"),
    path("dwdm/avaliacoes/", views.avaliacoes_dwdm, name="avaliacoes_dwdm"),
    path("dwdm/contactos/", views.contactos_dwdm, name="contactos_dwdm"),
    path("dwdm/estagio/", views.estagio_dwdm, name="estagio_dwdm"),
    path("dwdm/saidas/", views.saidas_dwdm, name="saidas_dwdm"),
    path("dwdm/brightstart/", views.brightstart, name="brightstart"),

    #EISI
    path("eisi/", views.index_mestrado, name="index_mestrado"),
    path("eisi/testemunhos/", views.testemunho_mestrado, name="testemunho_mestrado"),
    path("eisi/ingresso/", views.ingresso_mestrado, name="ingresso_mestrado"),
    path("eisi/destinatarios/", views.destinatarios_mestrado, name="destinatarios_mestrado"),
    path("eisi/plano/", views.plano_curric_mestrado, name="plano_curric_mestrado"),
    path("eisi/horarios/", views.horarios_mestrado, name="horarios_mestrado"),
    path("eisi/avaliacoes/", views.avaliacoes_mestrado, name="avaliacoes_mestrado"),
    path("eisi/contactos/", views.contactos_mestrado, name="contactos_mestrado"),


    # Fórum
    path("forum/", views.forum, name="index_forum"),
]

