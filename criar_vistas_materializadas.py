#!/usr/bin/env python
"""
Script para criar e atualizar vistas materializadas no PostgreSQL
Execute: python criar_vistas_materializadas.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd2_projeto.settings')
django.setup()

from django.db import connection, connections
from pathlib import Path


def atualizar_vistas():
    """Atualiza todas as vistas materializadas"""
    print("\nA atualizar vistas materializadas...")
    
    vistas = [
        'mv_estatisticas_turno',
        'mv_resumo_inscricoes_aluno',
        'mv_ucs_mais_procuradas',
        'mv_carga_docentes',
        'mv_inscricoes_por_dia',
        'mv_conflitos_horario'
    ]
    
    with connections["admin"].cursor() as cursor:
        for vista in vistas:
            try:
                print(f"Atualizando {vista}...")
                cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {vista}")
                print(f"{vista} atualizada")
            except Exception as e:
                print(f"Erro ao atualizar {vista}: {str(e)}")
    
    print("Todas as vistas foram atualizadas!")


def verificar_vistas():
    """Verifica se as vistas materializadas existem"""
    print("\nA verificar vistas materializadas...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'public'
            ORDER BY matviewname;
        """)
        
        vistas = cursor.fetchall()
        
        if vistas:
            print(f"\n{len(vistas)} vistas materializadas encontradas:")
            for i, (nome,) in enumerate(vistas, 1):
                print(f"  {i}. {nome}")
        else:
            print("Nenhuma vista materializada encontrada!")
        
        return len(vistas) > 0


def mostrar_estatisticas():
    """Mostra algumas estatísticas das vistas"""
    print("\nEstatísticas das Vistas:")
    
    try:
        with connections["admin"].cursor() as cursor:
            # Estatísticas de turnos
            cursor.execute("SELECT COUNT(*) FROM mv_estatisticas_turno")
            total_turnos = cursor.fetchone()[0]
            print(f"  - Turnos com estatísticas: {total_turnos}")
            
            # UCs procuradas
            cursor.execute("SELECT COUNT(*) FROM mv_ucs_mais_procuradas")
            total_ucs = cursor.fetchone()[0]
            print(f"  - UCs com dados: {total_ucs}")
            
            # Alunos
            cursor.execute("SELECT COUNT(*) FROM mv_resumo_inscricoes_aluno")
            total_alunos = cursor.fetchone()[0]
            print(f"  - Alunos com resumo: {total_alunos}")
            
            # Docentes
            cursor.execute("SELECT COUNT(*) FROM mv_carga_docentes")
            total_docentes = cursor.fetchone()[0]
            print(f"  - Docentes com carga: {total_docentes}")
            
            # Dias com inscrições
            cursor.execute("SELECT COUNT(*) FROM mv_inscricoes_por_dia")
            total_dias = cursor.fetchone()[0]
            print(f"  - Dias com inscrições: {total_dias}")
            
            # Conflitos
            cursor.execute("SELECT COUNT(DISTINCT n_mecanografico) FROM mv_conflitos_horario")
            alunos_conflito = cursor.fetchone()[0]
            print(f"  - Alunos com conflitos: {alunos_conflito}")
            
    except Exception as e:
        print(f"Erro ao obter estatísticas: {str(e)}")

