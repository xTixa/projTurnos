"""
Exemplos de uso das Vistas Materializadas
Copie e cole estes exemplos no Django Shell ou nas suas views
"""

from core.models import (
    MvEstatisticasTurno, MvResumoInscricoesAluno, MvUcsMaisProcuradas,
    MvCargaDocentes, MvInscricoesPorDia, MvConflitosHorario
)
from core.export_views import refresh_all_materialized_views
from django.db.models import Q, Avg, Sum, Count


# ==========================================
# EXEMPLO 1: Análise de Ocupação de Turnos
# ==========================================

def exemplo_ocupacao_turnos():
    """Analisa a ocupação dos turnos"""
    print("📊 ANÁLISE DE OCUPAÇÃO DE TURNOS\n")
    
    # Atualizar vistas primeiro
    refresh_all_materialized_views()
    
    # Turnos cheios
    turnos_cheios = MvEstatisticasTurno.objects.filter(turno_cheio=True)
    print(f"🔴 Turnos CHEIOS: {turnos_cheios.count()}")
    for t in turnos_cheios[:5]:
        print(f"  - {t.uc_nome} (Turno {t.n_turno}): {t.total_inscritos}/{t.capacidade}")
    
    # Turnos com baixa ocupação (< 50%)
    turnos_vazios = MvEstatisticasTurno.objects.filter(taxa_ocupacao_percent__lt=50)
    print(f"\n🟢 Turnos com BAIXA OCUPAÇÃO (< 50%): {turnos_vazios.count()}")
    for t in turnos_vazios[:5]:
        print(f"  - {t.uc_nome} (Turno {t.n_turno}): {t.total_inscritos}/{t.capacidade} ({t.taxa_ocupacao_percent}%)")
    
    # Taxa média de ocupação
    taxa_media = MvEstatisticasTurno.objects.aggregate(
        taxa_media=Avg('taxa_ocupacao_percent')
    )['taxa_media']
    print(f"\n📈 Taxa MÉDIA de ocupação: {taxa_media:.2f}%")
    
    # Total de vagas disponíveis
    total_vagas = MvEstatisticasTurno.objects.aggregate(
        total=Sum('vagas_disponiveis')
    )['total']
    print(f"🎯 Total de vagas DISPONÍVEIS: {total_vagas}")


# ==========================================
# EXEMPLO 2: Ranking de UCs
# ==========================================

def exemplo_ranking_ucs():
    """Mostra as UCs mais e menos procuradas"""
    print("\n📚 RANKING DE UNIDADES CURRICULARES\n")
    
    # Top 10 UCs mais procuradas
    top_ucs = MvUcsMaisProcuradas.objects.order_by('-total_alunos_inscritos')[:10]
    print("🏆 TOP 10 UCs MAIS PROCURADAS:")
    for i, uc in enumerate(top_ucs, 1):
        print(f"  {i}. {uc.uc_nome}")
        print(f"     - Alunos: {uc.total_alunos_inscritos}")
        print(f"     - Taxa preenchimento: {uc.taxa_preenchimento_global_percent}%")
        print(f"     - ECTS: {uc.ects}")
    
    # UCs menos procuradas (com pelo menos 1 inscrição)
    bottom_ucs = MvUcsMaisProcuradas.objects.filter(
        total_alunos_inscritos__gt=0
    ).order_by('total_alunos_inscritos')[:5]
    print("\n⚠️  5 UCs MENOS PROCURADAS:")
    for i, uc in enumerate(bottom_ucs, 1):
        print(f"  {i}. {uc.uc_nome}: {uc.total_alunos_inscritos} alunos")


# ==========================================
# EXEMPLO 3: Análise de Alunos
# ==========================================

def exemplo_analise_alunos():
    """Analisa o comportamento dos alunos"""
    print("\n👨‍🎓 ANÁLISE DE ALUNOS\n")
    
    # Alunos mais ativos
    alunos_ativos = MvResumoInscricoesAluno.objects.order_by('-total_ucs_inscritas')[:5]
    print("⭐ 5 ALUNOS MAIS ATIVOS:")
    for a in alunos_ativos:
        print(f"  - {a.aluno_nome}")
        print(f"    UCs: {a.total_ucs_inscritas} | ECTS: {a.total_ects} | Dias ativos: {a.dias_com_atividade}")
    
    # Alunos sem inscrições
    alunos_inativos = MvResumoInscricoesAluno.objects.filter(
        total_ucs_inscritas=0
    )
    print(f"\n⚠️  ALUNOS SEM INSCRIÇÕES: {alunos_inativos.count()}")
    
    # Média de ECTS por aluno
    media_ects = MvResumoInscricoesAluno.objects.aggregate(
        media=Avg('total_ects')
    )['media']
    print(f"\n📊 Média de ECTS por aluno: {media_ects:.2f}")
    
    # Distribuição por curso
    distribuicao = MvResumoInscricoesAluno.objects.values('curso_nome').annotate(
        total=Count('n_mecanografico')
    ).order_by('-total')
    print("\n📚 DISTRIBUIÇÃO POR CURSO:")
    for d in distribuicao:
        print(f"  - {d['curso_nome']}: {d['total']} alunos")


# ==========================================
# EXEMPLO 4: Carga Horária dos Docentes
# ==========================================

def exemplo_carga_docentes():
    """Analisa a carga horária dos docentes"""
    print("\n👨‍🏫 ANÁLISE DE CARGA DOCENTE\n")
    
    # Docentes com mais UCs
    top_docentes = MvCargaDocentes.objects.order_by('-total_ucs')[:5]
    print("🏆 DOCENTES COM MAIS UCs:")
    for d in top_docentes:
        print(f"  - {d.docente_nome}")
        print(f"    UCs: {d.total_ucs} | ECTS: {d.total_ects_lecionados} | Alunos: {d.total_alunos_distintos}")
    
    # Média de UCs por docente
    media_ucs = MvCargaDocentes.objects.aggregate(
        media=Avg('total_ucs')
    )['media']
    print(f"\n📊 Média de UCs por docente: {media_ucs:.2f}")
    
    # Total de ECTS lecionados
    total_ects = MvCargaDocentes.objects.aggregate(
        total=Sum('total_ects_lecionados')
    )['total']
    print(f"📚 Total de ECTS lecionados: {total_ects}")


# ==========================================
# EXEMPLO 5: Análise Temporal de Inscrições
# ==========================================

def exemplo_analise_temporal():
    """Analisa padrões temporais de inscrições"""
    print("\n📅 ANÁLISE TEMPORAL DE INSCRIÇÕES\n")
    
    # Dia com mais inscrições
    dia_pico = MvInscricoesPorDia.objects.order_by('-total_inscricoes').first()
    if dia_pico:
        print(f"🔥 DIA COM MAIS INSCRIÇÕES:")
        print(f"  Data: {dia_pico.data}")
        print(f"  Total: {dia_pico.total_inscricoes} inscrições")
        print(f"  Alunos distintos: {dia_pico.alunos_distintos}")
        print(f"  Dia da semana: {dia_pico.nome_dia_semana}")
    
    # Média de inscrições por dia
    media_dia = MvInscricoesPorDia.objects.aggregate(
        media=Avg('total_inscricoes')
    )['media']
    print(f"\n📊 Média de inscrições por dia: {media_dia:.2f}")
    
    # Distribuição por dia da semana
    por_dia_semana = MvInscricoesPorDia.objects.values('nome_dia_semana').annotate(
        total=Sum('total_inscricoes')
    ).order_by('-total')
    print("\n📅 INSCRIÇÕES POR DIA DA SEMANA:")
    for d in por_dia_semana:
        print(f"  - {d['nome_dia_semana'].strip()}: {d['total']} inscrições")


# ==========================================
# EXEMPLO 6: Detecção de Conflitos
# ==========================================

def exemplo_conflitos():
    """Identifica conflitos de horário"""
    print("\n⚠️  ANÁLISE DE CONFLITOS DE HORÁRIO\n")
    
    # Total de alunos com conflitos
    alunos_conflito = MvConflitosHorario.objects.values('n_mecanografico').distinct().count()
    print(f"🚨 ALUNOS COM CONFLITOS: {alunos_conflito}")
    
    # Listar alguns conflitos
    conflitos = MvConflitosHorario.objects.select_related()[:5]
    print("\n📋 EXEMPLOS DE CONFLITOS:")
    for c in conflitos:
        print(f"\n  Aluno: {c.aluno_nome} (Nº {c.n_mecanografico})")
        print(f"  Conflito entre:")
        print(f"    - {c.uc1_nome}: {c.turno1_inicio} - {c.turno1_fim}")
        print(f"    - {c.uc2_nome}: {c.turno2_inicio} - {c.turno2_fim}")
    
    # UCs mais envolvidas em conflitos
    ucs_conflito = {}
    for c in MvConflitosHorario.objects.all():
        ucs_conflito[c.uc1_nome] = ucs_conflito.get(c.uc1_nome, 0) + 1
        ucs_conflito[c.uc2_nome] = ucs_conflito.get(c.uc2_nome, 0) + 1
    
    if ucs_conflito:
        print("\n📊 UCs MAIS ENVOLVIDAS EM CONFLITOS:")
        top_ucs_conflito = sorted(ucs_conflito.items(), key=lambda x: x[1], reverse=True)[:5]
        for uc, total in top_ucs_conflito:
            print(f"  - {uc}: {total} conflitos")


# ==========================================
# EXEMPLO 7: Dashboard Completo
# ==========================================

def dashboard_completo():
    """Gera um dashboard completo com todas as estatísticas"""
    print("=" * 70)
    print("📊 DASHBOARD COMPLETO - SISTEMA DE TURNOS")
    print("=" * 70)
    
    # Atualizar vistas
    print("\n🔄 Atualizando vistas materializadas...")
    refresh_all_materialized_views()
    print("✅ Vistas atualizadas!\n")
    
    # Executar todas as análises
    exemplo_ocupacao_turnos()
    exemplo_ranking_ucs()
    exemplo_analise_alunos()
    exemplo_carga_docentes()
    exemplo_analise_temporal()
    exemplo_conflitos()
    
    print("\n" + "=" * 70)
    print("✅ DASHBOARD COMPLETO GERADO COM SUCESSO!")
    print("=" * 70)


# ==========================================
# EXEMPLO 8: Exportação Programática
# ==========================================

def exportar_relatorio_completo():
    """Exemplo de como gerar um relatório completo em JSON"""
    import json
    from datetime import datetime
    
    relatorio = {
        'data_geracao': datetime.now().isoformat(),
        'ocupacao': {
            'turnos_cheios': MvEstatisticasTurno.objects.filter(turno_cheio=True).count(),
            'taxa_media': float(MvEstatisticasTurno.objects.aggregate(
                taxa=Avg('taxa_ocupacao_percent')
            )['taxa'] or 0)
        },
        'ucs': {
            'total': MvUcsMaisProcuradas.objects.count(),
            'top_3': list(MvUcsMaisProcuradas.objects.order_by('-total_alunos_inscritos')[:3].values(
                'uc_nome', 'total_alunos_inscritos', 'taxa_preenchimento_global_percent'
            ))
        },
        'alunos': {
            'total': MvResumoInscricoesAluno.objects.count(),
            'media_ects': float(MvResumoInscricoesAluno.objects.aggregate(
                media=Avg('total_ects')
            )['media'] or 0)
        },
        'conflitos': {
            'alunos_afetados': MvConflitosHorario.objects.values('n_mecanografico').distinct().count()
        }
    }
    
    # Salvar em ficheiro
    with open('relatorio_turnos.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Relatório exportado para: relatorio_turnos.json")
    return relatorio


# ==========================================
# COMO USAR
# ==========================================

if __name__ == '__main__':
    print("""
    Para usar estes exemplos, execute no Django Shell:
    
    python manage.py shell
    
    Depois importe e execute:
    
    from core.exemplos_vistas import *
    
    # Dashboard completo
    dashboard_completo()
    
    # Ou funções individuais
    exemplo_ocupacao_turnos()
    exemplo_ranking_ucs()
    exemplo_analise_alunos()
    exemplo_carga_docentes()
    exemplo_analise_temporal()
    exemplo_conflitos()
    
    # Exportar relatório
    exportar_relatorio_completo()
    """)
