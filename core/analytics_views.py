"""
Views para análise de dados com MongoDB aggregations
Dashboards com insights sobre inscrições, consultas, comportamento de alunos
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from bd2_projeto.services.mongo_service import (
    analisar_taxa_sucesso_inscricoes,
    analisar_inscricoes_por_dia,
    analisar_alunos_mais_ativos,
    analisar_ucs_mais_procuradas,
    analisar_turnos_sobrecarregados
)
from core.utils import admin_required

@admin_required
def analytics_inscricoes(request):
    """Dashboard com análise de inscrições em turnos"""
    
    # Taxa de sucesso por tipo de resultado
    taxa_sucesso = analisar_taxa_sucesso_inscricoes()
    
    # Inscrições por dia (tendência temporal)
    inscricoes_dia = analisar_inscricoes_por_dia()
    
    # Alunos mais ativos
    alunos_ativos = analisar_alunos_mais_ativos()
    # Renomear _id para id (Django templates não permitem underscore)
    alunos_ativos = [
        {**aluno, 'id': aluno.get('_id')} 
        for aluno in alunos_ativos
    ]
    
    # UCs mais procuradas
    ucs_procuradas = analisar_ucs_mais_procuradas()
    # Renomear _id para id
    ucs_procuradas = [
        {
            **uc, 
            'id': uc.get('_id', {}).get('uc_id'),
            'uc_nome': uc.get('_id', {}).get('uc_nome')
        } 
        for uc in ucs_procuradas
    ]
    
    # Turnos sobrecarregados
    turnos_cheios = analisar_turnos_sobrecarregados()
    # Renomear _id para id
    turnos_cheios = [
        {**turno, 'id': turno.get('_id')} 
        for turno in turnos_cheios
    ]
    
    contexto = {
        "taxa_sucesso": taxa_sucesso,
        "inscricoes_dia": inscricoes_dia,
        "alunos_ativos": alunos_ativos,
        "ucs_procuradas": ucs_procuradas,
        "turnos_cheios": turnos_cheios,
    }
    
    return render(request, "admin/analytics_inscricoes.html", contexto)

@admin_required
def analytics_api_inscricoes_dia(request):
    """API para gráfico de inscrições por dia"""
    dados = analisar_inscricoes_por_dia()
    return JsonResponse(dados, safe=False)

@admin_required
def analytics_api_taxa_sucesso(request):
    """API para gráfico de taxa de sucesso"""
    dados = analisar_taxa_sucesso_inscricoes()
    return JsonResponse(dados, safe=False)

@admin_required
def analytics_api_alunos_ativos(request):
    """API para gráfico de alunos mais ativos"""
    dados = analisar_alunos_mais_ativos()
    return JsonResponse(dados, safe=False)

@admin_required
def analytics_api_ucs_procuradas(request):
    """API para gráfico de UCs mais procuradas"""
    dados = analisar_ucs_mais_procuradas()
    return JsonResponse(dados, safe=False)
