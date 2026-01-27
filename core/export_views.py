import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from core.utils import admin_required

# ---------------------------------------------------------------------------
# Helpers para acesso direto à BD (sem ORM)
# ---------------------------------------------------------------------------

def _fetch(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return cols, rows


def _fetch_dicts(sql, params=None):
    cols, rows = _fetch(sql, params)
    return [dict(zip(cols, row)) for row in rows]


def criar_xml_formatado(root):
    """Formata XML de forma legível"""
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')

def refresh_materialized_view(view_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW {view_name}")
    except Exception as exc:
        print(f"Aviso: não foi possível atualizar vista {view_name}: {exc}")


def refresh_all_materialized_views():
    views = [
        "mv_estatisticas_turno",
        "mv_resumo_inscricoes_aluno",
        "mv_ucs_mais_procuradas",
    ]
    for view in views:
        refresh_materialized_view(view)


@admin_required
def exportar_alunos_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_alunos()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow(["N. Mecanografico", "Nome", "Email", "Curso", "Ano Curricular"])
    for n_mec, nome, email, curso, ano in rows:
        writer.writerow([n_mec, nome, email, curso or "", ano or ""])
    return response


@admin_required
def exportar_alunos_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_alunos()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
def exportar_turnos_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_turnos()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow(["ID Turno", "N. Turno", "Tipo", "Capacidade", "UC", "Hora Inicio", "Hora Fim"])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4] or "",
            row[5] or "",
            row[6] or "",
        ])
    return response


@admin_required
def exportar_turnos_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_turnos()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
def exportar_inscricoes_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_inscricoes()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=inscricoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow([
        "ID Inscricao",
        "Data",
        "N. Mecanografico",
        "Aluno",
        "UC",
        "Turno",
        "Tipo Turno",
    ])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3] or "",
            row[4] or "",
            row[5] or "",
            row[6] or "",
        ])
    return response


@admin_required
def exportar_inscricoes_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_inscricoes()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=inscricoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
def exportar_ucs_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_ucs()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow(["ID UC", "Nome", "ECTS", "Curso", "Ano Curricular", "Semestre"])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3] or "",
            row[4] or "",
            row[5] or "",
        ])
    return response


@admin_required
def exportar_ucs_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_ucs()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


# ---------------------------------------------------------------------------
# Exportações XML
# ---------------------------------------------------------------------------

@admin_required
def exportar_alunos_xml(request):
    _, rows = _fetch("SELECT * FROM fn_export_alunos()")

    root = ET.Element("alunos")
    root.set("exportado_em", datetime.now().isoformat())
    for n_mec, nome, email, curso, ano in rows:
        aluno_elem = ET.SubElement(root, "aluno")
        ET.SubElement(aluno_elem, "n_mecanografico").text = str(n_mec)
        ET.SubElement(aluno_elem, "nome").text = nome
        ET.SubElement(aluno_elem, "email").text = email or ""
        ET.SubElement(aluno_elem, "curso").text = curso or ""
        ET.SubElement(aluno_elem, "ano_curricular").text = str(ano or "")

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_turnos_xml(request):
    _, rows = _fetch("SELECT * FROM fn_export_turnos()")

    root = ET.Element("turnos")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        turno_elem = ET.SubElement(root, "turno")
        ET.SubElement(turno_elem, "id_turno").text = str(row[0])
        ET.SubElement(turno_elem, "n_turno").text = str(row[1])
        ET.SubElement(turno_elem, "tipo").text = row[2] or ""
        ET.SubElement(turno_elem, "capacidade").text = str(row[3])
        ET.SubElement(turno_elem, "uc").text = row[4] or ""
        ET.SubElement(turno_elem, "hora_inicio").text = str(row[5] or "")
        ET.SubElement(turno_elem, "hora_fim").text = str(row[6] or "")

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_inscricoes_xml(request):
    _, rows = _fetch("SELECT * FROM fn_export_inscricoes()")

    root = ET.Element("inscricoes")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        inscricao_elem = ET.SubElement(root, "inscricao")
        ET.SubElement(inscricao_elem, "id_inscricao").text = str(row[0])
        ET.SubElement(inscricao_elem, "data_inscricao").text = str(row[1])
        ET.SubElement(inscricao_elem, "n_mecanografico").text = str(row[2])
        ET.SubElement(inscricao_elem, "aluno_nome").text = row[3] or ""
        ET.SubElement(inscricao_elem, "uc_nome").text = row[4] or ""
        ET.SubElement(inscricao_elem, "turno_numero").text = str(row[5] or "")
        ET.SubElement(inscricao_elem, "turno_tipo").text = row[6] or ""

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=inscricoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_ucs_xml(request):
    _, rows = _fetch("SELECT * FROM fn_export_ucs()")

    root = ET.Element("unidades_curriculares")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        uc_elem = ET.SubElement(root, "unidade_curricular")
        ET.SubElement(uc_elem, "id_unidadecurricular").text = str(row[0])
        ET.SubElement(uc_elem, "nome").text = row[1]
        ET.SubElement(uc_elem, "ects").text = str(row[2])
        ET.SubElement(uc_elem, "curso").text = row[3] or ""
        ET.SubElement(uc_elem, "ano_curricular").text = str(row[4] or "")
        ET.SubElement(uc_elem, "semestre").text = str(row[5] or "")

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


# ---------------------------------------------------------------------------
# Exportações de vistas materializadas
# ---------------------------------------------------------------------------

@admin_required
def exportar_mv_estatisticas_xml(request):
    _, rows = _fetch("SELECT id_turno, n_turno, tipo, capacidade, uc_nome, total_inscritos, vagas_disponiveis, taxa_ocupacao_percent FROM fn_export_mv_estatisticas_turno()")

    root = ET.Element("estatisticas_turnos")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        stat_elem = ET.SubElement(root, "estatistica")
        ET.SubElement(stat_elem, "id_turno").text = str(row[0])
        ET.SubElement(stat_elem, "n_turno").text = str(row[1])
        ET.SubElement(stat_elem, "tipo").text = row[2] or ""
        ET.SubElement(stat_elem, "uc_nome").text = row[4] or ""
        ET.SubElement(stat_elem, "capacidade").text = str(row[3])
        ET.SubElement(stat_elem, "total_inscritos").text = str(row[5] or 0)
        ET.SubElement(stat_elem, "vagas_disponiveis").text = str(row[6] or 0)
        ET.SubElement(stat_elem, "taxa_ocupacao_percent").text = str(row[7] or 0)

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=estatisticas_turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_mv_ucs_preenchidas_xml(request):
    _, rows = _fetch("SELECT id_unidadecurricular, uc_nome, curso_nome, ano_curricular, total_inscricoes, total_alunos_inscritos, taxa_preenchimento_global_percent FROM fn_export_mv_ucs_procuradas()")

    root = ET.Element("ucs_mais_procuradas")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        uc_elem = ET.SubElement(root, "uc")
        ET.SubElement(uc_elem, "id_unidadecurricular").text = str(row[0])
        ET.SubElement(uc_elem, "uc_nome").text = row[1] or ""
        ET.SubElement(uc_elem, "curso_nome").text = row[2] or ""
        ET.SubElement(uc_elem, "ano_curricular").text = str(row[3] or "")
        ET.SubElement(uc_elem, "total_inscricoes").text = str(row[4] or 0)
        ET.SubElement(uc_elem, "total_alunos_inscritos").text = str(row[5] or 0)
        ET.SubElement(uc_elem, "taxa_preenchimento_global_percent").text = str(row[6] or 0)

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_procuradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_mv_resumo_alunos_xml(request):
    _, rows = _fetch("SELECT * FROM fn_export_mv_resumo_alunos()")

    root = ET.Element("resumo_alunos")
    root.set("exportado_em", datetime.now().isoformat())
    for row in rows:
        aluno_elem = ET.SubElement(root, "aluno")
        ET.SubElement(aluno_elem, "n_mecanografico").text = str(row[0])
        ET.SubElement(aluno_elem, "aluno_nome").text = row[1] or ""
        ET.SubElement(aluno_elem, "aluno_email").text = row[2] or ""
        ET.SubElement(aluno_elem, "curso_nome").text = row[3] or ""
        ET.SubElement(aluno_elem, "ano_curricular").text = str(row[4] or "")
        ET.SubElement(aluno_elem, "total_ucs_inscritas").text = str(row[5] or 0)
        ET.SubElement(aluno_elem, "total_turnos_inscritos").text = str(row[6] or 0)
        ET.SubElement(aluno_elem, "total_ects").text = str(row[7] or 0)
        ET.SubElement(aluno_elem, "primeira_inscricao").text = str(row[8] or "")
        ET.SubElement(aluno_elem, "ultima_inscricao").text = str(row[9] or "")
        ET.SubElement(aluno_elem, "dias_com_atividade").text = str(row[10] or 0)

    xml_content = criar_xml_formatado(root)
    response = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=resumo_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    )
    return response


@admin_required
def exportar_mv_estatisticas_turno_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_mv_estatisticas_turno()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=estatisticas_turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow([
        "ID Turno",
        "N. Turno",
        "Tipo",
        "Capacidade",
        "UC",
        "Curso",
        "Ano",
        "Total Inscritos",
        "Vagas Disponiveis",
        "Taxa Ocupacao %",
        "Turno Cheio",
        "Hora Inicio",
        "Hora Fim",
    ])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            float(row[9]) if row[9] is not None else 0,
            "Sim" if row[10] else "Nao",
            row[11],
            row[12],
        ])
    return response


@admin_required
def exportar_mv_estatisticas_turno_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_mv_estatisticas_turno()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=estatisticas_turnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
def exportar_mv_ucs_preenchidas_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_mv_ucs_procuradas()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_procuradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow([
        "ID UC",
        "UC",
        "ECTS",
        "Curso",
        "Ano",
        "Semestre",
        "Total Alunos",
        "Total Turnos",
        "Total Inscricoes",
        "Capacidade Total",
        "Taxa Preenchimento %",
    ])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            float(row[10]) if row[10] is not None else 0,
        ])
    return response


@admin_required
def exportar_mv_ucs_preenchidas_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_mv_ucs_procuradas()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=ucs_procuradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
def exportar_mv_resumo_alunos_csv(request):
    _, rows = _fetch("SELECT * FROM fn_export_mv_resumo_alunos()")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=resumo_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    writer = csv.writer(response)
    writer.writerow([
        "N. Mecanografico",
        "Nome",
        "Email",
        "Curso",
        "Ano",
        "UCs Inscritas",
        "Turnos",
        "ECTS Total",
        "Primeira Inscricao",
        "Ultima Inscricao",
        "Dias Ativo",
    ])
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
        ])
    return response


@admin_required
def exportar_mv_resumo_alunos_json(request):
    data = _fetch_dicts("SELECT * FROM fn_export_mv_resumo_alunos()")
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=resumo_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@admin_required
@require_http_methods(["POST"])
def atualizar_vistas_materializadas(request):
    try:
        refresh_all_materialized_views()
        return JsonResponse(
            {"status": "success", "message": "Vistas materializadas atualizadas"}
        )
    except Exception as exc:
        print(f"Erro ao atualizar vistas: {exc}")
        return JsonResponse(
            {"status": "error", "message": f"Erro ao atualizar vistas: {exc}"},
            status=500,
        )
