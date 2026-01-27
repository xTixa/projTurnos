from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import analytics_views
from . import export_views
from . import import_views
from core.views import testar_mongo

app_name = "home"

urlpatterns = [
    # Importação de alunos
    path("admin-panel/import/alunos/csv/", import_views.importar_alunos_csv, name="import_alunos_csv"),
    path("admin-panel/import/alunos/json/", import_views.importar_alunos_json, name="import_alunos_json"),
    path("admin-panel/import/alunos/xml/", import_views.importar_alunos_xml, name="import_alunos_xml"),
    path("admin-panel/import/", import_views.admin_import_data, name="admin_import_data"),
    path("", views.index, name="index"),
    path("ingresso/", views.ingresso, name="ingresso"),
    path("plano/", views.plano_curricular, name="plano"),
    path("horarios/", views.horarios, name="horarios"),
    path("avaliacoes/", views.avaliacoes, name="avaliacoes"),
    path("contactos/", views.contactos, name="contactos"),
    path("informacoes/", views.informacoes, name="informacoes"),
    path("perfil/", views.perfil, name="perfil"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.do_logout, name="logout"),

    path("ei/inscricao_turno/", views.inscricao_turno, name="inscricao_turno"),
    path("turnos/inscrever/<int:turno_id>/<int:uc_id>/", views.inscrever_turno, name="inscrever_turno"),
    path("turnos/desinscrever/<int:turno_id>/<int:uc_id>/", views.desinscrever_turno, name="desinscrever_turno"),
    path("api/turnos/conflitos/<int:turno_id>/", views.api_verificar_conflitos, name="api_verificar_conflitos"),

    # Painel Admin
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/logs/", views.admin_logs_list, name="admin_logs_list"),
    path("admin-panel/export/", views.admin_export_data, name="admin_export_data"),
    
    # ANALYTICS — ANÁLISE DE DADOS (MongoDB)
    path("admin-panel/analytics/inscricoes/", analytics_views.analytics_inscricoes, name="analytics_inscricoes"),
    path("api/analytics/inscricoes-dia/", analytics_views.analytics_api_inscricoes_dia, name="api_inscricoes_dia"),
    path("api/analytics/taxa-sucesso/", analytics_views.analytics_api_taxa_sucesso, name="api_taxa_sucesso"),
    path("api/analytics/alunos-ativos/", analytics_views.analytics_api_alunos_ativos, name="api_alunos_ativos"),
    path("api/analytics/ucs-procuradas/", analytics_views.analytics_api_ucs_procuradas, name="api_ucs_procuradas"),

    # Exportação geral
    path("admin-panel/export/alunos/csv/", export_views.exportar_alunos_csv, name="export_alunos_csv"),
    path("admin-panel/export/alunos/json/", export_views.exportar_alunos_json, name="export_alunos_json"),
    path("admin-panel/export/alunos/xml/", export_views.exportar_alunos_xml, name="export_alunos_xml"),
    path("admin-panel/export/turnos/csv/", export_views.exportar_turnos_csv, name="export_turnos_csv"),
    path("admin-panel/export/turnos/json/", export_views.exportar_turnos_json, name="export_turnos_json"),
    path("admin-panel/export/turnos/xml/", export_views.exportar_turnos_xml, name="export_turnos_xml"),
    path("admin-panel/export/inscricoes/csv/", export_views.exportar_inscricoes_csv, name="export_inscricoes_csv"),
    path("admin-panel/export/inscricoes/json/", export_views.exportar_inscricoes_json, name="export_inscricoes_json"),
    path("admin-panel/export/inscricoes/xml/", export_views.exportar_inscricoes_xml, name="export_inscricoes_xml"),
    path("admin-panel/export/ucs/csv/", export_views.exportar_ucs_csv, name="export_ucs_csv"),
    path("admin-panel/export/ucs/json/", export_views.exportar_ucs_json, name="export_ucs_json"),
    path("admin-panel/export/ucs/xml/", export_views.exportar_ucs_xml, name="export_ucs_xml"),
    
    # Exportação de vistas materializadas
    path("admin-panel/export/mv/estatisticas-turno/csv/", export_views.exportar_mv_estatisticas_turno_csv, name="export_mv_estatisticas_csv"),
    path("admin-panel/export/mv/estatisticas-turno/json/", export_views.exportar_mv_estatisticas_turno_json, name="export_mv_estatisticas_json"),
    path("admin-panel/export/mv/estatisticas-turno/xml/", export_views.exportar_mv_estatisticas_xml, name="export_mv_estatisticas_xml"),
    path("admin-panel/export/mv/ucs-preenchidas/csv/", export_views.exportar_mv_ucs_preenchidas_csv, name="export_mv_ucs_preenchidas_csv"),
    path("admin-panel/export/mv/ucs-preenchidas/json/", export_views.exportar_mv_ucs_preenchidas_json, name="export_mv_ucs_preenchidas_json"),
    path("admin-panel/export/mv/ucs-preenchidas/xml/", export_views.exportar_mv_ucs_preenchidas_xml, name="export_mv_ucs_preenchidas_xml"),
    path("admin-panel/export/mv/resumo-alunos/csv/", export_views.exportar_mv_resumo_alunos_csv, name="export_mv_resumo_alunos_csv"),
    path("admin-panel/export/mv/resumo-alunos/json/", export_views.exportar_mv_resumo_alunos_json, name="export_mv_resumo_alunos_json"),
    path("admin-panel/export/mv/resumo-alunos/xml/", export_views.exportar_mv_resumo_alunos_xml, name="export_mv_resumo_alunos_xml"),
    
    # Atualizar vistas materializadas
    path("admin-panel/export/mv/refresh/", export_views.atualizar_vistas_materializadas, name="refresh_materialized_views"),

    # ADMIN – UNIDADE CURRICULAR
    path("admin-panel/uc/", views.admin_uc_list, name="admin_uc_list"),
    path("admin-panel/uc/create/", views.admin_uc_create, name="admin_uc_create"),
    path("admin-panel/uc/<int:id>/edit/", views.admin_uc_edit, name="admin_uc_edit"),
    path("admin-panel/uc/<int:id>/delete/", views.admin_uc_delete, name="admin_uc_delete"),

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

    # AVALIACOES ADMIN
    path("admin-panel/avaliacoes/", views.admin_avaliacoes_list, name="admin_avaliacoes_list"),
    path("admin-panel/avaliacoes/novo/", views.admin_avaliacoes_create, name="admin_avaliacoes_create"),
    path("admin-panel/avaliacoes/<int:id>/editar/", views.admin_avaliacoes_edit, name="admin_avaliacoes_edit"),
    path("admin-panel/avaliacoes/<int:id>/apagar/", views.admin_avaliacoes_delete, name="admin_avaliacoes_delete"),

    # ADMIN - PROPOSTAS DAPE
    path("admin-panel/dape/", views.admin_dape_list, name="admin_dape_list"),
    path("admin-panel/dape/create/", views.admin_dape_create, name="admin_dape_create"),
    path("admin-panel/dape/<int:id>/edit/", views.admin_dape_edit, name="admin_dape_edit"),
    path("admin-panel/dape/<int:id>/delete/", views.admin_dape_delete, name="admin_dape_delete"),

    #ficha 12
    path("cadeiras_semestre/", views.cadeiras_semestre, name="cadeiras_semestre"),
    path("vw_alunos_por_ordem_alfabetica/", views.alunos_por_ordem_alfabetica, name="vw_alunos_por_ordem_alfabetica"),
    path("turnos_list/", views.turnos_list, name="turnos_list"),
    path("cursos_list/", views.cursos_list, name="cursos_list"),

    # MONGO
    path("testar-mongo/", testar_mongo, name="testar_mongo"),
    path("pdf-mongodb/<str:tipo_pdf>/<str:file_id>/", views.servir_pdf_mongodb, name="servir_pdf_mongodb"),

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

    # DAPE
    path("dape/", views.dape, name="index_dape"),
    path("dape/contactos/", views.contactos_dape, name="contactos_dape"),
    path("dape/documentos/", views.documentos_dape, name="documentos_dape"),

    # Propostas de Estágio
    path("proposta-estagio/criar/", views.criar_proposta_estagio_view, name="criar_proposta_estagio"),
    path("proposta-estagio/listar/", views.listar_propostas_estagio_view, name="listar_propostas_estagio"),
    path("proposta-estagio/atualizar/<str:titulo>/", views.atualizar_proposta_estagio_view, name="atualizar_proposta_estagio"),
    path("proposta-estagio/deletar/<str:titulo>/", views.deletar_proposta_estagio_view, name="deletar_proposta_estagio"),
    path("favoritos/", views.favoritos_view, name="favoritos"),
    path("api/favoritos/toggle/", views.toggle_favorito_view, name="toggle_favorito"),
    path("proposta/<int:id_proposta>/", views.proposta_detalhes, name="proposta_detalhes"),
    path("proposta/<int:id_proposta>/atribuir/", views.atribuir_aluno_view, name="atribuir_aluno"),
]

