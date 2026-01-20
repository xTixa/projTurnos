import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import connection
from core.models import (
    Aluno, Turno, InscricaoTurno, UnidadeCurricular, Docente,
    MvEstatisticasTurno, MvResumoInscricoesAluno, MvUcsMaisProcuradas,
    MvCargaDocentes, MvInscricoesPorDia, MvConflitosHorario
)
from core.utils import admin_required

def criar_xml_formatado(root):
    """Formata XML de forma legível"""
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')

def refresh_materialized_view(view_name):
    """Atualiza uma vista materializada"""
    with connection.cursor() as cursor:
        cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name}")

def refresh_all_materialized_views():
    """Atualiza todas as vistas materializadas"""
    views = [
        'mv_estatisticas_turno',
        'mv_resumo_inscricoes_aluno',
        'mv_ucs_mais_procuradas',
        'mv_carga_docentes',
        'mv_inscricoes_por_dia',
        'mv_conflitos_horario'
    ]
    for view in views:
        refresh_materialized_view(view)

@admin_required
def exportar_alunos_csv(request):
    """Exporta lista de alunos para CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['N. Mecanográfico', 'Nome', 'Email', 'Curso', 'Ano Curricular'])
    
    alunos = Aluno.objects.select_related('id_curso', 'id_anocurricular').all()
    for aluno in alunos:
        writer.writerow([
            aluno.n_mecanografico,
            aluno.nome,
            aluno.email,
            aluno.id_curso.nome if aluno.id_curso else '',
            aluno.id_anocurricular.ano_curricular if aluno.id_anocurricular else ''
        ])
    
    return response


@admin_required
def exportar_alunos_json(request):
    """Exporta lista de alunos para JSON"""
    alunos = Aluno.objects.select_related('id_curso', 'id_anocurricular').all()
    
    data = []
    for aluno in alunos:
        data.append({
            'n_mecanografico': aluno.n_mecanografico,
            'nome': aluno.nome,
            'email': aluno.email,
            'curso': aluno.id_curso.nome if aluno.id_curso else None,
            'ano_curricular': aluno.id_anocurricular.ano_curricular if aluno.id_anocurricular else None
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
def exportar_turnos_csv(request):
    """Exporta lista de turnos para CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID Turno', 'N. Turno', 'Tipo', 'Capacidade', 'UC', 'Hora Início', 'Hora Fim'])
    
    turnos = Turno.objects.all()
    for turno in turnos:
        try:
            turno_uc = turno.turnouc
            uc_nome = turno_uc.id_unidadecurricular.nome if turno_uc else ''
            hora_inicio = turno_uc.hora_inicio if turno_uc else ''
            hora_fim = turno_uc.hora_fim if turno_uc else ''
        except:
            uc_nome = ''
            hora_inicio = ''
            hora_fim = ''
            
        writer.writerow([
            turno.id_turno,
            turno.n_turno,
            turno.tipo,
            turno.capacidade,
            uc_nome,
            hora_inicio,
            hora_fim
        ])
    
    return response

@admin_required
def exportar_turnos_json(request):
    """Exporta lista de turnos para JSON"""
    turnos = Turno.objects.all()
    
    data = []
    for turno in turnos:
        try:
            turno_uc = turno.turnouc
            uc_nome = turno_uc.id_unidadecurricular.nome if turno_uc else None
            hora_inicio = str(turno_uc.hora_inicio) if turno_uc else None
            hora_fim = str(turno_uc.hora_fim) if turno_uc else None
        except:
            uc_nome = None
            hora_inicio = None
            hora_fim = None
            
        data.append({
            'id_turno': turno.id_turno,
            'n_turno': turno.n_turno,
            'tipo': turno.tipo,
            'capacidade': turno.capacidade,
            'uc': uc_nome,
            'hora_inicio': hora_inicio,
            'hora_fim': hora_fim
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
def exportar_inscricoes_csv(request):
    """Exporta lista de inscrições para CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="inscricoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID Inscrição', 'Data', 'N. Mecanográfico', 'Aluno', 'UC', 'Turno', 'Tipo Turno'])
    
    inscricoes = InscricaoTurno.objects.select_related(
        'n_mecanografico', 'id_turno', 'id_unidadecurricular'
    ).all()
    
    for inscricao in inscricoes:
        writer.writerow([
            inscricao.id_inscricao,
            inscricao.data_inscricao,
            inscricao.n_mecanografico.n_mecanografico if inscricao.n_mecanografico else '',
            inscricao.n_mecanografico.nome if inscricao.n_mecanografico else '',
            inscricao.id_unidadecurricular.nome if inscricao.id_unidadecurricular else '',
            inscricao.id_turno.n_turno if inscricao.id_turno else '',
            inscricao.id_turno.tipo if inscricao.id_turno else ''
        ])
    
    return response

@admin_required
def exportar_inscricoes_json(request):
    """Exporta lista de inscrições para JSON"""
    inscricoes = InscricaoTurno.objects.select_related(
        'n_mecanografico', 'id_turno', 'id_unidadecurricular'
    ).all()
    
    data = []
    for inscricao in inscricoes:
        data.append({
            'id_inscricao': inscricao.id_inscricao,
            'data_inscricao': str(inscricao.data_inscricao),
            'n_mecanografico': inscricao.n_mecanografico.n_mecanografico if inscricao.n_mecanografico else None,
            'aluno_nome': inscricao.n_mecanografico.nome if inscricao.n_mecanografico else None,
            'uc_nome': inscricao.id_unidadecurricular.nome if inscricao.id_unidadecurricular else None,
            'turno_numero': inscricao.id_turno.n_turno if inscricao.id_turno else None,
            'turno_tipo': inscricao.id_turno.tipo if inscricao.id_turno else None
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="inscricoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
def exportar_ucs_csv(request):
    """Exporta lista de UCs para CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ucs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID UC', 'Nome', 'ECTS', 'Curso', 'Ano Curricular', 'Semestre'])
    
    ucs = UnidadeCurricular.objects.select_related(
        'id_curso', 'id_anocurricular', 'id_semestre'
    ).all()
    
    for uc in ucs:
        writer.writerow([
            uc.id_unidadecurricular,
            uc.nome,
            uc.ects,
            uc.id_curso.nome if uc.id_curso else '',
            uc.id_anocurricular.ano_curricular if uc.id_anocurricular else '',
            uc.id_semestre.semestre if uc.id_semestre else ''
        ])
    
    return response

@admin_required
def exportar_ucs_json(request):
    """Exporta lista de UCs para JSON"""
    ucs = UnidadeCurricular.objects.select_related(
        'id_curso', 'id_anocurricular', 'id_semestre'
    ).all()
    
    data = []
    for uc in ucs:
        data.append({
            'id_unidadecurricular': uc.id_unidadecurricular,
            'nome': uc.nome,
            'ects': uc.ects,
            'curso': uc.id_curso.nome if uc.id_curso else None,
            'ano_curricular': uc.id_anocurricular.ano_curricular if uc.id_anocurricular else None,
            'semestre': uc.id_semestre.semestre if uc.id_semestre else None
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="ucs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

# ==========================================
# VIEWS DE EXPORTAÇÃO XML
# ==========================================

@admin_required
def exportar_alunos_xml(request):
    """Exporta lista de alunos para XML"""
    root = ET.Element('alunos')
    root.set('exportado_em', datetime.now().isoformat())
    
    alunos = Aluno.objects.select_related('id_curso', 'id_anocurricular').all()
    for aluno in alunos:
        aluno_elem = ET.SubElement(root, 'aluno')
        ET.SubElement(aluno_elem, 'n_mecanografico').text = str(aluno.n_mecanografico)
        ET.SubElement(aluno_elem, 'nome').text = aluno.nome
        ET.SubElement(aluno_elem, 'email').text = aluno.email or ''
        ET.SubElement(aluno_elem, 'curso').text = aluno.id_curso.nome if aluno.id_curso else ''
        ET.SubElement(aluno_elem, 'ano_curricular').text = str(aluno.id_anocurricular.ano_curricular) if aluno.id_anocurricular else ''
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_turnos_xml(request):
    """Exporta lista de turnos para XML"""
    root = ET.Element('turnos')
    root.set('exportado_em', datetime.now().isoformat())
    
    turnos = Turno.objects.all()
    for turno in turnos:
        try:
            turno_uc = turno.turnouc
            uc_nome = turno_uc.id_unidadecurricular.nome if turno_uc else ''
            hora_inicio = str(turno_uc.hora_inicio) if turno_uc else ''
            hora_fim = str(turno_uc.hora_fim) if turno_uc else ''
        except:
            uc_nome = ''
            hora_inicio = ''
            hora_fim = ''
        
        turno_elem = ET.SubElement(root, 'turno')
        ET.SubElement(turno_elem, 'id_turno').text = str(turno.id_turno)
        ET.SubElement(turno_elem, 'n_turno').text = str(turno.n_turno)
        ET.SubElement(turno_elem, 'tipo').text = turno.tipo or ''
        ET.SubElement(turno_elem, 'capacidade').text = str(turno.capacidade)
        ET.SubElement(turno_elem, 'uc').text = uc_nome
        ET.SubElement(turno_elem, 'hora_inicio').text = hora_inicio
        ET.SubElement(turno_elem, 'hora_fim').text = hora_fim
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_inscricoes_xml(request):
    """Exporta lista de inscrições para XML"""
    root = ET.Element('inscricoes')
    root.set('exportado_em', datetime.now().isoformat())
    
    inscricoes = InscricaoTurno.objects.select_related(
        'n_mecanografico', 'id_turno', 'id_unidadecurricular'
    ).all()
    
    for inscricao in inscricoes:
        inscricao_elem = ET.SubElement(root, 'inscricao')
        ET.SubElement(inscricao_elem, 'id_inscricao').text = str(inscricao.id_inscricao)
        ET.SubElement(inscricao_elem, 'data_inscricao').text = str(inscricao.data_inscricao)
        ET.SubElement(inscricao_elem, 'n_mecanografico').text = str(inscricao.n_mecanografico.n_mecanografico) if inscricao.n_mecanografico else ''
        ET.SubElement(inscricao_elem, 'aluno_nome').text = inscricao.n_mecanografico.nome if inscricao.n_mecanografico else ''
        ET.SubElement(inscricao_elem, 'uc_nome').text = inscricao.id_unidadecurricular.nome if inscricao.id_unidadecurricular else ''
        ET.SubElement(inscricao_elem, 'turno_numero').text = str(inscricao.id_turno.n_turno) if inscricao.id_turno else ''
        ET.SubElement(inscricao_elem, 'turno_tipo').text = inscricao.id_turno.tipo if inscricao.id_turno else ''
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="inscricoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_ucs_xml(request):
    """Exporta lista de UCs para XML"""
    root = ET.Element('unidades_curriculares')
    root.set('exportado_em', datetime.now().isoformat())
    
    ucs = UnidadeCurricular.objects.select_related(
        'id_curso', 'id_anocurricular', 'id_semestre'
    ).all()
    
    for uc in ucs:
        uc_elem = ET.SubElement(root, 'unidade_curricular')
        ET.SubElement(uc_elem, 'id_unidadecurricular').text = str(uc.id_unidadecurricular)
        ET.SubElement(uc_elem, 'nome').text = uc.nome
        ET.SubElement(uc_elem, 'ects').text = str(uc.ects)
        ET.SubElement(uc_elem, 'curso').text = uc.id_curso.nome if uc.id_curso else ''
        ET.SubElement(uc_elem, 'ano_curricular').text = str(uc.id_anocurricular.ano_curricular) if uc.id_anocurricular else ''
        ET.SubElement(uc_elem, 'semestre').text = str(uc.id_semestre.semestre) if uc.id_semestre else ''
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ucs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_mv_estatisticas_xml(request):
    """Exporta estatísticas de turnos (vista materializada) para XML"""
    refresh_materialized_view('mv_estatisticas_turno')
    
    root = ET.Element('estatisticas_turnos')
    root.set('exportado_em', datetime.now().isoformat())
    
    estatisticas = MvEstatisticasTurno.objects.all()
    
    for stat in estatisticas:
        stat_elem = ET.SubElement(root, 'estatistica')
        ET.SubElement(stat_elem, 'id_turno').text = str(stat.id_turno)
        ET.SubElement(stat_elem, 'n_turno').text = str(stat.n_turno)
        ET.SubElement(stat_elem, 'tipo_turno').text = stat.tipo_turno or ''
        ET.SubElement(stat_elem, 'uc_nome').text = stat.uc_nome or ''
        ET.SubElement(stat_elem, 'capacidade').text = str(stat.capacidade)
        ET.SubElement(stat_elem, 'total_inscritos').text = str(stat.total_inscritos or 0)
        ET.SubElement(stat_elem, 'vagas_disponiveis').text = str(stat.vagas_disponiveis or 0)
        ET.SubElement(stat_elem, 'taxa_ocupacao').text = str(stat.taxa_ocupacao or 0)
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="estatisticas_turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_mv_ucs_procuradas_xml(request):
    """Exporta UCs mais procuradas (vista materializada) para XML"""
    refresh_materialized_view('mv_ucs_mais_procuradas')
    
    root = ET.Element('ucs_mais_procuradas')
    root.set('exportado_em', datetime.now().isoformat())
    
    ucs = MvUcsMaisProcuradas.objects.all()
    
    for uc in ucs:
        uc_elem = ET.SubElement(root, 'uc')
        ET.SubElement(uc_elem, 'id_unidadecurricular').text = str(uc.id_unidadecurricular)
        ET.SubElement(uc_elem, 'uc_nome').text = uc.uc_nome or ''
        ET.SubElement(uc_elem, 'curso_nome').text = uc.curso_nome or ''
        ET.SubElement(uc_elem, 'ano_curricular').text = str(uc.ano_curricular or '')
        ET.SubElement(uc_elem, 'total_inscricoes').text = str(uc.total_inscricoes or 0)
        ET.SubElement(uc_elem, 'alunos_unicos').text = str(uc.alunos_unicos or 0)
        ET.SubElement(uc_elem, 'media_inscricoes_aluno').text = str(uc.media_inscricoes_aluno or 0)
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ucs_procuradas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_mv_resumo_alunos_xml(request):
    """Exporta resumo de inscrições por aluno (vista materializada) para XML"""
    refresh_materialized_view('mv_resumo_inscricoes_aluno')
    
    root = ET.Element('resumo_alunos')
    root.set('exportado_em', datetime.now().isoformat())
    
    alunos = MvResumoInscricoesAluno.objects.all()
    
    for aluno in alunos:
        aluno_elem = ET.SubElement(root, 'aluno')
        ET.SubElement(aluno_elem, 'n_mecanografico').text = str(aluno.n_mecanografico)
        ET.SubElement(aluno_elem, 'aluno_nome').text = aluno.aluno_nome or ''
        ET.SubElement(aluno_elem, 'aluno_email').text = aluno.aluno_email or ''
        ET.SubElement(aluno_elem, 'curso_nome').text = aluno.curso_nome or ''
        ET.SubElement(aluno_elem, 'ano_curricular').text = str(aluno.ano_curricular or '')
        ET.SubElement(aluno_elem, 'total_ucs_inscritas').text = str(aluno.total_ucs_inscritas or 0)
        ET.SubElement(aluno_elem, 'total_turnos_inscritos').text = str(aluno.total_turnos_inscritos or 0)
        ET.SubElement(aluno_elem, 'total_ects').text = str(aluno.total_ects or 0)
        ET.SubElement(aluno_elem, 'primeira_inscricao').text = str(aluno.primeira_inscricao) if aluno.primeira_inscricao else ''
        ET.SubElement(aluno_elem, 'ultima_inscricao').text = str(aluno.ultima_inscricao) if aluno.ultima_inscricao else ''
        ET.SubElement(aluno_elem, 'dias_com_atividade').text = str(aluno.dias_com_atividade or 0)
    
    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="resumo_alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"'
    return response

@admin_required
def exportar_mv_estatisticas_turno_csv(request):
    """Exporta estatísticas de turnos (vista materializada) para CSV"""
    refresh_materialized_view('mv_estatisticas_turno')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="estatisticas_turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID Turno', 'N. Turno', 'Tipo', 'Capacidade', 'UC', 'Curso', 
        'Ano', 'Total Inscritos', 'Vagas Disponíveis', 'Taxa Ocupação %', 
        'Turno Cheio', 'Hora Início', 'Hora Fim'
    ])
    
    stats = MvEstatisticasTurno.objects.all()
    for stat in stats:
        writer.writerow([
            stat.id_turno,
            stat.n_turno,
            stat.tipo,
            stat.capacidade,
            stat.uc_nome,
            stat.curso_nome,
            stat.ano_curricular,
            stat.total_inscritos,
            stat.vagas_disponiveis,
            stat.taxa_ocupacao_percent,
            'Sim' if stat.turno_cheio else 'Não',
            stat.hora_inicio,
            stat.hora_fim
        ])
    
    return response

@admin_required
def exportar_mv_estatisticas_turno_json(request):
    """Exporta estatísticas de turnos (vista materializada) para JSON"""
    refresh_materialized_view('mv_estatisticas_turno')
    
    stats = MvEstatisticasTurno.objects.all()
    
    data = []
    for stat in stats:
        data.append({
            'id_turno': stat.id_turno,
            'n_turno': stat.n_turno,
            'tipo': stat.tipo,
            'capacidade': stat.capacidade,
            'uc_nome': stat.uc_nome,
            'curso_nome': stat.curso_nome,
            'ano_curricular': stat.ano_curricular,
            'total_inscritos': stat.total_inscritos,
            'vagas_disponiveis': stat.vagas_disponiveis,
            'taxa_ocupacao_percent': float(stat.taxa_ocupacao_percent),
            'turno_cheio': stat.turno_cheio,
            'hora_inicio': str(stat.hora_inicio),
            'hora_fim': str(stat.hora_fim)
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="estatisticas_turnos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
def exportar_mv_ucs_procuradas_csv(request):
    """Exporta UCs mais procuradas (vista materializada) para CSV"""
    refresh_materialized_view('mv_ucs_mais_procuradas')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ucs_procuradas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID UC', 'UC', 'ECTS', 'Curso', 'Ano', 'Semestre',
        'Total Alunos', 'Total Turnos', 'Total Inscrições', 
        'Capacidade Total', 'Taxa Preenchimento %'
    ])
    
    ucs = MvUcsMaisProcuradas.objects.all()
    for uc in ucs:
        writer.writerow([
            uc.id_unidadecurricular,
            uc.uc_nome,
            uc.ects,
            uc.curso_nome,
            uc.ano_curricular,
            uc.semestre,
            uc.total_alunos_inscritos,
            uc.total_turnos_com_inscricoes,
            uc.total_inscricoes,
            uc.capacidade_total_turnos,
            uc.taxa_preenchimento_global_percent
        ])
    
    return response

@admin_required
def exportar_mv_ucs_procuradas_json(request):
    """Exporta UCs mais procuradas (vista materializada) para JSON"""
    refresh_materialized_view('mv_ucs_mais_procuradas')
    
    ucs = MvUcsMaisProcuradas.objects.all()
    
    data = []
    for uc in ucs:
        data.append({
            'id_unidadecurricular': uc.id_unidadecurricular,
            'uc_nome': uc.uc_nome,
            'ects': uc.ects,
            'curso_nome': uc.curso_nome,
            'ano_curricular': uc.ano_curricular,
            'semestre': uc.semestre,
            'total_alunos_inscritos': uc.total_alunos_inscritos,
            'total_turnos_com_inscricoes': uc.total_turnos_com_inscricoes,
            'total_inscricoes': uc.total_inscricoes,
            'capacidade_total_turnos': uc.capacidade_total_turnos,
            'taxa_preenchimento_global_percent': float(uc.taxa_preenchimento_global_percent) if uc.taxa_preenchimento_global_percent else 0
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="ucs_procuradas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
def exportar_mv_resumo_alunos_csv(request):
    """Exporta resumo de inscrições por aluno (vista materializada) para CSV"""
    refresh_materialized_view('mv_resumo_inscricoes_aluno')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="resumo_alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'N. Mecanográfico', 'Nome', 'Email', 'Curso', 'Ano',
        'UCs Inscritas', 'Turnos', 'ECTS Total', 
        'Primeira Inscrição', 'Última Inscrição', 'Dias Ativo'
    ])
    
    alunos = MvResumoInscricoesAluno.objects.all()
    for aluno in alunos:
        writer.writerow([
            aluno.n_mecanografico,
            aluno.aluno_nome,
            aluno.aluno_email,
            aluno.curso_nome,
            aluno.ano_curricular,
            aluno.total_ucs_inscritas,
            aluno.total_turnos_inscritos,
            aluno.total_ects,
            aluno.primeira_inscricao,
            aluno.ultima_inscricao,
            aluno.dias_com_atividade
        ])
    
    return response

@admin_required
def exportar_mv_resumo_alunos_json(request):
    """Exporta resumo de inscrições por aluno (vista materializada) para JSON"""
    refresh_materialized_view('mv_resumo_inscricoes_aluno')
    
    alunos = MvResumoInscricoesAluno.objects.all()
    
    data = []
    for aluno in alunos:
        data.append({
            'n_mecanografico': aluno.n_mecanografico,
            'aluno_nome': aluno.aluno_nome,
            'aluno_email': aluno.aluno_email,
            'curso_nome': aluno.curso_nome,
            'ano_curricular': aluno.ano_curricular,
            'total_ucs_inscritas': aluno.total_ucs_inscritas,
            'total_turnos_inscritos': aluno.total_turnos_inscritos,
            'total_ects': aluno.total_ects,
            'primeira_inscricao': str(aluno.primeira_inscricao) if aluno.primeira_inscricao else None,
            'ultima_inscricao': str(aluno.ultima_inscricao) if aluno.ultima_inscricao else None,
            'dias_com_atividade': aluno.dias_com_atividade
        })
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="resumo_alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@admin_required
@require_http_methods(["POST"])
def atualizar_vistas_materializadas(request):
    """Endpoint para atualizar todas as vistas materializadas"""
    try:
        refresh_all_materialized_views()
        return JsonResponse({
            'status': 'success',
            'message': 'Todas as vistas materializadas foram atualizadas com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao atualizar vistas: {str(e)}'
        }, status=500)
