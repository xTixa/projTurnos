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
    path("turnos/inscrever/<int:turno_id>/<int:uc_id>/", views.inscrever_turno, name="inscrever_turno"),

    # Painel Admin
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/logs/", views.admin_logs_list, name="admin_logs_list"),

    # ADMIN – UNIDADE CURRICULAR
    path("admin-panel/uc/", views.admin_uc_list, name="admin_uc_list"),
    path("admin-panel/uc/create/", views.admin_uc_create, name="admin_uc_create"),
    path("admin-panel/uc/<int:id>/edit/", views.admin_uc_edit, name="admin_uc_edit"),
    path("admin-panel/uc/<int:id>/delete/", views.admin_uc_delete, name="admin_uc_delete"),


    # ADMIN – ENGENHARIA INFORMÁTICA
    path("admin-panel/ei/ingresso/", views.admin_ei_ingresso, name="admin_ei_ingresso"),
    path("admin-panel/ei/saidas/", views.admin_ei_saidas, name="admin_ei_saidas"),
    path("admin-panel/ei/plano/", views.admin_ei_plano, name="admin_ei_plano"),
    path("admin-panel/ei/horarios/", views.admin_ei_horarios, name="admin_ei_horarios"),
    path("admin-panel/ei/avaliacoes/", views.admin_ei_avaliacoes, name="admin_ei_avaliacoes"),
    path("admin-panel/ei/contactos/", views.admin_ei_contactos, name="admin_ei_contactos"),


    # Users
    path("admin-panel/users/", views.admin_users_list, name="admin_users_list"),
    path("admin-panel/users/create/", views.admin_users_create, name="admin_users_create"),
    path("admin-panel/users/<int:id>/edit/", views.admin_users_edit, name="admin_users_edit"),
    path("admin-panel/users/<int:id>/delete/", views.admin_users_delete, name="admin_users_delete"),
    path("admin-panel/users/docentes/", views.admin_users_docentes, name="admin_users_docentes"),
    path("admin-panel/users/alunos/", views.admin_users_alunos, name="admin_users_alunos"),

    # Turnos
    path("admin-panel/turnos/", views.admin_turnos_list, name="admin_turnos_list"),
    path("admin-panel/turnos/create/", views.admin_turnos_create, name="admin_turnos_create"),
    path("admin-panel/turnos/<int:id>/edit/", views.admin_turnos_edit, name="admin_turnos_edit"),
    path("admin-panel/turnos/<int:id>/delete/", views.admin_turnos_delete, name="admin_turnos_delete"),
    path("admin-panel/turnos/", views.admin_turnos_list, name="admin_turnos_list"),

    # HORARIOS ADMIN (AJUSTADO)
    path("admin-panel/horarios/", views.admin_horarios_list, name="admin_horarios_list"),
    path("admin-panel/horarios/novo/", views.admin_horarios_create, name="admin_horarios_create"),
    path("admin-panel/horarios/<int:id>/editar/", views.admin_horarios_edit, name="admin_horarios_edit"),
    path("admin-panel/horarios/<int:id>/apagar/", views.admin_horarios_delete, name="admin_horarios_delete"),

    #ficha 12
    path("cadeiras_semestre/", views.cadeiras_semestre, name="cadeiras_semestre"),
    path("vw_alunos_por_ordem_alfabetica/", views.alunos_por_ordem_alfabetica, name="vw_alunos_por_ordem_alfabetica"),
    path("turnos_list/", views.turnos_list, name="turnos_list"),
    path("cursos_list/", views.cursos_list, name="cursos_list"),

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

