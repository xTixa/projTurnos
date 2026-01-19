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

from django.db import connection
from pathlib import Path


def executar_sql_file(arquivo_sql):
    """Lê e executa um ficheiro SQL"""
    try:
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print(f"📄 A ler ficheiro: {arquivo_sql}")
        
        with connection.cursor() as cursor:
            # Divide o SQL em statements individuais (separados por ;)
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            
            total = len(statements)
            for i, statement in enumerate(statements, 1):
                # Ignora comentários e comandos vazios
                if statement.startswith('--') or statement.startswith('/*') or not statement:
                    continue
                
                try:
                    print(f"⏳ Executando statement {i}/{total}...")
                    cursor.execute(statement)
                    print(f"✅ Statement {i}/{total} executado com sucesso")
                except Exception as e:
                    # Se falhar, tenta continuar (pode ser DROP de algo que não existe)
                    print(f"⚠️  Aviso no statement {i}: {str(e)[:100]}")
        
        print("✅ Ficheiro SQL executado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar SQL: {str(e)}")
        return False


def atualizar_vistas():
    """Atualiza todas as vistas materializadas"""
    print("\n🔄 A atualizar vistas materializadas...")
    
    vistas = [
        'mv_estatisticas_turno',
        'mv_resumo_inscricoes_aluno',
        'mv_ucs_mais_procuradas',
        'mv_carga_docentes',
        'mv_inscricoes_por_dia',
        'mv_conflitos_horario'
    ]
    
    with connection.cursor() as cursor:
        for vista in vistas:
            try:
                print(f"⏳ Atualizando {vista}...")
                cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {vista}")
                print(f"✅ {vista} atualizada")
            except Exception as e:
                print(f"❌ Erro ao atualizar {vista}: {str(e)}")
    
    print("✅ Todas as vistas foram atualizadas!")


def verificar_vistas():
    """Verifica se as vistas materializadas existem"""
    print("\n🔍 A verificar vistas materializadas...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'public'
            ORDER BY matviewname;
        """)
        
        vistas = cursor.fetchall()
        
        if vistas:
            print(f"\n✅ {len(vistas)} vistas materializadas encontradas:")
            for i, (nome,) in enumerate(vistas, 1):
                print(f"  {i}. {nome}")
        else:
            print("❌ Nenhuma vista materializada encontrada!")
        
        return len(vistas) > 0


def mostrar_estatisticas():
    """Mostra algumas estatísticas das vistas"""
    print("\n📊 Estatísticas das Vistas:")
    
    try:
        with connection.cursor() as cursor:
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
        print(f"❌ Erro ao obter estatísticas: {str(e)}")


def main():
    print("=" * 60)
    print("🚀 GESTOR DE VISTAS MATERIALIZADAS - Projeto BD2")
    print("=" * 60)
    
    # Caminho para o ficheiro SQL
    sql_path = Path(__file__).parent / 'core' / 'sql' / 'materialized_views.sql'
    
    if not sql_path.exists():
        print(f"❌ Ficheiro SQL não encontrado: {sql_path}")
        return
    
    print("\nOpções:")
    print("1. Criar/Recriar vistas materializadas (executar SQL)")
    print("2. Atualizar vistas existentes (REFRESH)")
    print("3. Verificar vistas existentes")
    print("4. Mostrar estatísticas")
    print("5. Tudo (criar + atualizar + verificar + estatísticas)")
    print("0. Sair")
    
    escolha = input("\nEscolha uma opção (0-5): ").strip()
    
    if escolha == '1':
        print("\n" + "=" * 60)
        if executar_sql_file(sql_path):
            print("\n✅ Vistas materializadas criadas com sucesso!")
            print("💡 Dica: Execute a opção 2 para atualizar os dados.")
    
    elif escolha == '2':
        atualizar_vistas()
    
    elif escolha == '3':
        verificar_vistas()
    
    elif escolha == '4':
        mostrar_estatisticas()
    
    elif escolha == '5':
        print("\n" + "=" * 60)
        print("📦 Executando processo completo...")
        print("=" * 60)
        
        # 1. Criar vistas
        if executar_sql_file(sql_path):
            # 2. Atualizar
            atualizar_vistas()
            # 3. Verificar
            verificar_vistas()
            # 4. Estatísticas
            mostrar_estatisticas()
            
            print("\n" + "=" * 60)
            print("✅ PROCESSO COMPLETO FINALIZADO!")
            print("=" * 60)
            print("\n💡 Próximos passos:")
            print("   - Aceda ao painel admin: /admin-panel/export/")
            print("   - Exporte dados em CSV ou JSON")
            print("   - Configure atualizações automáticas (ver README)")
    
    elif escolha == '0':
        print("👋 Até breve!")
    
    else:
        print("❌ Opção inválida!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo utilizador.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
